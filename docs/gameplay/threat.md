# How Threat Works

The short version: **if you're doing the most damage to a boss, it's going to
shoot you.** Threat is the game's memory of who has been hurting an enemy
recently — and the enemies that use it turn on whoever's number is highest.

## Building threat

- **Damage builds threat.** Every point of health you actually remove from an
  enemy adds that much threat against you. Damage that gets absorbed by
  protection doesn't count, and neither does overkill on the killing blow —
  only health that really came off.
- **Some effects add threat directly.** The Overcharge's Nano Attack piles on
  a large chunk of extra threat with every hit, far beyond its damage — it's
  effectively a taunt.
- **Healing builds no threat.** Keeping your team alive doesn't put you on
  the enemy's radar. Only your own damage (and taunt effects) do.

## Threat fades — fast

Threat drains away at roughly **10% per second**. In practice that means an
enemy cares about *who's hurting it right now*, not who has done the most
total damage this fight. A few seconds of easing off is enough to fall from
the top of the list, and a burst from a teammate can take it over just as
quickly. Aggro is a live tug-of-war, not a scoreboard.

When the fight ends, the slate is wiped clean. Every new engagement starts
from zero.

## Threat modifiers

Some skills and devices scale the threat your damage generates, up or down:

| Source | Effect |
|---|---|
| **Super Tank** (Tank skill) | +15% threat on everything you do |
| **Assault Melee III** (Assault skill) | +50% threat, melee hits only |
| **Recon Rifle Damage** (Recon skill) | −10% threat with rifles |
| **Decoy** (Recon device) | −20% threat while it's deployed and you're firing |

Skill bonuses add together (an Assault with both Super Tank and Assault
Melee III generates +65% threat on melee swings). The Decoy's reduction is
applied on top of your skill total, so a Recon with the rifle skill firing
next to their Decoy generates only about 72% of normal threat.

If you want a boss's attention, build for more threat. If you want to shoot
in peace, build for less.

## The fine print: threat isn't the whole story

Threat decides who a boss *prefers* to attack — but plenty of other things
decide who gets attacked in practice:

- **Being seen starts fights.** Round a corner in front of an idle enemy and
  it attacks *you* — no damage required. First contact is about eyes and
  ears, not threat.
- **Shooting something gets its attention.** Hit an enemy from the back line
  and it will turn on you, its last attacker, even if someone else is
  closer. (Conveniently, that damage also makes you its top threat.)
- **Enemies help each other.** Attack one member of a group and its nearby
  friends join in — packs share fights, and reinforcements arrive already
  angry at whoever started it.
- **Alarms call in responders.** Some enemies raise the alarm when attacked,
  and the reinforcements that answer come hunting for the culprit.
- **Taunts jump the queue.** A deployed Decoy draws fire from enemies near
  it regardless of anyone's threat.
- **Only the serious enemies keep score.** Bosses, elites, and champions
  track threat. Most ordinary enemies don't — they simply go for whoever
  they saw first, whoever shot them last, or whoever's closest.
- **Cover doesn't erase threat.** If the top-threat player ducks behind a
  wall, they keep their spot on the list — the boss just finds something
  else to do (or someone else to shoot) until they reappear or their threat
  fades away.

## Rules of thumb

- **Tanking?** Keep hitting. Your position on the threat list only lasts as
  long as your recent damage — and take Super Tank if you mean it.
- **Bursting?** Big spikes steal aggro instantly. Be ready for the boss to
  turn around.
- **Sniping?** The rifle threat reduction and a Decoy together keep your
  profile low — but the shot that lands still makes you the last attacker.
- **Healing?** You're invisible to the threat system. Enemies will only come
  for you for the usual reasons — they saw you, or you shot them.
