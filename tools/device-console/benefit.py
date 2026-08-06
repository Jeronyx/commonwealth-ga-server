# Single source of stat polarity for the console and its reference pages.
#
# A minus sign is the CALC METHOD, not a judgement: -15% Power Pool Cost is a gain,
# -5 Protection on the enemy is a gain, -35% GroundSpeed on yourself is a cost.
# Benefit is derived, never hand-labelled per line:
#
#   want(prop, pv)              -> which direction the RECIPIENT of the stat change wants
#   classify(prop, neg, pv, side) -> 'good' / 'bad' / '' as seen by the BUILD OWNER,
#                                    flipped when the effect lands on an enemy
#
# '' means unclassified. The reference page flags those loudly instead of guessing.

# The recipient wants LESS of these. Two families, kept separate because the bench needs
# the distinction: OWNER_COST stats belong to whoever holds the device (a cooldown is yours
# even on a chip with no Self: prefix), INFLICTION stats land on whoever is hit.
OWNER_COST = {
    4, 53, 279,          # cooldown / refire / deploy time
    203,                 # cooldown modifier
    242, 322,            # power cost / block cost per sec
    349,                 # remote activation time
    357,                 # morale required
    391,                 # pet deploy time
    137,                 # falling damage
    66,                  # Effect GroundSpeed Modifier - only ever scales a slow on you
}
INFLICTION = {
    316,                 # additional damage taken
    60, 295,             # knockback / pushback magnitude
    166, 167, 169, 170, 171, 172, 254, 338, 305,   # CC props (stun/slow/sleep/KB/root/...)
}
LOWER_BETTER = OWNER_COST | INFLICTION

# The recipient wants MORE of these.
HIGHER_BETTER = {
    49, 51, 70, 211,                     # speed, health, air speed
    113, 114, 153, 207, 256, 356,        # accuracy, range, projectile speed
    155, 156, 157, 158, 159, 160, 163, 168, 217, 218, 219, 233, 235, 266, 324, 328, 371,  # protections
    208, 210, 330, 260,                  # effect lifetime, heal received, healing output, repair
    212, 214, 215, 232, 321, 336, 350,   # damage modifiers
    65, 361, 372, 373, 374, 375, 385, 388, 389,    # more damage modifiers / output / vs-type
    243, 244, 255, 285,                  # power restore / regen / pool
    339, 355, 360, 366, 381, 382, 383,   # pet & deployable stats
    352,                                 # AOE radius
    353,                                 # MakeVisible fade rate - restealth faster
    376,                                 # effect potency (pv decides the rest)
    386,                                 # shield strength
    390, 412,                            # max HP
}

# Deliberately unclassified: benefit depends on the build's intent, so the pages flag
# these for review instead of guessing.
#   421 Threat Modifier - Assault Melee III ADDS threat (a tank taunt perk) while other
#       skills shed it; more threat helps a tank and hurts everyone else.
UNKNOWN_PROPS = {420, 421}

# Effect categories (property_value_id scopes) that are PENALTIES on their carrier -
# scaling them DOWN is the benefit. Every other scoped category a potency/duration
# modifier reaches (debuffs you inflict, buffs you grant) is wanted bigger.
CAT_WANT_LESS = {
    1360,   # Movement Penalty (the minigun move penalty Super Destroyer removes)
    1452,   # Shield Movement Penalty (Super Tank)
    774,    # Stim Resistance (the post-stim debuff on you)
    1589,   # Regen Damage Penalty
}
# Scoped categories with no established polarity - same ambiguity as prop 421.
CAT_UNKNOWN = {1601}    # Threat Modifier category


def want(prop, pv=0):
    """'less' / 'more' / None - the direction the RECIPIENT wants. None = unclassified."""
    if pv:
        if pv in CAT_UNKNOWN:
            return None
        if pv in CAT_WANT_LESS:
            return 'less'
        return 'more'
    if prop in UNKNOWN_PROPS:
        return None
    if prop in LOWER_BETTER:
        return 'less'
    if prop in HIGHER_BETTER:
        return 'more'
    return None


def classify(prop, neg, pv=0, side=''):
    """'good' / 'bad' / '' for the BUILD OWNER.
    side: '' / 'you' / 'allies' apply directly; 'enemies' / 'target' flip."""
    w = want(prop, pv)
    if w is None:
        return ''
    helps = (('less' if neg else 'more') == w)
    if side in ('enemies', 'target'):
        helps = not helps
    return 'good' if helps else 'bad'


def tables():
    """JSON-safe copy for injection as window.__POLARITY__ (bench.js / builder.js).
    'ownerCost' is what the bench's owner-perspective `lower` flag wants; 'lower' is the
    full recipient-perspective set that classify() uses."""
    return {'lower': sorted(LOWER_BETTER), 'higher': sorted(HIGHER_BETTER),
            'ownerCost': sorted(OWNER_COST),
            'unknownProps': sorted(UNKNOWN_PROPS),
            'catWantLess': sorted(CAT_WANT_LESS), 'catUnknown': sorted(CAT_UNKNOWN)}
