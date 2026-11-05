"""The symbolic checks must all pass (they are exact algebra, see verify/identities.py)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import verify.identities as ident  # noqa: E402


def test_all_symbolic_identities_pass():
    ident.RESULTS.clear()
    assert ident.main() == 0
    assert all(ok for _, ok in ident.RESULTS)
    assert len(ident.RESULTS) >= 20


def test_witness_cubic_integral_is_nonzero_exactly():
    val = ident.witness_cubic_integral_exact()
    assert val != 0
    # It is a rational multiple of pi^3 (constant Fourier mode of a real trigonometric polynomial).
    import sympy as sp
    assert sp.simplify(val / sp.pi ** 3).is_rational
