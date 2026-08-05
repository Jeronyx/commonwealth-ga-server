# Skill → device resolution — what is wrong and how to rebuild it

Every "this skill affects these devices" list in the console and in the skill reference comes
from **`tools/device-console/skilldev.json`**. That file is a captured artifact: it was produced
once, on 2026-08-03, by a resolver that no longer exists, and `gen_tree.py` reads it from what
used to be a hard-coded scratchpad path. It has no generator, so it cannot be corrected, only
re-created. This document is the spec for re-creating it.

Reviewed against the game by the project owner on 2026-08-05; the findings below are theirs.

---

## 1. How the current file resolves, and where each mode fails

`skilldev.json` tags every skill with a `scope`:

| scope | count | how it resolved | verdict |
|---|---|---|---|
| `skill` | 68 | the effect group's `required_skill_id` — the game's own weapon-family gate | right by construction, but **broader than the tooltip** |
| `tree` | 29 | a loose semantic guess from the property id | **wrong often** |
| `category` | 2 | `required_category_value_id` (Aegis → shields, Stealth Protection → stealth) | correct |

### 1.1 `tree` scope — fixed 2026-08-05, keep the fix

The guess mapped a property to "devices that feel related", so prop 214 (ranged damage) collected
grenades and prop 321 (AOE damage) collected sniper rifles.

**The discriminator is the device's ATTACK TYPE, never its slot.** A device's slot says nothing
about how it attacks: Techro Blaster is an AOE weapon in the Ranged slot, Longbow is AOE in the
Specialty slot, Inferno-X Cannon is ranged in that same slot. Match `modes[].hit.atk`
(1 melee / 2 ranged / 3 AOE) against the property:

```
212 Damage Modifier - Melee  -> atk 1
214 Damage Modifier - Range  -> atk 2
321 Damage Modifier - AoE    -> atk 3
```

`gen_skillref.py` now does this at render time. **It belongs in the resolver**, not in the page.

### 1.2 `skill` scope — the real remaining problem

The gate is a weapon *family*, and a family is wider than the effect. The data has no field that
narrows it, so this cannot be fixed by reading harder — it needs a per-skill rule about what the
effect can meaningfully apply to.

Confirmed cases from the 2026-08-05 review:

| Skill | Shows | Should not, because |
|---|---|---|
| **Heavy Impact** | Rhino SMG, iMINIGUN, Incendiary Grenade | it amplifies **knockback**; those carry none |
| **Heal Durations I/II** | BioFeedback Beam, Healing Wave | those heals have **no duration** to extend |
| **Buff Enhancement** | Healing Grenade, BioFeedback Beam | same — needs confirming which of these carry a buff at all |
| **Poison Duration I/II** | Healing Boost, Regeneration, the Nanite guns | healing devices, not poisons |
| **Stealth Restealth** | Targeting Systems | not a stealth device |
| **Bio Rifle Range** | Pain Gun | tooltip says *"excluding the Pain Gun"*; gate is Medic Guns (405) and the Pain Gun carries 405 |
| **Station Buff** | Force Wall | check — is a Force Wall a station? |
| **Station Radius** | Force Wall | **a Force Wall is always the same size**, so radius cannot apply |
| **Super Supporter** | Dome Shield, Force Wall | check |
| **Super Ninja** (Infiltration) | Deconstructor | check why it resolves here |

**Suggested rule shape.** Instead of "every device in the gate family", intersect the family with
devices that actually carry something the effect can act on:

- lifetime modifiers (208) → only devices with an effect whose `lifetime_sec > 0`
- potency (376) → only devices carrying an effect in the property's `property_value_id` scope
  (this is already how Eagle Eye correctly reaches the Ballista debuff and not Killer Instinct —
  see `damage-pipeline.md` §15.2)
- radius (352, 382) → only devices with a radius to modify
- knockback potency → only devices applying a knockback category

Prop 376's scoping is the model to copy: `property_value_id` already limits an effect to one
category, and honouring it is generic rather than a special case.

---

## 2. Other corrections from the same review

- **Unequippable variants must be filtered.** Only the Crescent jetpack is in the live pool; the
  Combat / Hands Free / plain variants are not equippable and were padding Jetpack Power to 16
  devices, Super Flight to 4 and Spare Power likewise. `gen_skillref.py` now drops anything absent
  from the device model — the same 12 devices that have no icon in `deviceimg.json`. **Belongs in
  the resolver.**
- **Triage Wave must not appear under Group Heal Savior.** Measured on branch
  `device-usage-metrics`: a solo Triage rescue applies eg 22375 and no 16587, while Healing Wave
  and Healing Grenade both proc it. Mechanism unestablished — all three carry identical family-252
  linkage in the data — so this needs an explicit exception with a comment pointing at the
  measurement.
- **Super Healer's +50 on-hit heal lands on the CASTER, not the target.** The reference currently
  labels it as landing on whoever you hit. The side derivation (effect-group type, then the
  affected devices' targeting) gets the general case right but not this one.

---

## 3. Devices with no icon

Twelve, all jetpack variants, absent from `deviceimg.json`. Once the pool filter is in the
resolver these stop being referenced at all, so the gap closes itself.

---

## 4. Where this lives now

| File | Status |
|---|---|
| `tools/device-console/skilldev.json` | the captured artifact — **the thing to replace** |
| `tools/device-console/gen_tree.py` | reads it; also now emits `sit` / `sv` / `rc` / `egt` for triggers |
| `tools/device-console/gen_skillref.py` | builds the skill-reference page; carries the two fixes that belong upstream |

The reference page is published at
`https://claude.ai/code/artifact/1ce7a67c-4e92-47e3-b437-9850316cbb50`.
