from pathlib import Path
APP_NAME = 'LendHub'
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / 'data' / 'lendhub.db'
PREFERENCES_PATH = ROOT / 'data' / 'preferences.json'
DEFAULT_THEME = 'dark'
