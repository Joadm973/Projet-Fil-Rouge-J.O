import pandas as pd
from pathlib import Path
import sys

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config import RAW_OLYMPICS_FILE


def load_raw_data() -> pd.DataFrame:
    """Charge le dataset brut des JO depuis le fichier CSV."""
    return pd.read_csv(RAW_OLYMPICS_FILE)
