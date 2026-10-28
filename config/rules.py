"""The single source of truth for documented lending policy."""
PRIVILEGES = {
    'restricted': {'loans': 1, 'days': 7, 'premium': False},
    'standard': {'loans': 3, 'days': 14, 'premium': False},
    'trusted': {'loans': 5, 'days': 21, 'premium': True},
}
RANK = {'restricted': 0, 'standard': 1, 'trusted': 2}
ON_TIME_REWARD = 2
LATE_PER_DAY = 5
MAX_LATE_PENALTY = 60
DAMAGE_PENALTY = 25
LOSS_PENALTY = 60
BLOCK_DAYS = 14
TRUST_BANDS = [
    (80, 'Excellent', 'Eligible for premium equipment', 'green'),
    (60, 'Warning', 'No premium equipment', 'yellow'),
    (40, 'Demoted', 'One loan at a time', 'orange'),
    (20, 'Temporary block', '14 days; restricted on expiry', 'red'),
    (0, 'Blacklist', 'Administrator review required', 'red'),
]
def band(score):
    return next(row for row in TRUST_BANDS if score >= row[0])

def privilege_for(score):
    return 'trusted' if score >= 80 else 'standard' if score >= 60 else 'restricted'
