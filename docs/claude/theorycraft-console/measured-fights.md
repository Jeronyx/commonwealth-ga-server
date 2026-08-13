# Measured fights — validating the model against the game

Live-fire results, what they confirmed, and the one thing they showed is not calibrated.
Companion to `damage-pipeline.md` (the formulas) and `skill-device-resolution.md` (which skills
reach which devices). Everything here was measured in game on 2026-08-05 unless marked otherwise.

---

## 1. The rig — max-damage Recon, Raven SMG

The build used for every number below. 13 points.

**Marksman (8), in this order** — each pick satisfies the next one's point gate exactly:
Recon Rifle Range → Recon Rifle Power Cost → **Recon Rifle Damage** → Stim Duration →
**Stim Boost** → **Killer Instinct** → **Sureshot** → **Super Sharpshooter**

**Balanced (5):** Passive Protection → Advanced Passive Protection → Power Pool Increase →
Power Pool Return → **Damage Increase: Ranged**

**Gear:** Raven SMG (OC), Range Stim, Visual Scanner.

| | |
|---|---|
| Weapon | 75 base × 1.75 Output Mod = **131 effective**, refire 0.11s, 2.15 power/shot |
| Rate | **9.5 shots/sec** with Super Sharpshooter's +5% attack rate |
| Damage layer | +30% passive → **+35%** with the on-hit → **+50%** with Visual Scanner → **+87.5%** with Range Stim |
| Range Stim | +25% base, **+37.5%** with Stim Boost · 6.5s (5s × 1.3 Stim Duration) · 45s cooldown |
| Visual Scanner | +10% base, **+15%** with Stim Boost · 26s · 60s cooldown |
| Killer Instinct | −10 target Physical, 3s, fires only above 75% target HP, cannot refresh |
| **Sustain** | **7.6 seconds of continuous fire** — 140 pool ÷ 18.5/sec drain |

**Eagle Eye is deliberately excluded.** All five of its effects are scoped by
`property_value_id` to General Debuff / Additional Damage / Knockback, and the Raven SMG applies
none of them — it has only its damage (Health −75) and a scope mode. It is a Ballista skill: the
Ballista carries eg 18975, a category-986 protection debuff, which Eagle Eye amplifies −10 → −13.

**Power is the real ceiling.** Regen is suppressed while firing (backlog C4, confirmed), so
continuous fire never regenerates. 7.6s of trigger time lines up almost exactly with the Range
Stim's 6.5s window — firing the stim at any other moment wastes it.

---

## 2. VALIDATED — no-shield TTK, predicted 5.3s, measured 5.3s

**Target:** Assault, 3 Balanced / 10 Tank, all-Ranged (RRRRRR) armour.

| | |
|---|---|
| Health | ~3,425 — 1300 × 1.70 armour × 1.55 skills (Tough as Nails 15%, Brick Wall 10%, Super Tank 30%) |
| Ranged protection | **55** — 21 armour + 34 skills (Truck-Tough 15, Heavy Armor 10, Super Tank 5, Brick Wall 4) |
| Physical protection | **39** — 30 base + 9 Balanced |
| Delivered fraction | `(1−0.39) × (1−0.55)` = **27.5%**, or 32% while Killer Instinct holds |

| Window | Effective DPS | Cumulative |
|---|---|---|
| 0–3s (Range Stim + Killer Instinct) | 690 | 2,070 |
| 3–5.3s (KI expired) | 594 | 3,425 — dead |

**This is the strongest validation the model has.** The Ballista tests that calibrated the damage
chain were against 30 Physical / **0 Ranged**; this held to the second at 39 Physical / 55 Ranged.
It confirms, together: Output Mod as its own multiplicative layer, the skill layer summing,
two multiplicative protection axes, Killer Instinct's 3s window, and Stim Boost amplifying Range
Stim's buff.

---

## 3. Shields — the two behave completely differently against a ranged weapon

Both are 2000-point pools (`effect_groups.health`), 10s life, 60s cooldown, category 770.
Shield Strength scales pool (+25%) and lifetime (+40%).

| Shield | Grants | Against a RANGED attack |
|---|---|---|
| **Range Shield** (dev 2013, eg 5848) | **Protection − Ranged +100** | 55 → **155 vs rating 100 = immunity** |
| **AOE Shield** (dev 2004, eg 5835) | Protection − AOE +100 | **completely inert** |

`CalcAttackTypeProtection` is a switch — exactly one attack-type axis applies per hit, so a
ranged attack never looks at the AOE axis. **AOE Shield's headline +100 does nothing against an
SMG.** What a player feels from it is **Aegis Armament**: +25 Physical, reactive, while *any*
shield is up. The shield triggers the skill; the shield itself contributes nothing.

| Target state | Phys | Ranged | You deliver |
|---|---|---|---|
| No shield | 39 | 55 | **27.5%** |
| AOE Shield up (Aegis only) | 64 | 55 | **16.2%** |
| Range Shield up | 64 | 155 | **0%** |

So "shielded tank" is not one thing. Against AOE Shield you still kill, ~1.7× slower. Against
Range Shield a ranged weapon cannot win — the counter is to strip it (Neutralize Wave removes
category 770 outright) or to fight in the 40 of every 60 seconds it is down.

---

## 4. CALIBRATED (2026-08-13) — the pool absorbs the post-mitigation slice

**Measured:** Assault burns a Range Shield, immediately pops a second Range Shield. Recon fires
continuously with Range Stim. Recon runs out of power. **Assault left on ~800 HP** (≈2,625 taken).

**The console now reproduces this: 818 HP at the power-out moment** (rig per §1 with Range Stim,
no Visual Scanner — §4's fight description names only the stim). Shields break at 2.1s and 4.2s,
power dies at 7.6s. Run it in the Combat tab: rig on A firing the Raven with Range Stim on, the
tank on B with two Range Shields on — the auto-scheduler pops the second the moment the first
breaks.

**The drain rule was never actually free — it is fixed by code**, and it is the *slice*:

- `TgEffectGroup.uc` `CalcProtection` (ga-source, :745) submits
  `SubmitMitigationDamage(nProtectionType, int(fValue - fNewValue))` **per axis**, where
  `fValue` is the running value entering that axis. Axes chain Category → DamageType →
  AttackType, so by the Ranged axis the Physical cut has already happened.
- Our server's `TgEffectManager__SubmitMitigationDamage` (the reimplemented native) drains only
  a group with `m_nHealth > 0` **containing an effect on the submitted protection prop**. The
  Range Shield's group carries prop 218 only, so the Physical axis's submission finds no shield
  and falls through; the Ranged axis — immune under the shield, so its "reduction" is the whole
  remaining value — is what drains the pool.
- The pool is `GetEffectHealth` = `effect_groups.health` buffed by **prop 386 only**
  (`TgEffectGroup.uc:266`): 2000 × 1.25 Shield Strength = **2500** here. The roll's Output Mod
  does not touch it.

**Why the old table bracketed instead of hitting:** the gap was never in shield absorption. The
timeline had a damage-layer regression — an active support device's buff (Range Stim's +37.5%)
was folded into the weapon's baseline resolve *and* re-applied at fire time as a fresh
multiplicative layer, and the baseline half never expired with the stim. Buffs join the skill
layer as a SUM (`GetBuffedProperty` registers them in one layer): raw during the stim is
158.8 × (1 + .30 + .05 + .375) = 274, not 274 × 1.375. Fixed in `builder.js` (baseline excludes
the whole active-device layer; live buffs applied as `raw × (100+sp+live)/(100+sp)`).

**For the cheap in-game timing test** (Range Shield up, §1 rig firing with stim): the calibrated
model predicts the break at **~2.1s**, not the old table's 1.2/3.2 brackets.

### NEW TENSION — the Raven's item damage mods vs §2's 5.3s

With the layer regression fixed, the same §2 no-shield fight now computes **3.9–4.1s**, not the
measured 5.3s. The difference is almost exactly the Raven's rolled item mods (DDDDDD: Damage
Modifier - Range +12%, Effect Damage +9%), which the resolver multiplies in as the item layer —
**Ballista-verified to the unit** (§0/C1: 585 × 1.75 × 1.21 matched). Drop them and §2 computes
**5.2s ≈ measured**, but then this section's shield fight computes 1,999 HP left instead of 800.
The two measured fights disagree about whether the SMG's +21% applies; the shield fight and the
Ballista unit-match say yes, §2's stopwatch says no.

**Decisive one-log-line test:** single unbuffed Raven shot at the §2 tank. Combat log shows
**44** if the item mods apply (158.8 × 0.61 × 0.45), **36** if they don't (131.25 × 0.61 × 0.45).

### Second fight, set up but not yet run

Assault opens with Range Shield; Recon pops Range Stim and fires; the moment Range Shield ends
the Assault uses AOE Shield. Expected shape: a window of total immunity, then the shield breaks
and Killer Instinct fires on the next hit (target still at full HP), then AOE Shield contributes
only Aegis. Run it in the Combat tab rather than by hand.

---

## 4b. Heal weapons — self-heal confirmed, but the target field is suspect

**BioFeedback Beam (device 2906) heals its user on every landed shot, on both fire modes**, and
pays even when the target is at full health. Confirmed in game, and the console has it right:

| Mode | To the target | To the user |
|---|---|---|
| Healing Beam | Health **+52** (eg 9074, type 264 Hit) | Health **+18** (eg 18938, type **759 Successful Hit**) |
| Concentrated Healin' | Health **+104** (eg 9076, type 264) | Health **+19.5** (eg 9079, type **759**, cat Regeneration) |

The console labels these `Self: Heal +18.0` / `Self: Heal +19.5` and tags them egt 759 — the same
group type that carries Super Healer's +50 and Death Medic's +60. Because it is a *Successful
Hit* group it fires on landing the beam rather than on restoring missing HP, which is why it pays
against a full-health target. Worth remembering when judging a beam medic's self-sufficiency: the
primary is 70 HP per tick across both people, the secondary 123.5.

**RESOLVED (2026-08-13) — what `target_type_value_id` gates.** The field maps 1:1 onto
`TgDeviceFire.DeviceTargeterType` and is consumed by the native `UTgDeviceFire::IsValidTarget`
(decompiled in ga-source), which gates **both aim validation and splash iteration** — it defines
who the fire mode may legally *land on*, not who you can put your crosshair on:

| value | enum | rule in the decompile |
|---|---|---|
| 212 Enemy | TGDTT_Enemy | `IsEnemy` |
| 213 Friend and Self | TGDTT_Friend | `!IsEnemy` — **the user passes** |
| 846 Enemy and Self | TGDTT_Enemy_And_Self | `IsEnemy \|\| IsSelfOrOwner` |
| **884 Friend Only** | TGDTT_Friend_Only | `!IsEnemy`, **but the device's own user is explicitly rejected** |
| 703 All / 214 Self | TGDTT_All / TGDTT_Self | always / never a valid aim target |

So the heal beam's "Friend and Self" is not wrong: a single-target beam cannot self-heal because
**you can never occupy your own crosshair trace** — geometry, not data. Self-inclusion only bites
where the delivery can physically reach the user: splash and auras. That makes the field
trustworthy for side labels, and it carries one real distinction the console previously erased:

- **The five medic Waves (Healing, Frenzy, Protection, Power, Triage) are 884 — they buff every
  nearby ally EXCEPT the caster.** A Healing Grenade (213) heals the thrower standing in its
  blast; a Healing Wave does not heal the medic who cast it. gen2 now maps 884 → `friendonly`
  and the Combat tab scopes it "allies, not self". *Cheap in-game check if wanted: cast Healing
  Wave alone at missing HP — the code says your own HP does not move.*

The companion field `target_type_affect_value_id` is the **physicality gate** (step 5 of
`IsValidTarget`): 861 Mechanical on the three repair arms (why they weld only structures — the
console's name-regex special case has a data-driven source), 860 Biological on the heal/buff
family and on the Pain Gun (an 860+Enemy weapon is refused a mechanical target outright, upstream
of the seeded structure protections).

---

## 5. Coverage — what the console still does not model

From `backlog.md` plus this session:

- **Crowd control entirely.** Stun, Knockback, Pushback, Sleep, Immobilise. Protections and
  cleanses for them exist, but nothing in the timeline is ever stunned — so a Concussion Grenade
  or EMP Bomb contributes damage and none of its actual purpose. Heavy Impact, Built Brick Wall
  Tough and Cybernetic Speed are all balanced around a mechanic that is absent.
- **Effects lingering across a weapon swap** (D6) — a Nanite gun's HoT keeps ticking after the
  medic swaps away. Blocks honest rotations, and so blocks F4 (DPS/TTK).
- **Same-source heal refresh** — two Nanite guns, or one refiring inside its own HoT window.
  Cross-source contention was fixed; a source against itself was never established.
- **Protection-shred contention** — `applyStacking` still ranks by priority then lifetime, the
  same assumption the burn/heal measurements already overturned once.
- **Detection** (D2, D3) — Visibility Config bits are inferred, and reveal range/FOV live on the
  spawned entity so they never reach the device card.
- ~~**Shield absorption**~~ — calibrated, §4 above. The open shield question is now the Raven
  item-mod tension (§4, C10 in the backlog).
