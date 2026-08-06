# Systematic skill -> device interaction resolver.
# Methodology (proven from code):
#  1. required_skill_id gating: buff entries scoped to a skill only match devices whose item skill_id == that skill
#     (GetBuffIndex/GetBuffedProperty match rule: stored skillId>0 only matches same-skill queries).
#  2. required_category gating: reactive skills (ProcessReactiveSkillBasedEffectGroup) trigger while an effect
#     group of that category is active -> devices that produce that category.
#  3. effect_group_type: 261 passive-equip, 264 on-hit, 505 hit-situational (conditional), 759 successful-hit, 1104 reactive.
#  4. Unscoped passives resolve by prop semantics (214 ranged dmg -> ranged devices, 350 pet -> pet devices, etc).
import sqlite3, json, os
# Generated data lands in out/ next to the scripts (the repo-wide "out/" ignore covers it);
# only skilldev.json is committed and stays beside the script.
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out') + os.sep
os.makedirs(OUT, exist_ok=True)
db = sqlite3.connect(r"E:\GA_LOCAL\gaa.db"); db.row_factory = sqlite3.Row
def q(s, a=()): return db.execute(s, a).fetchall()
# The game calls it Cooldown wherever the player sees it; the property table says Recharge
# Time. Renamed at the point names are produced, so it is consistent across the whole console.
PROPRENAME = {4: 'Cooldown', 203: 'Cooldown Modifier'}
def pn(pid):
    if pid in PROPRENAME: return PROPRENAME[pid]
    r = q("SELECT name FROM asm_data_set_properties WHERE prop_id=?", (pid,))
    return (r[0]['name'] if r and r[0]['name'] else str(pid))
def sname(sid):
    r = q("SELECT name_msg_translated nm FROM asm_data_set_skill_group_skills WHERE skill_id=? AND name_msg_translated<>'' LIMIT 1", (sid,))
    return r[0]['nm'] if r else ("skill%s" % sid)
CALC = {67: '+', 68: '+%', 69: '-%', 70: '-'}
TREE = {155: 'Balanced', 156: 'Healer', 157: 'Poison', 158: 'Tank', 159: 'Destroyer',
        160: 'Infiltration', 161: 'Marksman', 162: 'Engineer', 163: 'Drones'}
TREECLS = {155: 'All', 156: 'Medic', 157: 'Medic', 158: 'Assault', 159: 'Assault',
           160: 'Recon', 161: 'Recon', 162: 'Robotics', 163: 'Robotics'}
PROF = {680: 'Assault', 567: 'Medic', 681: 'Recon', 679: 'Robotics'}

# ---------- 1. inventory devices + classification ----------
inv = q("SELECT DISTINCT device_id, profile_id, allowed_slots FROM ga_players_inventory WHERE user_id=2381 AND device_id>0")
radius_props = [r['prop_id'] for r in q("SELECT prop_id FROM asm_data_set_properties WHERE name LIKE '%Effect Radius%' OR name='Radius'")]
devices = {}
for r in inv:
    did = r['device_id']
    if did in devices:
        continue
    it = q("SELECT i.skill_id sk, m.message nm FROM asm_data_set_items i JOIN asm_data_set_msg_translations m ON m.msg_id=i.name_msg_id WHERE i.item_id=? LIMIT 1", (did,))
    name = it[0]['nm'] if it else ("dev%s" % did)
    dskill = it[0]['sk'] if it else 0
    # Only the Crescent jetpack is equippable; the other jetpack variants sit in the inventory
    # table but not in the live pool (same rule as gen2.py's device model).
    if r['allowed_slots'] == '201' and 'Crescent' not in name:
        continue
    modes = q("SELECT device_mode_id mid, attack_type_value_id atk, damage_type_value_id dmg, deployable_id dep, bot_id bot, device_projectile_id proj FROM asm_data_set_devices_data_set_device_modes WHERE device_id=?", (did,))
    atk = set(); pet = False; proj = False
    for m in modes:
        if m['atk']: atk.add(m['atk'])
        if (m['dep'] or 0) > 0 or (m['bot'] or 0) > 0: pet = True
        if (m['proj'] or 0) > 0: proj = True
    # A bomb carries no radius of its own - the thing it THROWS does. Venom Bomb has no
    # radius prop at all; its payload device (via device_projectile_id -> projectiles ->
    # spawn_deployable_id) has Effect Radius 20. Classifying on the carrier alone made every
    # Recon explosive read as non-AOE, so the AOE damage passive skipped all eight of them.
    # A station placed directly (mode deployable_id, no projectile) is likewise its own
    # payload: the aura lives on the deployable's device (Medical Station's cat-1324 heal is
    # on dev 2064). bot_id stays excluded - a turret is a separate combatant.
    payload = []
    for _m in q("SELECT device_projectile_id proj FROM asm_data_set_devices_data_set_device_modes WHERE device_id=? AND device_projectile_id>0", (did,)):
        for _p in q("SELECT spawn_item_id si, spawn_deployable_id sd, spawn_bot_id sb FROM asm_data_set_projectiles WHERE device_projectile_id=? LIMIT 1", (_m['proj'],)):
            if _p['sb']:
                pet = True     # a projectile-spawned bot (Spider Grenades' spiders) is a pet,
                continue       # not this device's payload - its damage takes Pet Damage (350)
            if _p['sd']:
                for _r in q("SELECT device_id dv FROM asm_data_set_deployables WHERE deployable_id=? LIMIT 1", (_p['sd'],)):
                    if _r['dv']: payload.append(_r['dv'])
            if _p['si']: payload.append(_p['si'])
    for _m in q("SELECT deployable_id dep FROM asm_data_set_devices_data_set_device_modes WHERE device_id=? AND deployable_id>0", (did,)):
        for _r in q("SELECT device_id dv FROM asm_data_set_deployables WHERE deployable_id=? LIMIT 1", (_m['dep'],)):
            if _r['dv']: payload.append(_r['dv'])
    hasradius = False
    if radius_props:
        ph = ",".join(str(p) for p in radius_props)
        for _d in [did] + payload:
            if q("SELECT 1 FROM asm_data_set_device_mode_properties WHERE device_id=? AND prop_id IN (%s) AND base_value>0 LIMIT 1" % ph, (_d,)):
                hasradius = True; break
    # Classify MELEE FIRST: melee has a cone Effect Radius, which must NOT re-tag it as AOE.
    # Mirrors the server rule in TgDeviceFire__GetEffectGroup.cpp (attack 170/372 = melee, else
    # radius => AOE, else 85/177 = ranged).
    is_melee_dev = bool(atk & {170, 372})
    if is_melee_dev:
        hasradius = False
    # Attack classes of the modes that actually HURT someone, carrier and payload alike -
    # classified per MODE with the same rule the device model uses (gen2 hit_of): melee never
    # promotes, a ranged mode with a prop-6 blast radius is AOE, else it stays ranged. Raw
    # attack type alone must not decide - every AOE weapon also carries atk 85/177 (that is
    # how it AIMS, not what it hits), which put MagmaLance under ranged damage. And a harmless
    # spawn must not promote: the snipers' YA_AOE_AmmoCrate resupply has a 40 radius, which
    # made the Ballista read as an AOE weapon.
    dmgcls = set()
    for _d in [did] + payload:
        for _m in q("SELECT device_mode_id mid, attack_type_value_id a FROM asm_data_set_devices_data_set_device_modes WHERE device_id=?", (_d,)):
            base = {85: 2, 177: 2, 170: 1, 372: 1}.get(_m['a'])
            if not base:
                continue
            r6 = q("SELECT base_value bv FROM asm_data_set_device_mode_properties WHERE device_id=? AND device_mode_id=? AND prop_id=6", (_d, _m['mid']))
            mcls = 3 if (base == 2 and r6 and r6[0]['bv'] > 0) else base
            # "hurts" = deals actual damage (negative Health/Power, props 51/211) - the only
            # props the bench's damage bucket (212/214/321) ever modifies. A protection debuff
            # or a taunt takes Effect Potency (376) instead, so it must not put a device on a
            # damage-skill list the skill cannot act on.
            harm = False
            for _eg in q("SELECT DISTINCT effect_group_id eg FROM asm_data_set_device_mode_effect_groups WHERE device_id=? AND device_mode_id=?", (_d, _m['mid'])):
                for _e in q("SELECT prop_id p, calc_method_value_id c FROM asm_data_set_effects WHERE effect_group_id=?", (_eg['eg'],)):
                    if _e['c'] in (69, 70) and _e['p'] in (51, 211):
                        harm = True
            if harm:
                dmgcls.add(mcls)
    cats = set(); heals = False; dmg = False; debuff = False; timedfx = False
    # The payload's effect groups are this device's effects: a Venom Bomb deals no damage
    # itself, the mine it throws does. Scanning only the carrier left every Recon explosive
    # flagged as dealing no damage, applying no debuff and having no timed effect - so the AOE
    # damage passive (which needs aoe AND dmg) skipped them even once they read as AOE.
    _egq = ("SELECT DISTINCT dme.effect_group_id eg FROM asm_data_set_device_mode_effect_groups dme "
            "WHERE dme.device_id IN (%s)" % ",".join("?" * (1 + len(payload))))
    for eg in q(_egq, tuple([did] + payload)):
        meta = q("SELECT category_value_id cat, lifetime_sec l, required_skill_id rsk FROM asm_data_set_effect_groups WHERE effect_group_id=? LIMIT 1", (eg['eg'],))
        if meta:
            if meta[0]['cat']: cats.add(meta[0]['cat'])
            if (meta[0]['l'] or 0) > 0: timedfx = True
        for e in q("SELECT prop_id p, base_value bv, calc_method_value_id c FROM asm_data_set_effects WHERE effect_group_id=?", (eg['eg'],)):
            pos = e['c'] in (67, 68)
            if e['p'] in (51, 211):
                if pos: heals = True
                else: dmg = True
            if e['p'] in (155, 156, 157, 217, 218, 219, 324, 316) and not pos: debuff = True
    devices[did] = {'name': name, 'skill': dskill, 'class': PROF.get(r['profile_id'], 'Shared'),
                    'atk': sorted(atk), 'pet': pet, 'aoe': 3 in dmgcls, 'proj': proj,
                    'dmgcls': dmgcls, 'rad': hasradius,
                    'cats': sorted(cats), 'heals': heals, 'dmg': dmg, 'debuff': debuff, 'timedfx': timedfx,
                    # prop 4 Recharge Time: what "off-hand recharge" actually keys on. Weapons
                    # use refire (53) instead, so having a cooldown is what separates the two.
                    'cooldown': bool(q("SELECT 1 FROM asm_data_set_device_mode_properties WHERE device_id=? AND prop_id=4 AND base_value>0 LIMIT 1", (did,))),
                    # Power Pool Cost and Power Pool Cost - Block are DIFFERENT properties and
                    # take different modifiers - the resolver maps each to itself. Lumping them
                    # put Spare Power on the Impact Hammer, whose swing is free and whose only
                    # power draw is blocking.
                    'power': bool(q("SELECT 1 FROM asm_data_set_device_mode_properties WHERE device_id=? AND prop_id=242 AND base_value<>0 LIMIT 1", (did,))),
                    'blockpower': bool(q("SELECT 1 FROM asm_data_set_device_mode_properties WHERE device_id=? AND prop_id=322 AND base_value<>0 LIMIT 1", (did,)))}

# skill -> devices index
by_skill = {}
for did, d in devices.items():
    by_skill.setdefault(d['skill'], []).append(did)
# category -> devices index
by_cat = {}
for did, d in devices.items():
    for c in d['cats']:
        by_cat.setdefault(c, []).append(did)

print("=== device skill_id coverage ===")
for sk, dl in sorted(by_skill.items()):
    print("  skill %s (%s): %s" % (sk, sname(sk), ", ".join(devices[d]['name'] for d in dl[:14])))

# ---------- 2. tree skills + effect groups ----------
skills = {}
for r in q("""SELECT DISTINCT sgs.skill_group_id grp, sgs.skill_id sid, sgs.name_msg_translated nm
              FROM asm_data_set_skill_group_skills sgs
              WHERE sgs.skill_group_id BETWEEN 155 AND 163 AND sgs.name_msg_translated<>''"""):
    egs = {}
    for s in q("SELECT DISTINCT effect_group_id eg, effect_group_type_value_id t FROM asm_data_set_skill_effect_groups WHERE skill_group_id=? AND skill_id=?", (r['grp'], r['sid'])):
        meta = q("SELECT required_skill_id rsk, required_category_value_id rcat, situational_type_value_id sit, situational_value sv, lifetime_sec l, category_value_id cat, application_value_id app, application_value appv FROM asm_data_set_effect_groups WHERE effect_group_id=? LIMIT 1", (s['eg'],))
        m = meta[0] if meta else None
        effs = [(e['p'], round(e['bv'], 2), e['c'], e['pv'] or 0) for e in q("SELECT prop_id p, base_value bv, calc_method_value_id c, property_value_id pv FROM asm_data_set_effects WHERE effect_group_id=?", (s['eg'],))]
        egs[s['eg']] = {'type': s['t'], 'rsk': m['rsk'] if m else 0, 'rcat': m['rcat'] if m else 0,
                        'sit': m['sit'] if m else 0, 'sv': m['sv'] if m else 0, 'life': m['l'] if m else 0,
                        # a skill rider contends for a stacking bucket exactly like a device's
                        # own effect - Killer Instinct's shred sits in 986 with the Ballista's
                        'cat': m['cat'] if m else 0, 'app': m['app'] if m else 0,
                        'appv': m['appv'] if m else 0, 'fx': effs}
    if egs:
        skills[(r['grp'], r['sid'])] = {'name': r['nm'], 'tree': TREE[r['grp']], 'cls': TREECLS[r['grp']], 'egs': egs}

print("\n=== tree skills with effect groups: %d ===" % len(skills))

# ---------- 3. resolve interactions ----------
TKIND = {261: 'PASSIVE', 264: 'ON-HIT', 505: 'CONDITIONAL', 759: 'ON-HIT', 1104: 'REACTIVE'}

# Ungated effects resolve by prop semantics: which devices does this property mean anything on?
# The damage props key on dmgcls - the attack classes of the modes that actually hurt someone -
# so an AOE weapon is not "ranged" just because it aims like one, and a sniper rifle is not
# "AOE" because of a harmless spawn.
SEMPRED = {
    212: lambda v: 1 in v['dmgcls'],       # melee dmg
    214: lambda v: 2 in v['dmgcls'],       # ranged dmg
    215: lambda v: 2 in v['dmgcls'],
    232: lambda v: 2 in v['dmgcls'],
    321: lambda v: 3 in v['dmgcls'],       # AOE dmg
    352: lambda v: 3 in v['dmgcls'],       # AOE radius
    350: lambda v: v['pet'], 381: lambda v: v['pet'], 382: lambda v: v['pet'],
    383: lambda v: v['pet'], 366: lambda v: v['pet'], 391: lambda v: v['pet'],
    330: lambda v: v['heals'],
    357: lambda v: v['skill'] in (365, 351, 363, 364),
    337: lambda v: v['skill'] in (365, 351, 363, 364),
    # These three modify a DEVICE, not the player, but had no rule - so the skills that
    # carry them resolved to nothing at all. Offhand Recharge is the clearest case: a
    # Balanced-tree skill reading "decreases the time it takes for off-hand devices to
    # recharge" that reached zero devices.
    203: lambda v: v['cooldown'], 4: lambda v: v['cooldown'],
    208: lambda v: v['timedfx'],
    # Spare Power's power-cost cut is the last of these: the resolver already applies
    # prop 242 to a device's power, so the skill affects devices and should say so.
    242: lambda v: v['power'], 322: lambda v: v['blockpower'],
}

# A gate names a weapon FAMILY, and a family is wider than the effect: Heal Durations is
# gated to the heal families but only a heal that HAS a duration can have it extended.
# These narrow a gated family to the devices the effect can act on at all.
ACTPRED = {
    208: lambda v: v['timedfx'],       # a lifetime modifier needs a timed effect
    352: lambda v: v['rad'],           # a radius modifier needs a radius (Force Wall has none;
                                       # a station's harmless aura still has one, so this is the
                                       # raw prop-6 check, not the damaging-AOE class)
    203: lambda v: v['cooldown'], 4: lambda v: v['cooldown'],
    242: lambda v: v['power'], 322: lambda v: v['blockpower'],
}

# Decisions the data cannot express, reviewed against the game 2026-08-05
# (docs/claude/theorycraft-console/skill-device-resolution.md):
EXCLUDE = {
    674: {'Pain Gun'},      # Bio Rifle Range tooltip: "excluding the Pain Gun"; the gate
                            # (Medic Guns 405) includes it and no field expresses the carve-out
    852: {'Triage Wave'},   # Group Heal Savior: measured on device-usage-metrics - a solo
                            # Triage rescue applies eg22375 and never eg16587, while Healing
                            # Wave and Healing Grenade both proc it
}
def fxsum(fx, maxn=3):
    out = []
    for f in fx[:maxn]:
        p, v, c = f[0], f[1], f[2]
        out.append("%s %s%s" % (pn(p), CALC.get(c, ''), v))
    return "; ".join(out)

ix = {}      # device_id -> list of interactions
skill_report = []  # for chat/doc
unresolved = []
for (grp, sid), S in sorted(skills.items()):
    for eg, G in S['egs'].items():
        kind = TKIND.get(G['type'], str(G['type']))
        detail = fxsum(G['fx'])
        gate = ''
        targets = []
        how = ''
        scope = ''
        if G['rsk']:
            how = 'gated to %s' % sname(G['rsk']); scope = 'skill'
            if not by_skill.get(G['rsk']):
                unresolved.append((S['name'], eg, G['rsk'], sname(G['rsk']), detail))
                continue
        elif G['rcat']:
            how = 'while a category-%s effect is active' % G['rcat']; scope = 'category'
            kind = 'REACTIVE'
            if not by_cat.get(G['rcat']):
                unresolved.append((S['name'], eg, 'cat%s' % G['rcat'], '', detail))
                continue
        else:
            how = 'applies to all matching devices'; scope = 'tree'
        # Resolve per EFFECT, not per group: each effect reaches the devices it can act on,
        # and the group's list is the union. Two narrowings apply on top of the base set:
        #  - ACTPRED: the effect's property must mean something on the device.
        #  - property_value_id: an effect carrying one is scoped to that effect CATEGORY and
        #    may not touch any other (damage-pipeline.md 15.2) - Heavy Impact's potency is
        #    pv875 Knockback, so of the Assault Guns it reaches only the guns that knock back.
        devset = set()
        for f in G['fx']:
            p, pv = f[0], f[3]
            if G['rsk']:
                base = set(by_skill.get(G['rsk'], []))
            elif G['rcat']:
                base = set(by_cat.get(G['rcat'], []))
            else:
                pred = SEMPRED.get(p)
                base = {d for d, v in devices.items() if pred(v)} if pred else set()
            if (G['rsk'] or G['rcat']) and p in ACTPRED:
                base = {d for d in base if ACTPRED[p](devices[d])}
            if pv:
                base = {d for d in base if pv in devices[d]['cats']}
            devset |= base
        if not devset:
            continue  # self/defensive stat, no device link
        targets = sorted(devset)
        if G['sit'] == 1271: gate = ' (target HP >%s%%)' % int(G['sv'])
        if G['sit'] == 1270: gate = ' (target HP <%s%%)' % int(G['sv'])
        for did in targets:
            # class compatibility: a class-tree skill can only affect that class's devices
            if S['cls'] != 'All' and devices[did]['class'] not in ('Shared', S['cls']):
                continue
            if devices[did]['name'] in EXCLUDE.get(sid, ()):
                continue
            ix.setdefault(did, []).append({'skill': S['name'], 'sid': sid, 'tree': S['tree'], 'kind': kind,
                                           'detail': detail + gate, 'how': how, 'scope': scope,
                                           # numeric backing so the bench can recompute, not just describe
                                           'fx': [list(f) for f in G['fx']],
                                           'egt': G['type'], 'life': G['life'] or 0,
                                           'sit': G['sit'] or 0, 'sv': G['sv'] or 0,
                                           'cat': G.get('cat') or 0, 'app': G.get('app') or 0,
                                           'appv': G.get('appv') or 0})
        skill_report.append((S['cls'], S['tree'], S['name'], kind, how, len(targets), detail + gate))

# Unmerged dump for the resolver: ONE entry per effect GROUP, so a skill that has both an
# always-on (261) group and a conditional (505) group keeps them distinct — merging would
# lose the always-on vs situational split the bench depends on.
json.dump({str(k): [dict(e) for e in v] for k, v in ix.items()}, open(OUT + 'ixraw.json', 'w'))
print("ixraw:", sum(len(v) for v in ix.values()), "effect groups")

# Merge per device: ONE entry per skill (a skill can have several effect groups — e.g. Assault
# Melee III has an ungated stat group AND a skill-gated Threat group; it must read as one skill).
KPRI = {'REACTIVE': 0, 'CONDITIONAL': 1, 'ON-HIT': 2, 'PASSIVE': 3}
for did in ix:
    merged = {}
    for e in ix[did]:
        m = merged.get(e['skill'])
        if not m:
            merged[e['skill']] = dict(e, details=[e['detail']], fx=list(e['fx']))
        else:
            if e['detail'] not in m['details']: m['details'].append(e['detail'])
            if KPRI.get(e['kind'], 9) < KPRI.get(m['kind'], 9): m['kind'] = e['kind']
            if e['scope'] == 'skill': m['how'] = e['how']
            for f in e['fx']:
                if f not in m['fx']: m['fx'].append(f)
    out = []
    for m in merged.values():
        m['detail'] = " · ".join(m['details']); m.pop('details')
        # Per-GROUP facts do not survive the per-skill merge: after fx from several groups are
        # unioned, the first group's egt/life/sit/cat would masquerade as applying to all of
        # them. ix.json is the display feed (gen3's interaction chips); anything numeric reads
        # ixraw.json, which keeps one entry per effect group.
        for k in ('fx', 'egt', 'life', 'sit', 'sv', 'cat', 'app', 'appv'):
            m.pop(k, None)
        out.append(m)
    ix[did] = sorted(out, key=lambda x: (KPRI.get(x['kind'], 9), x['tree'] != 'Balanced', x['skill']))

json.dump({str(k): v for k, v in ix.items()}, open(OUT + 'ix.json', 'w'), indent=0)

# device classification (attack type / pet / aoe / heals) - the bench needs this to pick the
# right ConvertPropToPropList modifier bucket for a given damage number.
json.dump({str(k): {'name': v['name'], 'cls': v['class'], 'skill': v['skill'], 'atk': v['atk'],
                    'pet': v['pet'], 'aoe': v['aoe'], 'heals': v['heals'], 'dmg': v['dmg']}
           for k, v in devices.items()}, open(OUT + 'devmeta.json', 'w'))
print('devmeta:', len(devices), 'devices')

# skill_id -> the devices it affects (for the character sheet)
skilldev = {}
for did, es in ix.items():
    for e in es:
        if not e.get('sid'): continue
        d = skilldev.setdefault(str(e['sid']), {'name': e['skill'], 'devices': [], 'scope': e['scope']})
        entry = [devices[did]['name'], devices[did]['class']]   # keep class so the sheet can filter
        if entry not in d['devices']: d['devices'].append(entry)
for d in skilldev.values(): d['devices'].sort()
# Written next to the script (and committed), not to the scratchpad: this file feeds both the
# console and the skill reference, and lived as an orphaned artifact once already.
json.dump(skilldev, open(os.path.join(HERE, 'skilldev.json'), 'w'))
print("skill->device map:", len(skilldev), "skills")

print("\n=== SKILL -> DEVICE INTERACTION MAP (by class/tree) ===")
cur = None
for cls, tree, name, kind, how, n, detail in sorted(skill_report):
    if (cls, tree) != cur:
        cur = (cls, tree); print("\n-- %s / %s --" % cur)
    print("  %-26s %-11s %-28s ->%3d devices | %s" % (name, kind, how, n, detail[:70]))

print("\n=== UNRESOLVED gates (no inventory device carries the required skill) ===")
for nm, eg, rsk, rn, detail in unresolved:
    print("  %-26s eg%-6s needs %s %s | %s" % (nm, eg, rsk, rn, detail[:60]))

print("\ndevices with interactions:", len(ix), "of", len(devices))
