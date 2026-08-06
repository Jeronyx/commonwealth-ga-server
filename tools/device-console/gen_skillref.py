# Builds a standalone skill reference: every skill, per tree, per class, with the in-game
# text alongside the effects the console models. Written for checking one against the other.
import io, json, html, os
from collections import OrderedDict
import benefit

# All generated data lives in out/ next to the scripts; running from any CWD works.
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')

T = json.load(io.open(os.path.join(OUT, 'tree.json'), encoding='utf-8'))
trees, names, classes, icons = T['trees'], T['names'], T['classes'], T['icons']

CSS = """<style>
:root{
  --bg:#eceff4; --panel:#fff; --panel2:#f4f6fa; --line:#d4dbe4;
  --ink:#131820; --mut:#57626f; --dim:#8993a1;
  --up:#186b43; --dn:#a92338; --cond:#8a5d05; --gate:#4c5866;
  --ally:#1c6f52; --foe:#a3363f;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#0d1014; --panel:#161b23; --panel2:#1b212b; --line:#252c37;
    --ink:#c9d2de; --mut:#8a94a3; --dim:#5d6673;
    --up:#7ee081; --dn:#ff5d6c; --cond:#ffce4d; --gate:#93a0b2;
    --ally:#57d9a8; --foe:#ff8b95;
  }
}
:root[data-theme="dark"]{
  --bg:#0d1014; --panel:#161b23; --panel2:#1b212b; --line:#252c37;
  --ink:#c9d2de; --mut:#8a94a3; --dim:#5d6673;
  --up:#7ee081; --dn:#ff5d6c; --cond:#ffce4d; --gate:#93a0b2;
  --ally:#57d9a8; --foe:#ff8b95;
}
:root[data-theme="light"]{
  --bg:#eceff4; --panel:#fff; --panel2:#f4f6fa; --line:#d4dbe4;
  --ink:#131820; --mut:#57626f; --dim:#8993a1;
  --up:#186b43; --dn:#a92338; --cond:#8a5d05; --gate:#4c5866;
  --ally:#1c6f52; --foe:#a3363f;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px}
h1,h2,h3{text-wrap:balance;margin:0}
code{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.9em}

.top{border-bottom:1px solid var(--line);background:var(--panel);padding:34px 0 0}
.eyebrow{margin:0 0 8px;font:600 10.5px/1 ui-monospace,Consolas,monospace;
  letter-spacing:.2em;text-transform:uppercase;color:var(--dim)}
.top h1{font:600 clamp(26px,4vw,40px)/1.05 ui-monospace,Consolas,monospace;letter-spacing:.02em}
.lede{max-width:62ch;color:var(--mut);margin:12px 0 22px;font-size:15.5px}
.nav{display:flex;gap:8px;flex-wrap:wrap}
.nav a{display:inline-block;padding:9px 15px 11px;border:1px solid var(--line);border-bottom:none;
  border-radius:8px 8px 0 0;text-decoration:none;color:var(--mut);background:var(--panel2);
  font:600 11.5px/1 ui-monospace,Consolas,monospace;letter-spacing:.14em;text-transform:uppercase;
  transition:color .14s,box-shadow .14s}
.nav a:hover{color:var(--ink);box-shadow:inset 0 -3px 0 var(--acc)}
.nav a:focus-visible{outline:2px solid var(--acc);outline-offset:2px}

.clsblock{margin:46px 0 0;scroll-margin-top:18px}
.clshead{border-left:3px solid var(--acc);padding:2px 0 2px 14px;margin-bottom:20px}
.clshead h2{font:600 21px/1.15 ui-monospace,Consolas,monospace;letter-spacing:.12em;
  text-transform:uppercase;color:var(--acc)}
.clshead p{margin:5px 0 0;color:var(--mut);font-size:13.5px}

.tree{margin:0 0 26px;border:1px solid var(--line);border-radius:12px;background:var(--panel);overflow:hidden}
.th{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;padding:13px 18px;
  background:var(--panel2);border-bottom:1px solid var(--line)}
.th h2{font:600 13px/1 ui-monospace,Consolas,monospace;letter-spacing:.16em;text-transform:uppercase}
.cnt,.shared{font:11px/1 ui-monospace,Consolas,monospace;color:var(--dim);letter-spacing:.05em}
.shared{margin-left:auto;border:1px solid var(--line);border-radius:100px;padding:4px 10px}

.rows{display:flex;flex-direction:column}
.tier{display:flex;align-items:center;gap:10px;padding:9px 18px;background:var(--panel2);
  border-top:1px solid var(--line)}
.tier:first-child{border-top:none}
.tier span{font:600 10px/1 ui-monospace,Consolas,monospace;letter-spacing:.15em;
  text-transform:uppercase;color:var(--acc)}
.tier::after{content:"";flex:1;height:1px;background:var(--line)}

.sk{display:grid;grid-template-columns:52px minmax(150px,190px) minmax(0,1fr) minmax(0,1fr);
  gap:16px;padding:15px 18px;border-top:1px solid var(--line);align-items:start}
.ic img{width:44px;height:44px;border-radius:8px;display:block;border:1px solid var(--line)}
.noic{color:var(--dim)}
.nm h3{font:600 14.5px/1.25 system-ui}
.pre{margin:4px 0 0;font:10.5px/1.35 ui-monospace,Consolas,monospace;color:var(--dim);letter-spacing:.03em}
.ds p{margin:0;color:var(--mut);font-size:13.5px;max-width:60ch}
.affbox{grid-column:1/-1;margin-top:2px;border:1px solid var(--line);border-radius:7px;background:var(--panel2);
  overflow:hidden}
.affbox summary{cursor:pointer;list-style:none;padding:6px 10px;
  font:10px/1.4 ui-monospace,Consolas,monospace;letter-spacing:.11em;text-transform:uppercase;
  color:var(--dim);display:flex;align-items:center;gap:6px}
.affbox summary::-webkit-details-marker{display:none}
.affbox summary::before{content:"▸";font-size:8px;color:var(--dim);transition:transform .15s}
.affbox[open] summary::before{transform:rotate(90deg)}
.affbox summary:hover{color:var(--ink)}
.affbox summary:focus-visible{outline:2px solid var(--acc);outline-offset:-2px}
.affbox summary b{color:var(--ink);font-weight:700}
.affgrid{display:grid;gap:0 14px;padding:2px 10px 10px;
  grid-template-columns:repeat(auto-fit,minmax(172px,1fr))}
.affgrid.one{grid-template-columns:1fr}
.affgrid.one .acls i{max-width:none}
.acls{min-width:0}
.acls i{font-style:normal;font-family:ui-monospace,Consolas,monospace;font-size:9px;
  letter-spacing:.12em;text-transform:uppercase;color:var(--gate);display:block;
  margin:6px 0 5px;padding-bottom:4px;border-bottom:1px solid var(--line)}
.acls i b{color:var(--ink);font-weight:700}
.acls ul{list-style:none;margin:0;padding:0}
.affgrid.one .acls ul{display:grid;gap:0 14px;
  grid-template-columns:repeat(auto-fill,minmax(172px,1fr))}
.acls li{font-size:11.5px;color:var(--mut);line-height:1.7;display:flex;align-items:center;
  gap:6px;min-width:0}
.acls li>span.di{flex:none}
.di{width:15px;height:15px;border-radius:3px;display:inline-block;
  background:transparent center/contain no-repeat}
.fx{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:5px}
.fx li{font-size:13px;line-height:1.45}
.fx b{font-family:ui-monospace,Consolas,monospace;font-variant-numeric:tabular-nums;font-weight:700}
.fx b.up{color:var(--up)} .fx b.dn{color:var(--dn)}
.pn{color:var(--ink);opacity:.86}
.none{color:var(--dim);font-style:italic;font-size:13px}
.k{font-style:normal;font-family:ui-monospace,Consolas,monospace;font-size:9.5px;letter-spacing:.07em;
  text-transform:uppercase;border:1px solid var(--line);border-radius:4px;padding:1px 5px;
  margin-left:4px;color:var(--gate);white-space:nowrap}
.k-conditional,.k-reactive,.k-on-hit{color:var(--cond);border-color:color-mix(in srgb,var(--cond) 45%,var(--line))}
.k-iv{color:var(--up);border-color:color-mix(in srgb,var(--up) 45%,var(--line))}
.k-allies{color:var(--ally);border-color:color-mix(in srgb,var(--ally) 45%,var(--line))}
.k-enemies{color:var(--foe);border-color:color-mix(in srgb,var(--foe) 45%,var(--line))}
.k-you{color:var(--dim)}
.fx b.unk{color:var(--cond)}
.fx b.ch{color:var(--gate)}
.k-choice{color:var(--gate);border-style:dashed}
.k-flag{background:var(--cond);border-color:var(--cond);color:var(--panel);font-weight:700}
.trig{margin:9px 0 0;font-size:12px;line-height:1.5;color:var(--mut);
  border-left:2px solid color-mix(in srgb,var(--cond) 55%,var(--line));padding-left:10px}
.trig b{color:var(--ink);font-weight:600}

.note{margin:8px 0 0;font-size:12px;line-height:1.5;color:var(--mut);
  border-left:2px solid var(--cond);padding:2px 0 2px 10px}
.note em{font-style:normal;font-family:ui-monospace,Consolas,monospace;font-size:9.5px;
  letter-spacing:.1em;text-transform:uppercase;color:var(--cond);display:block;margin-bottom:2px}
.note.n-fixed,.note.n-fixed6{border-left-color:var(--up)} .note.n-fixed em,.note.n-fixed6 em{color:var(--up)}
.note.n-design{border-left-color:var(--gate)} .note.n-design em{color:var(--gate)}

footer{margin:40px 0 60px;padding-top:18px;border-top:1px solid var(--line)}
footer p{margin:0;color:var(--dim);font-size:12.5px;max-width:80ch}

@media (max-width:900px){
  .sk{grid-template-columns:44px 1fr;gap:12px}
  .ds,.ef,.affbox{grid-column:1/-1}
  .ef{padding-top:2px;border-top:1px dashed var(--line)}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>"""

CLS_ORDER = ['Assault', 'Medic', 'Recon', 'Robotics']
ACCENT = {'Assault': '#ff7a45', 'Medic': '#37d3a6', 'Recon': '#a882ff', 'Robotics': '#3fb4ff'}
BAL_ACC = '#e3b53c'
SHARED = '155'   # Balanced - every class has it

SKILL_NAME = {}
for _g, _ns in trees.items():
    for _n in _ns:
        SKILL_NAME[_n['id']] = _n['name']

# Device name -> who its modes aim at, so an on-hit effect can say whether it lands on a
# team-mate or an enemy. Group Heal Savior and Killer Instinct are both type-505 "on whoever
# you hit"; the difference is entirely in what the skill is attached to.
DEVTGT = {}
DEVID = {}                      # device name -> id, so a name can find its icon
DEVICON = {}                    # device id -> base64 png
USED_ICONS = set()              # only emit CSS for icons actually referenced


def _walk_devices(obj):
    """inv_model.json is keyed by CLASS, each holding a device list - not a flat map."""
    if isinstance(obj, dict):
        if obj.get('name') and 'modes' in obj:
            yield obj
            return
        for v in obj.values():
            for d in _walk_devices(v):
                yield d
    elif isinstance(obj, list):
        for v in obj:
            for d in _walk_devices(v):
                yield d

try:
    _inv = json.load(io.open(os.path.join(OUT, 'inv_model.json'), encoding='utf-8'))
    for _d in _walk_devices(_inv):
        if _d.get('id'):
            DEVID[_d['name']] = str(_d['id'])
        for _m in (_d.get('modes') or []):
            t = ((_m.get('hit') or {}).get('tgt'))
            if t:
                DEVTGT.setdefault(_d['name'], set()).add(t)
    print('device targets resolved: %d devices' % len(DEVTGT))
    DEVICON.update(json.load(io.open(os.path.join(OUT, 'deviceimg.json'), encoding='utf-8')))
    print('device icons available: %d' % len(DEVICON))
except Exception as _e:
    print('note: inv_model.json unavailable (%s) - side labels degrade to "target"' % _e)

# Effect-group types that land on the CARRIER rather than on whoever is hit.
SELF_EGT = {261, 759, 1104, 266, 283, 263}


# Not a device anyone equips - it is the invisible baseline every character carries.
HIDE_DEV = {'HUMAN BASE ATTRIBUTES'}


def devs_for(node, cls):
    """Devices this skill reaches, limited to ones the class can actually equip. The data gates
    by weapon family, which spans classes - Combat Off-Hand Utility reaches Concussion Grenade
    as well as the Medic offhands - but a Medic cannot carry an Assault grenade, so showing it
    under Medic is misleading. Attack-type matching and the live-pool filter live in the
    resolver (gen_ix.py), not here."""
    out, seen = [], set()
    for d in (node.get('dev') or []):
        nm = d[0] if isinstance(d, list) else str(d)
        dc = d[1] if isinstance(d, list) and len(d) > 1 else ''
        if nm in HIDE_DEV or nm in seen:
            continue
        if cls and dc and dc != cls:
            continue
        seen.add(nm)
        out.append((nm, dc))
    return out


DEVBYSKILL = T.get('devbyskill') or {}


def side_of(node, f, cls=None):
    """you / allies / enemies / target - every line says who it lands on."""
    egt = f.get('egt') or 0
    if egt in SELF_EGT:
        return 'you'
    # A gated effect rides exactly its gate's devices, so who it lands on comes from those -
    # Super Engineer's +5 protection is gated to Repair (friend-only arms) and must not
    # inherit the enemy-targeting turrets from the rest of the skill's device list.
    rsk = f.get('rsk') or 0
    if rsk and str(rsk) in DEVBYSKILL:
        names = [d[0] for d in DEVBYSKILL[str(rsk)]]
    else:
        names = [nm for nm, _dc in devs_for(node, cls)]
    tg = set()
    for nm in names:
        tg |= DEVTGT.get(nm, set())
    # 'all' can hit enemies; a friend/self-only device set is firmly ally-side (the repair
    # arms carry {friend, self} and were falling through to the ambiguous bucket).
    HOSTILE = {'enemy', 'enemyself', 'all'}
    if tg and not (tg & HOSTILE):
        return 'allies'
    if tg and not (tg & {'friend', 'self'}):
        return 'enemies'
    return 'target'

NOTES = {
    742: ('fixed6', 'Falling Damage is stored as a 0&ndash;1 fraction: 1.0 Decrease-% = '
                    '<b>&minus;100%</b> &mdash; no fall damage at all. The fraction-scaling '
                    'rule previously stopped below 1 and rendered this as &minus;1%.'),
    890: ('design', 'Threat is PvE aggro: every point of damage you deal is a point of threat, '
                    'and bosses attack whoever holds the most. This skill deliberately raises '
                    'yours (+50% on melee) so they stay on you &mdash; the tank&rsquo;s trade. '
                    'See <em>How Threat Works</em> (docs/gameplay/threat.md).'),
    546: ('design', 'Raises the threat your damage generates by 15% across everything, keeping '
                    'PvE aggro on you &mdash; deliberate for a tank. See <em>How Threat Works</em> '
                    '(docs/gameplay/threat.md).'),
    598: ('design', 'The threat cut means rifle damage draws 10% less PvE aggro &mdash; bosses '
                    'come for you later than your damage says they should. See <em>How Threat '
                    'Works</em> (docs/gameplay/threat.md).'),
    674: ('data',    'The gate is Medic Guns (skill 405) and the Pain Gun carries skill 405, but the '
                     'text says &ldquo;excluding the Pain Gun&rdquo; &mdash; the resolver carves it out to match.'),
    852: ('data',    'Triage Wave is carved out: measured on a solo Triage rescue, it applies its own '
                     'effect group but never procs this one, while Healing Wave and Healing Grenade both do.'),
    902: ('fixed',   'Repeats on a 2s interval. The interval used to be dropped, so this skill '
                     'contributed nothing at all until 2026-08-05.'),
}
KIND_LABEL = {'conditional': 'conditional', 'reactive': 'reactive', 'on-hit': 'on hit'}


def trigger_of(f):
    """Plain-English condition for a non-passive effect."""
    sit, sv, rcn = f.get('sit') or 0, f.get('sv') or 0, f.get('rcn') or ''
    if sit == 1270:
        return 'fires when the target is <b>below %g%% health</b>' % sv
    if sit == 1271:
        return 'fires when the target is <b>above %g%% health</b>' % sv
    if rcn:
        return 'active only while <b>%s</b> is on you' % html.escape(rcn)
    if f.get('kind') == 'on-hit':
        return 'applied <b>on each hit</b>, for its listed duration'
    return ''


def fx_html(node, cls=None):
    """One line per DISTINCT value. The same property at the same value gated to four class
    jetpacks is one fact, not four, so those collapse; different values stay apart."""
    fx = node.get('fx') or []
    if not fx:
        return '<span class="none">no modelled effect</span>'
    # Same property at the same value collapses to one line - but only when the gates are the
    # same gate. Jetpack Power's four are "Assault Jetpack", "Medic Jetpack" and so on: one
    # effect on your jetpack, described four times, so they merge. Death Medic's two +200%
    # potency entries are Medic Guns and Area Poisons - different families, so they stay apart.
    # Normalising away a leading class word is what separates the two cases.
    CLASSWORDS = ('assault ', 'medic ', 'recon ', 'robotic ', 'robotics ')

    def gate_key(g):
        s = (g or '').lower()
        for w in CLASSWORDS:
            if s.startswith(w):
                return s[len(w):]
        return s

    groups = OrderedDict()
    for f in fx:
        # pv is part of the identity: an effect scoped to a category (potency, durations) is a
        # different stat per scope even at the same value - Station Buff's +20% Station Damage
        # and +20% Station Healing are two facts, not a duplicate.
        key = (f.get('p'), f.get('v'), bool(f.get('pct')), bool(f.get('neg')),
               f.get('kind'), f.get('iv') or 0, gate_key(f.get('rskn')), f.get('pv') or 0)
        groups.setdefault(key, []).append(f)

    rows, trigs = [], []
    for key, members in groups.items():
        f = members[0]
        v, neg = f.get('v', 0), f.get('neg')
        num = '%s%g%s' % ('&minus;' if neg else '+', abs(v), '%' if f.get('pct') else '')
        chips = []
        k = KIND_LABEL.get(f.get('kind'), '')
        if k:
            chips.append('<em class="k k-%s">%s</em>' % (f.get('kind'), k))
        # Show every gate the collapsed group actually spans. Dropping them entirely was wrong:
        # Death Medic carries +200% potency TWICE, once gated to Medic Guns and once to Area
        # Poisons, and merging them into one unlabelled line reads as a single buff when a medic
        # can carry one weapon family without the other.
        raw = []
        for m in members:
            g = m.get('rskn')
            if g and g not in raw:
                raw.append(g)
        if raw:
            # One gate per line by construction. Several raw names here means the same gate
            # per class ("Assault Jetpack", "Medic Jetpack", ...), so show it once, unprefixed.
            label = raw[0] if len(raw) == 1 else gate_key(raw[0]).title()
            chips.append('<em class="k k-gate">%s</em>' % html.escape(label))
        # A pv-scoped effect only touches that effect category. Prop 376 already carries the
        # scope as its NAME (the game never says "potency"); for the rest (duration modifiers)
        # the scope is a chip, which is also what tells apart Eagle Eye's two +30% duration
        # lines (Additional Damage vs General Debuff).
        if f.get('pvn') and f.get('p') != 376:
            chips.append('<em class="k k-scope">%s</em>' % html.escape(f['pvn']))
        side = side_of(node, f, cls)
        chips.append('<em class="k k-side k-%s">%s</em>' % (side, side))
        if f.get('iv'):
            chips.append('<em class="k k-iv">every %gs</em>' % f['iv'])
        if f.get('life'):
            chips.append('<em class="k k-life">%gs</em>' % f['life'])
        # The arrow is the BENEFIT, the sign is the raw calc method - they disagree on
        # purpose: "-100% Movement Penalty" is a gain (green up-arrow, literal minus), and a
        # protection shred on the enemy is a gain too. 'choice' = a deliberate build trade
        # (stacking threat to tank, owner's ruling 2026-08-06): neutral, chipped, never
        # asserted good or bad. '' = unclassified: loud and amber, investigated never guessed.
        ben = benefit.classify(f.get('p'), bool(neg), f.get('pv') or 0, side)
        # "bad" on somebody ELSE means the line reads as buffing enemies or debuffing allies.
        # No skill does that on purpose - it is a side-reading anomaly (Stealth Protection's
        # +1 on-hit protection stores as a lands-on-target group) - so it is flagged for
        # investigation rather than asserted. Genuine red is reserved for self-costs.
        if ben == 'bad' and side != 'you':
            ben = ''
        if ben == 'choice':
            chips.append('<em class="k k-choice" title="More threat keeps PvE aggro on you - '
                         'the tank&#39;s job, taken on purpose. Less keeps bosses off you. '
                         'See How Threat Works (docs/gameplay/threat.md).">build choice</em>')
        elif not ben:
            chips.append('<em class="k k-flag">polarity?</em>')
        arrow = {'good': '&#9650;&#8202;', 'bad': '&#9660;&#8202;'}.get(ben, '')
        rows.append('<li><b class="%s">%s%s</b> <span class="pn">%s</span>%s</li>'
                    % ({'good': 'up', 'bad': 'dn', 'choice': 'ch'}.get(ben, 'unk'), arrow, num,
                       html.escape(f.get('n', '?')),
                       ' ' + ''.join(chips) if chips else ''))
        t = trigger_of(f)
        if t and t not in trigs:
            trigs.append(t)
    out = '<ul class="fx">%s</ul>' % ''.join(rows)
    for t in trigs:
        out += '<p class="trig">%s</p>' % t
    return out


def affects_html(node, cls=None):
    """Expandable, complete, and columnar - a truncated list is no use for checking coverage,
    and a single tall list is hard to scan. Every device list is grouped under a class heading
    and laid out in columns; Balanced gets one column per class, a class tree gets one heading
    whose devices flow across as many columns as fit."""
    devs = devs_for(node, cls)
    if not devs:
        return ''
    by = OrderedDict()
    for nm, dc in devs:
        by.setdefault(dc or 'Other', []).append(nm)
    single = len(by) == 1
    blocks = []
    for c, v in by.items():
        head = '<i>%s <b>%d</b></i>' % (html.escape(c), len(v))
        items = []
        for x in sorted(v):
            did = DEVID.get(x)
            if did and did in DEVICON:
                USED_ICONS.add(did)
                ico = '<span class="di i%s"></span>' % did
            else:
                ico = '<span class="di"></span>'
            items.append('<li>%s%s</li>' % (ico, html.escape(x)))
        blocks.append('<div class="acls">%s<ul>%s</ul></div>' % (head, ''.join(items)))
    n = len(devs)
    # One column per class when several are involved, so the classes read side by side instead
    # of as one long stack. A single class has no columns to compare, so its devices flow into
    # as many columns as fit.
    grid = 'affgrid one' if single else 'affgrid'
    return ('<details class="affbox"><summary>affects <b>%d</b> device%s%s</summary>'
            '<div class="%s">%s</div></details>'
            % (n, '' if n == 1 else 's',
               '' if single else ' across %d classes' % len(by), grid, ''.join(blocks)))


def prereq(node):
    bits = []
    if node.get('psk') and SKILL_NAME.get(node['psk']):
        bits.append('after %s' % html.escape(SKILL_NAME[node['psk']]))
    if node.get('max', 1) > 1:
        bits.append('%d ranks' % node['max'])
    return ' &middot; '.join(bits)


def skill_row(node, cls=None):
    ic = icons.get(str(node.get('icon')))
    img = ('<img alt="" src="data:image/png;base64,%s">' % ic) if ic else '<span class="noic">&mdash;</span>'
    note = ''
    if node['id'] in NOTES:
        kind, text = NOTES[node['id']]
        note = '<p class="note n-%s"><em>%s</em>%s</p>' % (
            kind, {'display': 'display', 'data': 'text vs data', 'fixed': 'fixed 05 Aug',
                   'fixed6': 'fixed 06 Aug', 'design': 'by design'}[kind], text)
    pre = prereq(node)
    # The device list spans the description AND effect columns. Inside the narrow description
    # cell it only ever fitted two columns, which defeats the point of a column per class.
    return ('<article class="sk">'
            '<div class="ic">%s</div>'
            '<div class="nm"><h3>%s</h3>%s</div>'
            '<div class="ds"><p>%s</p>%s</div>'
            '<div class="ef">%s</div>'
            '%s'
            '</article>') % (
        img, html.escape(node['name']),
        ('<p class="pre">%s</p>' % pre) if pre else '',
        html.escape(node.get('desc') or ''), note, fx_html(node, cls),
        affects_html(node, cls))


def tier_label(gp):
    if not gp:
        return 'Open from the start'
    return 'Unlocks at %d point%s in this tree' % (gp, '' if gp == 1 else 's')


def tree_block(gid, accent, shared=False, cls=None):
    # Tree order: by the gate that unlocks a row, then down and across the grid as drawn.
    nodes = sorted(trees[gid], key=lambda n: (n.get('gp') or 0, n.get('y') or 0, n.get('x') or 0))
    out, cur = [], None
    for n in nodes:
        gp = n.get('gp') or 0
        if gp != cur:
            cur = gp
            out.append('<div class="tier"><span>%s</span></div>' % tier_label(gp))
        out.append(skill_row(n, cls))
    tag = '<span class="shared">every class has this tree</span>' if shared else ''
    return ('<section class="tree" style="--acc:%s">'
            '<header class="th"><h2>%s</h2><span class="cnt">%d skills</span>%s</header>'
            '<div class="rows">%s</div></section>') % (
        accent, html.escape(names[gid]), len(nodes), tag, ''.join(out))


parts = ['<title>Global Agenda &mdash; Skill Reference</title>', CSS]

navitems = [('balanced', BAL_ACC, 'Balanced')] + [(c.lower(), ACCENT[c], c) for c in CLS_ORDER]
parts.append('<header class="top"><div class="wrap">'
             '<p class="eyebrow">Global Agenda &middot; theorycraft console</p>'
             '<h1>Skill reference</h1>'
             '<p class="lede">Every skill in all nine trees, with the text the game shows beside '
             'the effects the console models. Grouped by the point gate that unlocks each row, '
             'in tree order.</p>'
             '<nav class="nav">%s</nav></div></header>' % ''.join(
                 '<a href="#%s" style="--acc:%s">%s</a>' % n for n in navitems))

body = ['<main class="wrap">']
body.append('<section class="clsblock" id="balanced" style="--acc:%s">'
            '<div class="clshead"><h2>Balanced</h2>'
            '<p>The one tree shared by all four classes.</p></div>' % BAL_ACC)
body.append(tree_block(SHARED, BAL_ACC, shared=True))
body.append('</section>')

for c in CLS_ORDER:
    gids = [str(g) for g in classes[c] if str(g) != SHARED]
    body.append('<section class="clsblock" id="%s" style="--acc:%s">'
                '<div class="clshead"><h2>%s</h2><p>%s. Balanced is shared with every class.</p></div>'
                % (c.lower(), ACCENT[c], c, ' and '.join(names[g] for g in gids)))
    for g in gids:
        body.append(tree_block(g, ACCENT[c], cls=c))
    body.append('</section>')

body.append('<footer><p>%d skills across 9 trees. Values come from <code>gaa.db</code> via the '
            'console generators. <b>The arrow is the benefit, the sign is the data:</b> '
            '&#9650; green means the line helps your build, &#9660; red means it costs you, '
            'and the +/&minus; stays the raw calc method &mdash; so &ldquo;&#9650;&nbsp;&minus;15%% '
            'Power Pool Cost&rdquo; and &ldquo;&#9650;&nbsp;&minus;5 Protection&rdquo; on an enemy '
            'both read as gains. Every line names who it lands on (you / allies / enemies). '
            'A <em>build choice</em> chip marks a deliberate trade with no universal polarity: '
            'stacking Threat keeps PvE aggro on you (the tank&rsquo;s job), shedding it keeps '
            'bosses off you &mdash; reductions arrow green, increases stay neutral. '
            'An amber value with a <em>polarity?</em> chip is unclassified and needs '
            'investigating, not guessing. '
            'Effects sharing a property, value, gate and category scope are shown '
            'once; a different gate or scope is a separate line. Effect Potency (prop 376) is '
            'labelled the way the game labels it &mdash; by the category it is scoped to '
            '(Disease, Knockback, &hellip;), never as &ldquo;potency&rdquo;. '
            '&ldquo;Affects&rdquo; lists the devices a skill reaches.</p></footer>'
            % sum(len(v) for v in trees.values()))
body.append('</main>')
parts.append(''.join(body))

# Icons are defined once each, as classes, AFTER the body so only the ones actually referenced
# are emitted. Inlining a data URI per row would repeat the same image for every skill that
# touches that device - 900 rows against 115 icons.
# deviceimg.json already stores a full data: URI, unlike tree.json's bare base64 for skills.
icon_css = ''.join('.i%s{background-image:url(%s)}' % (d, DEVICON[d])
                   for d in sorted(USED_ICONS))
parts.append('<style>%s</style>' % icon_css)
print('icons embedded: %d (referenced %d times)' % (len(USED_ICONS), len(USED_ICONS)))

refpath = os.path.join(OUT, 'skill-reference.html')
io.open(refpath, 'w', encoding='utf-8').write('\n'.join(parts))
print('wrote', refpath)
