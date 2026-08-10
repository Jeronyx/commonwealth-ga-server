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

## 4. NOT CALIBRATED — what the shield pool absorbs

**Measured:** Assault burns a Range Shield, immediately pops a second Range Shield. Recon fires
continuously with Range Stim. Recon runs out of power. **Assault left on ~800 HP** (≈2,625 taken).

That single number does not reconcile with either hand model, and the two bracket it widely:

| Pool absorbs | Shield breaks | Predicted HP left | vs measured 800 |
|---|---|---|---|
| the post-Physical slice (~81/shot) | ~3.2s | ~2,760 | far too tanky |
| the full raw hit (~226/shot) | ~1.2s | ~130 | far too fragile |

The damage half of the model is validated to the second (§2), so the gap is in **shield
absorption** — which has never been tested until now. 800 HP is the calibration point.

**How to settle it cheaply:** fire at a target with Range Shield up and nothing else, and time
how long until the shield breaks. ~1.2s means the pool absorbs raw; ~3.2s means it absorbs the
post-mitigation slice. Everything downstream follows from that one number.

**Do not hand-compute this.** The console already models shields as a pool plus the protections
it covers, resolves `SubmitMitigationDamage`, and scales the pool by Shield Strength. Run the
fight in the Combat tab instead — the hand arithmetic in this section is exactly why it is
recorded as *not* calibrated.

### Second fight, set up but not yet run

Assault opens with Range Shield; Recon pops Range Stim and fires; the moment Range Shield ends
the Assault uses AOE Shield. Expected shape: a window of total immunity, then the shield breaks
and Killer Instinct fires on the next hit (target still at full HP), then AOE Shield contributes
only Aegis. Run it in the Combat tab rather than by hand.

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
- **Shield absorption** — §4 above.
