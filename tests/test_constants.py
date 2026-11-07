"""Every constant and exponent in docs/04 is recomputed exactly by verify/constants.py."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import verify.constants as consts  # noqa: E402


def test_all_constant_checks_pass():
    consts.RESULTS.clear()
    assert consts.main() == 0
    assert len(consts.RESULTS) >= 30
