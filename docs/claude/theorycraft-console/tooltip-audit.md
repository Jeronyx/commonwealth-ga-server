# Tooltip audit — every console device vs what the theorycraft actually models

Full sweep, 2026-08-13, owner-requested. For **each of the 115 devices**: what the in-game
tooltip says (from `asm_data_set_items.desc_msg_id`, verbatim, `|` = line break), how I read
it, what the console/timeline does with it, and anything special. Tooltips are prose, not
mechanics — where they disagree with the data, the data wins (established repeatedly: §18
protection "percentages" are flat; Boost Beam's "Multi" alt; Decoy's numbers).

**Legend for the verdict at the end of each entry:**
- ✅ **solid** — tooltip, data and model agree.
- ⚠️ **tooltip lies** — model follows the data; tooltip text is wrong or misleading.
- 🔶 **partial** — modelled, but a named aspect is missing (usually CC, stance or position).
- ❌ **gap** — the model is wrong or silent on something that matters. Backlog id given.

---

## Findings that came OUT of this sweep (new)

1. **❌ Multi-shot weapons undercount 5× / 3× (new backlog C13).** Prop 287 "rounds per
   trigger pull" (Stormer 5, Tempest 5, Spider Grenades 3) is rendered as a `Shots 5x` card
   chip and **consumed nowhere** — the run and the DPS solve both fire ONE slug per trigger.
   Stormer's real per-trigger output is 5 × 68 = 340 before mitigation, not 68.
2. **✅→fixed: Persist Pulse (prop 151).** My first reading called Oathbreaker's tooltip a
   lie (10s claim vs a 2s effect lifetime). The owner corrected it and the data agrees:
   Oathbreaker and Super Smash carry **Persist Pulse = 1.0** — they are 10-second FIELDS
   that re-fire every second, so the 2s debuff is permanently refreshed on anyone standing
   in the zone and lapses 2s after leaving. The run previously paid ONE pulse (a 10×
   undercount on Super Smash's damage); both now pulse for the full window.
3. **⚠️ Decoy**: tooltip "Reduces Threat by 30%" — data is **−20%** (prop 421, owner-doc'd).
4. **🔶 Medical Station**: tooltip "50% chance to remove negative effects" — the console
   models the cure as **guaranteed** per pulse; the chance roll is unmodelled.
5. **🔶 Zoom stances**: every "Aim / Zoom" ALT is a stance whose buffs (range +30%, self
   slow) apply *while the PRI fires zoomed*. The console stores them as a separate mode —
   selecting the zoom mode in the Combat tab fires nothing, and the zoom bonuses never
   compose onto the primary. Affects every SMG/rifle/sniper and the nanite guns.
6. **✅ GammaBurst's tooltip actually adds up** — "−20% protection on mechanical" = the
   −15 mech-only shred PLUS the −5 all-targets shred landing together; "−5% on Human" is the
   general one alone. Rare case of a tooltip being *precisely* right.
7. **Assassin Blade backstab** "+41% Additional damage" = flat 86 on a 219 base = **39.3%**
   of PRI (41% of what, is unclear — 86 is the stored number and is what lands).
8. **Nanite Restoration "Power Return +20%"** is flat +4/s for 10s = 40 power — 20% only of
   a 200 pool. On the real ~140–180 pools it is 22–29%.

Standing gaps that recur through the list (not re-argued per device): **crowd control**
(stun/KB/root/slow-as-movement) is entirely unmodelled — a Concussion Grenade contributes
damage and none of its purpose; **position** (walls blocking, turret arcs, wall-bounce,
splash line-of-sight) is out of scope by design; **stealth/detection** (D2/D3) is surfaced
as reveal chips but nothing in the timeline hides or reveals; **taunt** is AI-only and the
sim has no AI; **threat** (420/421) is PvE aggro, carried as data, no PvE sim.

---

# ASSAULT (28)

### Brawler's Beat Stick [6806] — Melee
- **Tooltip:** "A heavy stone maul|Slow attack speed|Backstab: Slows target 30% for 3s.|Right-click: Heavy Slam uses power| -Increased damage, knocks targets back"
- **Reading:** slow two-mode maul; RMB is a power-fed heavy hit (830: alt-fire, so it CANNOT block), backstab rider is a slow.
- **Console:** PRI 280 @0.85s; ALT 350, 40 power, knockback 30+10, target slow −25%/3s, self slow while swinging; backstab slow −30%/3s behind the backstab toggle; +20% vs mech equip passive.
- **Notes:** knockback and the slows land as tracked effects but move nobody (CC gap). One of only two melees with no block (with Assassin Blade), and the card correctly cycles off/PRI/ALT. ✅ (CC caveat)

### Impact Hammer [5801] — Melee
- **Tooltip:** "Can block.|Backstab: Ignite target for 3s."
- **Reading:** block-only RMB (no counter), backstab applies a burn.
- **Console:** PRI 300 @0.63s; BLOCK 15 pwr/s, no counter chips (block-only is correct — the data has no type-398 group); backstab DoT 48×3s on category 719 Ignite, so it takes the Ignite protection axis and can be refused (S31).
- **Notes:** "Can block" vs Radiant's "Does damage on block" is a real data distinction the console preserves. ✅

### Radiant Axe [3973] — Melee
- **Tooltip:** "Does damage on block.|Backstab: Ignite target for 3s."
- **Reading:** blocking counters the attacker.
- **Console:** PRI 208; BLOCK 15 pwr/s + Counter: 200 dmg + slow −50%/3s to whoever hits the block; backstab burn as Impact Hammer.
- **Notes:** counters resolve as type-398 BLOCK_HIT (attacker-side); the timeline has no incoming-melee model, so counters never fire in a run — bench-only. 🔶

### Heatwrack M.A.S.E.R. [4166] — Ranged, OC
- **Tooltip:** "+30% range while zoomed."
- **Reading:** standard long SMG with a zoom stance.
- **Console:** PRI 70 @0.11s, 2.15 pwr, range 150; ALT = zoom stance (+30% range/eff range, −20% speed).
- **Notes:** finding #5 — zoom never composes onto PRI in a run. ✅ otherwise

### Legion SMG [6882] — Ranged
- **Tooltip:** "Standard issue Legion SMG|+30% range while zoomed."
- **Console:** 100 @0.15s, 3 pwr — slower, harder-hitting SMG; zoom stance as above.
- **Notes:** non-OC (Output +70% roll only). ✅

### Rhino SMG [5788] — Ranged, OC
- **Tooltip:** "+30% range while zoomed.|Exceptional Accuracy."
- **Console:** 75 @0.11s, 2.15 pwr, range 100/90. Accuracy is not a modelled stat (nobody misses in the timeline) — "Exceptional Accuracy" is real in game (spread) and invisible here by design.
- **Notes:** the sim's no-miss assumption flatters low-accuracy guns relative to this one. ✅

### Stormer [4196] — Ranged, OC
- **Tooltip:** "Fires 5 slugs per shot."
- **Reading:** shotgun — 5 independent pellets per trigger.
- **Console:** card shows `Shots 5x`; **the run fires ONE 68-damage slug per 0.5s trigger.**
- **Notes:** **finding #1 — 5× damage undercount (C13).** Each slug should mitigate (and drain shields, and pay on-hit effects) independently. ❌

### GammaBurst Launcher [2790] — Specialty, OC
- **Tooltip:** "-20% protection on mechanical for 5sec.|-5% protection on Human for 5sec."
- **Console:** 500 AoE + `Mech: Phys Prot −15/5s` + `Phys Prot −5/5s`.
- **Notes:** finding #6 — the tooltip is the SUM as experienced per physicality (mech takes −15 and −5 = −20; humans −5). Mech shred lands only on structures (players are never mechanical). Eagle Eye does NOT amplify these (its scope is cat 986). ✅

### Headhunter Launcher [1991] — Specialty, OC
- **Tooltip:** "Rockets track enemies."
- **Console:** 500 AoE rocket @1s; tracking is a projectile-flight property — the timeline has no projectiles or misses, so tracking is moot (everything already hits).
- **Notes:** in game tracking trades away lead-skill; the sim can't see that difference. ✅

### Helot Minigun [6896] — Specialty
- **Tooltip:** "…|Heavy impact shots|Speed reduced while firing|Improved accuracy|Right-click: Roots user in place| -Reduces Air Speed while firing| -Deals increased damage| -Reduced power consumption"
- **Console:** PRI 91 @0.1s, 1.5 pwr, self slow −48% while firing; ALT 100 @0.1s, **0.5 pwr**, self ROOT + air speed −75%. Knockback 1.5/shot ("heavy impact").
- **Notes:** root/self-slow tracked but positionless; the ALT's power economy (3× cheaper AND harder-hitting) is the real reason to root, and the sustain figures show it. ✅

### Inferno-X Cannon [2914] — Specialty, OC
- **Tooltip:** same RMB text as Helot.
- **Console:** PRI 99/ALT 110, same costs as Helot, no knockback.
- **Notes:** the starvation-episode logic in the run was literally tuned on this gun (the 16-report flatline). ✅

### Longbow Launcher [5789] — Specialty, OC
- **Tooltip:** "Shoots a timed explosive grenade.|Detonates immediately on direct impact.|Enhanced launching range."
- **Console:** 334 AoE @0.3s, range 1000 (vs Tremor's 500 — the "enhanced range").
- **Notes:** timed-vs-impact detonation is a projectile behavior; the sim resolves every shot as an immediate hit, which matches the direct-impact case. ✅

### MagmaLance [3695] — Specialty, OC
- **Tooltip:** *(empty)*
- **Console:** 450 AoE + 100×2s burn (cat 719, refusable, protection-axis Ignite).
- **Notes:** nothing to compare — the data is the only voice. ✅

### Tremor Launcher [1994] — Specialty, OC
- **Tooltip:** "Shoots a timed explosive grenade.|Detonates immediately on direct impact."
- **Console:** 334 AoE @0.3s, radius 15 (biggest launcher splash), range 500.
- **Notes:** as Longbow. ✅

### iMINIGUN [1987] — Specialty, OC
- **Tooltip:** "Shots cause knockback.|Speed reduced while firing.|-15% protection on Mechanical targets.|Right-click: Roots…"
- **Console:** PRI 91/ALT 100 @0.1s, mech shred −15/1s re-applied per shot (a permanent −15 on any structure under fire), knockback 1/shot.
- **Notes:** the −15 "%" is flat 15 (§18). Mech shred = timed armour strip on structures, exactly where it lands. ✅ (KB caveat)

### AOE Shield [2004] — Offhand
- **Tooltip:** "Immune to AOE damage for 10s or 2000 damage.|Speed reduced."
- **Reading:** both limbs real: duration AND pool cap, whichever first.
- **Console:** pool 2000 (×386 mods) behind `AOE Prot +100` — immunity vs rating 100 on the AOE axis only. Drains by the post-mitigation slice per the calibrated rule (measured-fights §4). Against ranged/melee it contributes NOTHING except triggering Aegis Armament.
- **Notes:** the classic trap — "shielded" ≠ safe; axis must match. Self slow −10% tracked, movement unmodelled. ✅

### Berserk [5809] — Offhand
- **Tooltip:** "+25% Melee damage for 8s.|+15% Melee protection for 8s.|+30% Speed for 8s."
- **Console:** all three, 8s; melee prot is **flat +15**, tooltip's % is prose (§18).
- **Notes:** the +25% joins the melee skill layer as a live buff (post-C9 sum rule). ✅

### Concussion Grenade [2498] — Offhand, OC
- **Tooltip:** "Massive knockback on target."
- **Console:** 800 AoE + Knockback 1000. The knockback — the entire point per the tooltip — moves nobody (CC gap).
- **Notes:** contributes as a hard-hitting 60s-cooldown nuke; its displacement value is invisible. 🔶

### EMP Grenade [2022] — Offhand
- **Tooltip:** "Stuns mechanical targets for 4s.|-40% protection on stunned targets.|Damages mechanical targets each second for 4s."
- **Console:** 600 AoE to players; the stun, the −40 all-prot strip and the 60×4s burn are **Mech:**-scoped (cats 653/921 — players immune) and land only on aimed structures.
- **Notes:** vs structures this is the premier armour-stripper; mech stun (structure stops acting 4s) is CC and unmodelled. 🔶

### Incendiary Grenade [2019] — Offhand
- **Tooltip:** *(empty)*
- **Console:** 600 AoE + 100×10s ignite. This is the grenade that VALIDATED the AOE-axis selection and category-axis burn rules to the unit (damage-pipeline §8).
- **Notes:** measurement anchor. ✅

### Overcharge [5806] — Offhand
- **Tooltip:** "Instant attack.|Massive knockback on target.|Deals a high amount of threat to enemy npcs."
- **Console:** 400 AoE @45s cd + KB 1000 + **Threat +4000 flat** (prop 420 — the injection, not the −% modifier; owner-doc'd distinction).
- **Notes:** threat is PvE aggro — carried, displayed, no PvE sim. KB unmodelled. 🔶

### Perfect Target [3708] — Offhand
- **Tooltip:** "Taunts mechanical.|Immune to all attacks for 10s.|Cannot make attacks.|Speed greatly reduced."
- **Console:** +500 Phys/Energy, +200 Bio/Bleed/Ignite, +100 Slow prot for 10s (≥ rating ⇒ immunity via mitigation, not a flag), melee attack rate −100%, slow −25%, taunt 10s.
- **Notes:** the data only locks MELEE attacks; the full "cannot attack" is native. The sim does not stop you firing while it runs — don't. Taunt is AI-only. 🔶

### Power Stim [3699] — Offhand
- **Tooltip:** "Restores 140 power.|+50% power recharge for 11s."
- **Console:** exactly that; regen bonus is suppressed while firing (C4 — regen never runs during drain), so the +50% only matters in gaps.
- **Notes:** the instant 140 is the real payload for a drain build. ✅

### Range Shield [2013] — Offhand
- **Tooltip:** "Immune to range damage for 10s or 2000 damage.|Speed reduced."
- **Console:** the CALIBRATED shield (measured-fights §4): pool 2000×(1+386 mods) behind `Ranged Prot +100`; drains by the post-Physical slice; breaks in ~2.1s under the §1 rig; a ranged weapon cannot win through it — strip it (Neutralize) or wait it out.
- **Notes:** the model's best-tested piece after the damage chain itself. ✅

### Spider Grenades [2163] — Offhand, OC
- **Tooltip:** "3 Grenades chase enemy targets."
- **Console:** payload instance ("Pounce", 267 AoE, 50 HP each); card says `Shots 3x`/`Max out 3` but the run deploys ONE instance per throw.
- **Notes:** same family as finding #1 — the ×3 is not multiplied (C13). Chasing is projectile AI, moot in a no-position sim. ❌

### Protection Boost [2838] — Boost
- **Tooltip:** "Requires Morale Boost charge.|+25% Protection for self and allies for 10s."
- **Console:** +25 flat Melee/Ranged/AOE prot, 10s, team-wide (radius 50) + its own 2000 shield pool (cat 302 — the odd one out of the pool trio); morale-timed (the run's one calibration input).
- **Notes:** tgt 213 with splash ⇒ the caster IS included (unlike the 884 medic waves). ✅

### Super Smash Boost [5775] — Boost
- **Tooltip:** "…|Knockback enemies for 10s.|Increases assault damage resistance by 25%."
- **Console:** a 10s field pulsing every 1s (Persist Pulse) — 150 damage + knockback per pulse to everyone in radius 20, self Phys +25/10s. Was a single pulse before this audit; now pays all ~10.
- **Notes:** the knockback itself still moves nobody (CC gap), but the sustained damage field is real now. ✅ (KB caveat)

### Assault Crescent Jetpack [7031] — Jetpack
- **Tooltip:** "Leaked experimental jetpack prototype|Enhanced acceleration and airspeed|Allows shooting while flying."
- **Console:** movement only; costs 5.9 power per 0.25s while flown; reaches nobody by rule.
- **Notes:** its only combat meaning is the power it steals from your guns. ✅ (dev/unreleased content, included by policy)

---

# MEDIC (29)

### Legion Combat Knife [7485] — Melee
- **Tooltip:** "…|Fast attack speed|Does damage on block.|Backstab: Lacerates foe, causing bleeding for 5s"
- **Console:** 178 @0.54s; counter 200 + slow; backstab DoT 70×5s (cat 1016 Bleed — its own protection axis).
- **Notes:** ✅ (counter is bench-only, as all counters)

### Life Stealer [5800] — Melee
- **Tooltip:** "Can block.|Successful hit heals medic.|Backstab: Poison target for 5s.| -Deals damage each second| -Disease reduces healing received by 20%"
- **Console:** 208 @0.63s; **Self: Heal +50 per landed swing — paid per hit since the C11 fix** (same egt-759 mechanic as BioFeedback); backstab: 55×5s poison + Heal Received −20%/5s; block-only RMB.
- **Notes:** its own poison REFRESHES on re-application (measured — the burn-refresh rule was calibrated on this weapon). Roll oddity: `Output Mod +10.0` is a flat 10, not a percentage — carried as stored. ✅

### Poison Injector [3967] — Melee
- **Tooltip:** "Does damage on block.|Backstab: Poison target for 5s.| -…"
- **Console:** Life Stealer without the self-heal, with a counter.
- **Notes:** ✅

### Agonizer [2991] — Ranged, OC
- **Tooltip:** "Lowers target ability to heal by 5%.|Lowers target protection by 5%."
- **Console:** 200 @0.5s + DoT 20×4s + Heal Received −5%/4s + Phys Prot −5/4s, all riding every shot (4s timers permanently refreshed under fire).
- **Notes:** the −5s are flat/small but permanent while firing; anti-heal now actually consults the debuff (the liveHealMult fix). ✅

### Euthanizer Rifle [4154] — Ranged, OC
- **Tooltip:** "+30% range while zoomed."
- **Console:** 70 @0.11s SMG-pattern; zoom stance.
- **Notes:** ✅ (finding #5 applies)

### Legion Side Arm [6884] — Ranged
- **Tooltip:** "Standard issue pistol…|+30% range while zoomed."
- **Console:** 260 @0.65s, 10 pwr/shot — heavy single shots.
- **Notes:** ✅

### Pain Gun [4676] — Ranged
- **Tooltip:** "Target is slowed by 30%.|Target takes 30% more damage from any source.|Reduces target's ability to heal by 5%."
- **Console:** 7 dmg beam @0.25s whose payload is `+Dmg Taken 30%` (prop 316, applied BEFORE mitigation — the run fills it in), slow −30%, heal −5%; short 0.5–1s timers = "while the beam holds".
- **Notes:** its 860 Biological gate means it cannot even TARGET structures — bounces by rule, not just by the seeded +1000s. The +30% is the whole gun; the sim now delivers it. ✅ (slow is CC-tracked, movement unmodelled)

### Rockwind SMG [5797] — Ranged, OC
- **Tooltip:** "+30% range while zoomed.|Exceptional Accuracy."
- **Console:** Raven-pattern 75 @0.11s.
- **Notes:** ✅

### Adrenaline Gun [6898] — Specialty
- **Tooltip:** "Commonwealth prototype healing device|Increase Max HP by 400 for 10 sec"
- **Console:** ER-2 pattern: 200 instant + 86/tick HoT 10s + **Max HP +400/10s** on the target; support cadence (re-fires on expiry, not refire — the anti-spam rule).
- **Notes:** aimed friend device — cannot target self (C12); the Max-HP buff joins bucket contention like any timed effect. ✅

### BioFeedback Beam [2906] — Specialty, OC
- **Tooltip:** "Self heals while in use.|Alt-fire: +100% healing, increased cost."
- **Console:** PRI 52-to-target + **Self 18 per landed tick**; ALT 104 + Self 19.5, 7.5× the power. Self-heals pay even on a full-health target (Successful Hit trigger) — owner-verified, C11.
- **Notes:** resolver scales the self chips through the item layers (18 → ~38 on the HHHHHH roll); if in-game floaters say flat 18, raise it — logged in C11. ✅

### Boost Beam [3946] — Specialty, OC
- **Tooltip:** "+10% Damage buff on Target.|Alt-fire: +100% healing, increased cost."
- **Console:** heal 52/104 + `Dmg +10%/1s` (2s on ALT) on the target — a damage buff that rides the heal beam, re-refreshed per tick; ALT renamed **"Concentrated Healing"** (was the stale "Multi Healing Beam" — this audit's sibling fix).
- **Notes:** the +10% joins the target's skill layer live (C9 sum rule). ✅

### Multi-Boost Beam [6004] — Specialty, OC
- **Tooltip:** "+10% Damage buff on Target.|Alt-fire: Arcs to 3 targets.|Alt-fire: +15% Damage boost|Alt-fire: Reduced Healing."
- **Console:** PRI as Boost Beam; ALT heal 20 (the "reduced healing") + Dmg +15%/1s, **single target**.
- **Notes:** the arc-to-3 is native beam arcing and is NOT modelled — backlog **D9**. Until then its ALT undercounts by up to 3×. ❌

### Nanite Enhancement System [5064] — Specialty, OC
- **Tooltip:** "+5% Damage buff for 10 sec."
- **Console:** ER-2 heal (200 + 86/tick/10s) + Dmg +5%/10s on the target.
- **Notes:** cannot self-target (C12); its HoT persists across a weapon swap (D6) and contends in the Regeneration bucket vs Healing Grenade (Newest Wins in practice). ✅

### Nanite Restoration System [2061] — Specialty, OC
- **Tooltip:** "Power Return: +20% over 10 sec."
- **Console:** ER-2 heal + Power Regen +4/s for 10s.
- **Notes:** finding #8 — "+20%" is flat 40 power over the window; % depends on the pool. The power tick is regen-class and does NOT run while the target is draining (C4). ✅

### Frenzy Wave [3645] — Offhand
- **Tooltip:** "+25% Damage for 10 sec."
- **Console:** heal 300 + +25% on all three damage axes for 10s, radius 45, **allies-not-self** (884 Friend Only — the caster gets nothing; D7).
- **Notes:** Super Healer's +50-per-ally-hit rides this cast (C11). The +25%s join each ally's skill layer live. ✅

### Healing Grenade [2531] — Offhand, OC
- **Tooltip:** "Cures Poison, Ignite, and Disease."
- **Console:** 320 + HoT 64×15s + strips cats 303/719/305; 213 splash ⇒ the thrower IS healed standing in it (unlike the waves).
- **Notes:** its HoT displaces/loses to nanites under Newest-Wins-in-practice (measured 2026-08-03). ✅

### Healing Wave [2376] — Offhand
- **Tooltip:** "Cures all negative status effects."
- **Console:** 600 + strips 7 categories, allies-not-self.
- **Notes:** "all" = the 7 in its strip list; the medic's own debuffs are NOT cured (884). Super Healer pays per ally hit. ✅

### Neutralize Wave [3642] — Offhand
- **Tooltip:** "Removes shields and buffs.|Removes all positive healing effects.|Deals damage for each effect removed"
- **Console:** strips 15 categories including **770 Personal Shield** (the anti-Range-Shield answer) and the regen/HoT cats, base 110+115, plus per-category strip damage against what is actually running; the run holds it until the enemy has committed buffs (the "worth stripping" gate).
- **Notes:** THE counter to shield stacking; its damage scales with how buffed the target is. ✅

### Poison Aura [2379] — Offhand
- **Tooltip:** "-2% protection for 7 sec.|Healing received -15% for 7 sec."
- **Console:** 115 + DoT 115×7s + Heal Received −15% + Phys −2, hits every enemy (aura splash).
- **Notes:** flat −2, not "% " (§18). Cannot poison its owner (offensive guard). ✅

### Poison Grenade [2168] — Offhand, OC
- **Tooltip:** same as Poison Aura.
- **Console:** thrown version: 158 + DoT 158×7s, radius 20, `enemyself` — CAN catch the thrower.
- **Notes:** poison group's application value IS its per-tick (Strongest Wins is meaningful here). ✅

### Power Wave [4682] — Offhand
- **Tooltip:** "Charges nearby allies, granting 60 power instantly|Restores an additional 20 power over 4 seconds"
- **Console:** +60 instant + 5/s×4s, heal 300, **allies-not-self** — the medic's own pool gets NOTHING from their own Power Wave (884; worth knowing before relying on it for sustain).
- **Notes:** tooltip matches the data exactly (60 + 20). ✅

### PowerVirus Grenade [4690] — Offhand
- **Tooltip:** "-50% Power recharge for 7 sec.| "
- **Console:** 158 + DoT 158×7s + Power Regen −50%/7s on everyone splashed.
- **Notes:** regen suppression compounds with C4 (firing already stops regen) — it really bites in the gaps between bursts. Death Medic pays the medic per body hit. ✅

### Protection Wave [3639] — Offhand
- **Tooltip:** "+10% Protection for 7 sec."
- **Console:** heal 300 + **flat +10 Physical** for 7s, allies-not-self.
- **Notes:** Physical axis only — not the all-axis read the tooltip invites. ⚠️

### Regeneration [2246] — Offhand
- **Tooltip:** "Damage done is decreased by 25% while active."
- **Console:** self HoT 115/tick 15s + self Dmg −25%/15s (a self-penalty, coloured as a cost).
- **Notes:** the tooltip only mentions the penalty — the actual heal (the point) is tooltip-invisible. Category 1341 Self Heal: does NOT contend with Healing Grenade/nanites (C6). ✅

### Soul Stealer [6006] — Offhand
- **Tooltip:** "Self heals for each successful target hit."
- **Console:** BioShock splash 158 + DoT + **Self: Heal +200 per enemy the blast touches** — the per-body payout is exactly the C11 mechanic, so a 3-man splash pays 600.
- **Notes:** the sweep's best showcase of the per-hit-self-heal fix. ✅

### Triage Wave [5808] — Offhand
- **Tooltip:** "+100% Healing on target below 25% health.|+250 Power on target below 25% Health."
- **Console:** 600 + conditional 600 + conditional 250 power, gated at HP<25% **evaluated before its own heals land** (the one-hit-one-evaluation rule), allies-not-self.
- **Notes:** the "+100%" is a second 600, not a multiplier. ✅

### Healing Boost [2773] — Boost
- **Tooltip:** "Requires Morale Boost charge.|Heals you and your allies."
- **Console:** HoT 200/tick 10s team-wide; the ONLY boost priced 18480 morale (everything else 15840).
- **Notes:** 213 splash ⇒ includes the medic ("you and your allies" — tooltip agrees with the data here). ✅

### Oathbreaker Boost [5776] — Boost
- **Tooltip:** "…|Reduces enemy healing by 50% around self for 10s.|Damages enemies around self.|Heals medic for each player damaged.|Increases medic damage resistance by 20%."
- **Console:** a 10s field pulsing every 1s (Persist Pulse, finding #2): per pulse — 75 damage and Healing −50%/2s to every enemy in radius 35, +75 self heal per body hit (C11 pays per pulse per body), self Phys +20/10s.
- **Notes:** the 2s debuff + 1s pulse = permanently suppressed healing on anyone who stays in the zone, exactly the tooltip's 10s as experienced. Owner-corrected during review; the model now pulses. ✅
- **The "poison pool" trail is cosmetic.** The boost class is `TgDevice_HitPulse` (ga-source): activation arms a 10s PersistTimer and re-fires `FireAmmunition` every `s_fPersistHitPulse` (1s) — each pulse is an instantaneous radius-35 hit resolved from the DEVICE, which the medic is carrying, so the field is centred on the medic's position at each pulse. The mode row has `projectile 0 / deployable 0 / bot 0`, it is not in the volume-device family (slot 1354), and nothing it applies spawns an entity — so the pools left on the floor mark where past pulses went off and apply nothing. Two real tactical consequences: the aura samples at 1 Hz (a dash through between pulses is free), and `require_los_flag = 1` — cover inside the radius blocks a pulse.

### Medic Crescent Jetpack [7032] — Jetpack
- as Assault jetpack. ✅

---

# RECON (30)

### Assassin Blade [6895] — Melee
- **Tooltip:** "…|Backstab: +41% Additional damage|Right-click: Heavy Slash uses power| -Deals increased damage| -Reduces physical protection by 15."
- **Console:** PRI 219 + backstab flat 86; ALT 280, 40 pwr, Phys −15/4s; no block (rc 830).
- **Notes:** finding #7 — 86 is 39.3% of 219; the tooltip's "41%" doesn't resolve to any stored pair exactly. The −15 shred is cat-986-class contention (Strongest Wins bucket with Ballista/KI et al.). ✅
 
### Dual Daggers [5799] — Melee
- **Tooltip:** "Can block.|Fast attack.|Backstab: +41% Additional damage."
- **Console:** 260 @0.55s + backstab 86; block-only.
- **Notes:** highest sustained melee DPS of the recon set before backstab. ✅

### Ghost Sword [3970] — Melee
- **Tooltip:** "Does damage on block.|Backstab: +41% Additional damage."
- **Console:** 208 + backstab 86; counter 200+slow.
- **Notes:** ✅

### Rusted Machete [7486] — Melee
- **Tooltip:** "Fast attack speed|Does damage on block.|Backstab: Sunders armor reducing physical protection by 12 for 5s"
- **Console:** 178 @0.54s; backstab Phys −12/5s (the tooltip is exact: flat 12); counter.
- **Notes:** ✅

### Ballista [2110] — Ranged, OC
- **Tooltip:** "-10% target protection for 5 sec.|Only fires while in scope."
- **Console:** 585 @0.8s, 15 pwr; Phys −10/5s (cat 986 — the shred Eagle Eye amplifies to −13); zoom stance self slow −75%.
- **Notes:** THE calibration weapon (§0, matched to the unit). "Only fires in scope" is a stance constraint the sim ignores — it just fires. The KI-self-shot interplay was settled here. ✅

### Dweller Sniper Rifle [6883] — Ranged
- **Tooltip:** "Precision rifle of desert dweller origin|Only fires while in scope."
- **Console:** 657 @0.9s + knockback 20+5.
- **Notes:** carries the unexplained prop 243=18.0 shared by all three snipers (open question, project-status). ✅

### Raven SMG [6069] — Ranged, OC
- **Tooltip:** "+30% range while zoomed.|Exceptional Accuracy."
- **Console:** 75 @0.11s — the §1 rig weapon, the most-validated gun in the model.
- **Notes:** open C10 rides this gun: whether its +12%/+9% rolled mods actually multiply (one log line decides, 44 vs 36). ✅

### Rogue SMG [4946] — Ranged, OC
- **Tooltip:** "+30% Range while zoomed."
- **Console:** 70 @0.11s, range 150/100 — the long-range Raven trade.
- **Notes:** ✅

### Scorpia [3249] — Ranged, OC
- **Tooltip:** "-40% Healing on target for 5 sec."
- **Console:** 585 sniper + Heal Received −40%/5s — the strongest anti-heal in the game, and heals now genuinely consult it.
- **Notes:** ✅

### Spring Stealth [3023] — Specialty
- **Tooltip:** "Turn invisible to enemies.|Increases jump height."
- **Console:** power drain 1/0.5s + jump/air/fall-damage utils; **invisibility itself is unmodelled** (no detection layer, D2/D3) — nothing in a run behaves differently while "stealthed".
- **Notes:** its combat meaning today is only the power it costs. 🔶

### Sprint Stealth [2209] — Specialty
- **Tooltip:** "Turn invisible to enemies.|+34% Speed while in Stealth."
- **Console:** as Spring, speed +100 stored (tooltip says +34% — the stored figure is the raw speed add; movement is unmodelled either way).
- **Notes:** 🔶

### Targeting System [5807] — Specialty
- **Tooltip:** "On activation, can see enemies through nearby walls|Does not allow agent to stealth."
- **Console:** through-walls reveal chip (3000u/358°); **Equip:** +5% Range Damage and +20% Max Power — always-on for CARRYING it, modelled in the equip layer (live whether or not it's out).
- **Notes:** the equip passives are why it's worth a slot even unused; reveal is display-only. ✅

### Bionics [2368] — Offhand
- **Tooltip:** "+55% Speed for 12 sec.|Super jump for 12 sec.|No falling damage for 12 sec.|Immunity to Slows for 12 sec.|+50% Power recharge for 12 sec."
- **Console:** all of it: removes Slow on use, Slow Prot +1000 (refusal-class immunity via S31 — new slows are refused outright, not shortened), power regen +50%/12s, movement utils.
- **Notes:** slow-immunity actually functions in the sim (protection refuses the effect), unlike movement itself. ✅

### Deconstructor [5804] — Offhand
- **Tooltip:** "Destroys mechanical targets over time."
- **Console:** deployed mine that pulses 250 + `AOE Prot −50/1s` every 0.5s, lasts until destroyed, 550 HP, bio-immune like all structures.
- **Notes:** vs structures it shreds then kills; players take the pulses too (its damage is not mech-gated, only its purpose). ✅

### Decoy [2129] — Offhand
- **Tooltip:** "Taunts mechanical enemies.|Reduces Threat by 30% for 10s when activated."
- **Console:** self Threat −20%/10s (finding #3 — data says 20), 20s decoy lifespan; taunt is AI-only.
- **Notes:** threat category 1601 is its own bucket (owner ruling: extending it is a gain). PvE mechanic, carried not simmed. ⚠️

### EMP Bomb [2219] — Offhand
- **Tooltip:** "Stuns humans for 3 sec.|Stuns mechanical targets for 6 sec."
- **Console:** thrown mine, 900 AoE + Stun 3s (players) + Mech: Stun 6s.
- **Notes:** the human stun is the headline and is CC — unmodelled; the sim shows a big hit and no lockout. Cat 378 Stun has a protection axis (163) so SuperAgent/Sealed Systems refusal DOES work against it. 🔶

### Fire Bomb [3056] — Offhand, OC
- **Tooltip:** *(empty)*
- **Console:** 768 + 100×9s burn mine, bombs splash all enemies (owner ruling).
- **Notes:** ✅

### Graviton Bomb [4716] — Offhand
- **Tooltip:** "Massive Knockback on hit."
- **Console:** 900 + KB 1100.
- **Notes:** KB unmodelled — as Concussion, its purpose is invisible. 🔶

### Melee Stim [2953] — Offhand
- **Tooltip:** "+25% Melee Damage for 8 sec."
- **Console:** exactly that, joins the melee skill layer live.
- **Notes:** ✅

### Range Stim [2218] — Offhand
- **Tooltip:** "+25% Range Damage for 5 sec."
- **Console:** +25 (→37.5 with Stim Boost) for 5s (→6.5 with Stim Duration); the §1 rig's window and the fight-timing anchor of the whole calibration.
- **Notes:** ✅

### Sealed Systems [3704] — Offhand
- **Tooltip:** "Removes any negative status effects.|Immune to all negative effects for 20 sec.|Heals for each effect removed."
- **Console:** removes 5 categories + 300 heal + Bio/Disease/Ignite/Stun Prot +1000 for 20s — the S31/32 showcase: protection ≥ rating REFUSES re-application outright (a Pain Gun's anti-heal cannot land again for the window).
- **Notes:** "all negative effects" oversells: 4 protection axes, so e.g. slows/knockback are NOT covered. ⚠️

### Standard Mine [2225] — Offhand, OC
- **Tooltip:** "Minor Knockback on hit.|Maximum of three mines deployed."
- **Console:** 588 mine, deploy 4s, 400 HP; the game bakes in that only ONE of each mine type damages — each throw replaces the last (owner-doc'd), so "max 3" is presence, not stacked damage.
- **Notes:** ✅

### Sticky Poison Mine [2897] — Offhand
- **Tooltip:** "Mine will stick to surfaces.|Slows target -30% for 5 seconds.|Maximum of three mines deployed."
- **Console:** 351 + DoT 35×5s + slow; sticking is positional.
- **Notes:** ✅

### Venom Bomb [4708] — Offhand
- **Tooltip:** "-40% protection for 5 sec."
- **Console:** 900 + DoT 130×5s + **Phys −40/5s on players AND the mech mirror on structures** — the hardest protection shred in the inventory.
- **Notes:** flat 40 (§18); contends in the shred bucket. ✅

### Visual Scanner [2176] — Offhand
- **Tooltip:** "+10% Range Damage for 20sec.|Can see enemies in Stealth for 20sec."
- **Console:** +10 (→15 with Stim Boost) range damage 20s (→26 with the TTTCCC roll) + stealth reveal (display-only).
- **Notes:** the §4 shield fight settled that the measured rig ran WITHOUT it — worth remembering it exists when reproducing fights. ✅

### Vulture Vision [6012] — Offhand
- **Tooltip:** "+10% Damage for 20 sec.|Enemies below 25% health are highlighted."
- **Console:** +10% ALL damage (prop 65 — melee included, unlike the scanner) + low-health highlight chip.
- **Notes:** ✅

### Fashion Boost [7559] — Boost
- **Tooltip:** "Grants an immense fashion boost.|…|+20% Max Health 30 sec.|+40 Power Pool 30 sec.|+20% Power Pool Recharge 30 sec.|+15% Damage and Healing 30 sec."
- **Console:** all five effects team-wide; duration chip reads 28s vs the effects' 30s (two stored numbers; the effects' own 30 governs).
- **Notes:** zDev/unreleased content, included by policy. ✅

### Sensor Boost [2846] — Boost
- **Tooltip:** "…|+20% Speed for 10 sec.|+40% Damage for 10 sec.|Can see enemy stealth for 10 sec."
- **Console:** +40% on all three damage axes for 10s team-wide (the timeline-shifting boost the morale calibration exists for), speed util, stealth reveal 300u (vs the scanner's 3000u — a tenth the radius).
- **Notes:** ✅

### Shatter Bomb Boost [2113] — Boost
- **Tooltip:** "Requires Morale Boost charge.|Deploys a large bomb."
- **Console:** morale-gated 3000-damage 40-radius bomb + Stun 3s (players, CC-unmodelled) + vs structures: 2000×2s DoT and Phys/AOE −100 (deletes structure armour entirely for 2s).
- **Notes:** 🔶 (stun)

### Recon Crescent Jetpack [7033] — Jetpack
- as Assault jetpack. ✅

---

# ROBOTICS (28)

### EnergyBurn Mace [3951] — Melee
- **Tooltip:** "Does damage on block.|Backstab: -30 Power."
- **Console:** 208; backstab −30 POWER to the victim (lands, gated on the backstab toggle); counter.
- **Notes:** power drains are target-side and modelled; the tooltip is exact. ✅

### Heavy Wrench [7484] — Melee
- **Tooltip:** "An old metal wrench|Fast attack speed|Does damage on block.|Backstab: Slows target by 30% for 5s."
- **Console:** 178 @0.54s; backstab slow; counter.
- **Notes:** carries the unexplained `effect_groups.health = 1` on its slow category (open D4) — excluded, not a pool. ✅

### Mace and Shield [5802] — Melee
- **Tooltip:** "Can block.|Backstab: -30 Power.|+100% Damage on successful block."
- **Console:** 180; block costs **1 pwr/s** (vs everyone else's 15 — the shield is the point) and counters for **360** (=2×180, the tooltip's "+100%").
- **Notes:** the counter is bench-only (no incoming-melee model in the run). ✅

### Colony Energy Rifle [6885] — Ranged
- **Tooltip:** "This gun is not of human origin|+30% Range while zoomed."
- **Console:** Legion-SMG pattern 100 @0.15s.
- **Notes:** ✅

### HEL-TAC Rifle [4158] — Ranged, OC
- **Tooltip:** "+30% Range while zoomed."
- **Console:** 70 @0.11s, range 150.
- **Notes:** ✅

### Harken SMG [5798] — Ranged, OC
- **Tooltip:** "+30% range while zoomed.|Exceptional Accuracy."
- **Console:** Raven-pattern 75 @0.11s.
- **Notes:** ✅

### Rumbleblaster [3523] — Ranged, OC
- **Tooltip:** "Fires a wall-bouncing, AoE damage projectile."
- **Console:** 375 AoE @0.75s; wall-bouncing is positional and unmodelled.
- **Notes:** 🔶 (bounce)

### Techno Blaster [6897] — Ranged
- **Tooltip:** "…|Right-click: Charge up high impact blast| -Requires 50 Power| -Knockback and increased damage/radius"
- **Console:** PRI as Rumbleblaster; ALT 475, radius 7, 50 power, KB 700.
- **Notes:** 🔶 (bounce, KB)

### Tempest [4192] — Ranged, OC
- **Tooltip:** "Fires 5 slugs.|Causes Knockback."
- **Console:** ONE 68 slug per 0.5s trigger — **finding #1, 5× undercount (C13)**.
- **Notes:** ❌

### A.R.C. Repair Arm [2046] — Specialty, OC
- **Tooltip:** "Speeds deployment of turrets and stations.|+30% Damage buff on target.|Alt-fire: Arcs beam to multiple targets, reduced repair."
- **Console:** repair 48/tick + Dmg +30%/1s + Deploy Rate +4.5; ALT repairs 40 arced… as a single target (arcing unmodelled, same class as D9); aims ONLY at friendly structures (mech gate 861 — now data-confirmed, D8).
- **Notes:** two known holes are open items: welding does not yet ACCELERATE construction in the run, and the arm's damage buff is not applied to the structure's output (project-status "pick up here" #1). 🔶

### Focused Repair Arm [2918] — Specialty, OC
- **Tooltip:** "…|+15% Damage buff on target.|Alt-fire: Increased Repair, +40% Damage."
- **Console:** PRI repair 48 + Dmg +15%; ALT repair 85 + Dmg +40% — the single-target trade of the A.R.C.
- **Notes:** same two holes as the A.R.C. 🔶

### Force Target [5811] — Specialty
- **Tooltip:** "Target taunts mechanicals for 5 sec.|Requires specialty Weapon slot."
- **Console:** 200 @0.5s + Taunt 5s rider.
- **Notes:** taunt points AI at the taunter and ONLY at pawns (owner-confirmed — even taunted AI never targets a structure); no AI in the sim, so it's a mid SMG here. 🔶

### Nanite Repair [5810] — Specialty, OC
- **Tooltip:** "Increases deployment rate."
- **Console:** repair 100 instant + 100/tick 10s + Deploy Rate +3.5/10s, structures only (861).
- **Notes:** the ER-2 of welding; same welding-acceleration hole. 🔶

### Auto Cannon [3755] — Offhand
- **Tooltip:** "90 degree forward firing arc.|-20% Mechanical Damage"
- **Console:** 40s-build turret, 147 @0.2s, 1100 HP; `Deployed: vs Mech −20%` = the CANNON deals less to mechanical targets; firing arc positional.
- **Notes:** turret targeting follows the pawn rule (acquires players/bots, never structures) — but a PLAYER may aim their own weapons at it freely; turret-vs-turret is legal when aimed by the run. ✅ (arc)

### Eye Drone [2675] — Offhand
- **Tooltip:** "Can see stealth players.|Cannot move.|Limited life."
- **Console:** 1s deploy, 10s life, 52 @0.2s, KB-immune (+1000), 500 HP; stealth reveal display-only.
- **Notes:** lifespan is skill-extendable; lives its real lifecycle in the run. ✅

### Flame Turret [5792] — Offhand
- **Tooltip:** "360 degree firing arc."
- **Console:** 25s build, 90 + 100×5s burn @0.1s, 1000 HP.
- **Notes:** the burn re-applies per shot — permanent ignite on whatever it holds. ✅

### Force Wall [2051] — Offhand, OC
- **Tooltip:** "Blocks all enemy fire.|Limited duration and damage absorption."
- **Console:** a shootable STRUCTURE (2370 HP, Phys +75, bio-channel +1000s, 20s) — the "absorption" limb; **what a wall DOES (blocking fire through its plane) is positional and unmodelled** (project-status outstanding #4).
- **Notes:** in the sim it's a damage sponge you can aim at, not cover. 🔶

### Grizzly Drone [2107] — Offhand, OC
- **Tooltip:** "-40% protection on mechanical targets.|Prioritizes mechanical targets.|Limited life."
- **Console:** 10s drone, 53 @0.2s + Mech: Phys −40/2s; "prioritizes mech" is AI preference — in the sim the aim is the user's choice.
- **Notes:** its shred makes it the anti-turret escort exactly as the tooltip intends. ✅

### Harrier Drone [4782] — Offhand
- **Tooltip:** "Limited life."
- **Console:** plain 57 @0.2s gun drone, 10s, 700 HP.
- **Notes:** ✅

### Hornet Drone [2279] — Offhand
- **Tooltip:** "-40% protection on mechanical targets.|Limited life."
- **Console:** rocket drone 275 AoE @1s + Mech: Phys/AOE −40/2s, 600 HP.
- **Notes:** ✅

### Lockdown Drone [4698] — Offhand
- **Tooltip:** "-30% Speed on target.|Cannot move.|Limited life."
- **Console:** stationary beam 100 @0.5s + slow −30%/1s re-applied per volley and lapsing when fire stops (the payload-rider pattern), KB-immune.
- **Notes:** slow tracked, movement unmodelled. 🔶

### Medical Station [2066] — Offhand
- **Tooltip:** "50% chance to remove negative effects."
- **Console:** 15s build, 1500 HP; aura pulse: Heal 154 + cures Poison/Disease/Ignite every 1s to the whole side.
- **Notes:** **finding #4 — the 50% chance is modelled as guaranteed.** Also the known loose thread: a Medical Station died ~0.6s faster under turret fire than the arithmetic predicts (project-status #2). 🔶

### Personal Turret [2300] — Offhand
- **Tooltip:** "180 degree forward firing arc."
- **Console:** 25s build, 147 @0.2s, 1000 HP.
- **Notes:** the deploy-time-units calibration device (C2). ✅ (arc)

### Power Station [4076] — Offhand
- **Tooltip:** "+10 Power per sec.|+5% Protection."
- **Console:** aura +10 power/s + flat Phys +5 pulse to the whole side, 1500 HP.
- **Notes:** station power is a GRANT, not regen — it works even while allies fire (C4 does not suppress it). Tooltip's % is flat (§18). ✅

### Rocket Turret [2095] — Offhand
- **Tooltip:** "90 degree forward firing arc."
- **Console:** 40s build, 1000 AoE @2.8s, 1320 HP — the siege piece.
- **Notes:** its AoE payload currently hits enemy PLAYERS only; a rocket amid enemy structures does not splash them (open ruling, project-status #3). 🔶

### Sensor [2326] — Offhand
- **Tooltip:** "+15% Damage.|Detects nearby stealth players.|Shows enemies on mini-map."
- **Console:** 15s build, 1500 HP; aura Dmg +15%/1s to the whole side; its own detection parameters live on the spawned entity and are not surfaced (D3); heavy own-protections (+20s, Stun +1000).
- **Notes:** the damage aura is the modelled value; the intel half is display-only. 🔶

### Dome Shield Boost [2886] — Boost
- **Tooltip:** "Requires Morale Boost charge.|Creates a dome shield for 15 sec."
- **Console:** morale-gated 2500-HP destructible dome (C5 closed it: substance = deployable health + Persist Time); blocking-through-the-surface is positional, unmodelled.
- **Notes:** 🔶 (as Force Wall)

### Robotics Crescent Jetpack [7034] — Jetpack
- as Assault jetpack. ✅

---

## Tally

| verdict | count | devices |
|---|---|---|
| ❌ gap | 4 | Stormer, Tempest, Spider Grenades (C13 ×3), Multi-Boost Beam (D9) |
| ⚠️ tooltip lies | 3 | Decoy (−20 not −30), Protection Wave (Physical only), Sealed Systems ("all" = 4 axes) |
| 🔶 partial | ~19 | everything whose PURPOSE is CC, position, stealth, taunt or chance — modelled as data, inert as mechanic |
| ✅ solid | ~89 | the rest — tooltip, data and model agree, several validated to the unit; Oathbreaker and Super Smash joined this row after the owner's Persist-Pulse correction was implemented |

The 🔶 set is one architecture decision, not twenty bugs: crowd control and position are the
two systems the timeline does not have. The measured-fights backlog already carries CC as the
next big item.
