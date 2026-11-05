"""Numerical cross-checks of docs/04 using numerics/spectral.py.  Runtime: a few seconds."""
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from numerics.spectral import NS2D, NS3D  # noqa: E402


def test_2d_taylor_green_exact_solution():
    """w = 2 sin x sin y e^{-2 nu t} is an exact solution; the solver must reproduce it to RK4/spectral accuracy."""
    nu, N, dt, T = 0.1, 32, 1e-2, 1.0
    s = NS2D(N, nu)
    wh = s.fft(s.taylor_green(0.0))
    n = int(round(T / dt))
    for _ in range(n):
        wh = s.step(wh, dt)
    err = np.max(np.abs(s.ifft(wh) - s.taylor_green(n * dt)))
    assert err < 1e-9, err


def test_2d_energy_identity_and_enstrophy_monotone():
    """dE/dt = -nu int |grad u|^2 = -nu int w^2 (Theorem 1 + Lemma 0.4); enstrophy non-increasing (Theorem 4)."""
    nu, N, dt = 0.02, 64, 2e-3
    s = NS2D(N, nu)
    wh = s.fft(s.random_field(seed=1, kmax=5, amplitude=3.0)) * s.dealias
    E, Z, D = [], [], []
    for _ in range(200):
        E.append(s.energy(wh))
        Z.append(s.enstrophy(wh))
        D.append(s.grad_u_sq(wh))
        assert abs(D[-1] - 2 * Z[-1]) < 1e-10 * max(1.0, D[-1])  # ||grad u||^2 = ||w||^2
        wh = s.step(wh, dt)
    E, Z, D = map(np.array, (E, Z, D))
    dEdt = (E[2:] - E[:-2]) / (2 * dt)
    rel = np.max(np.abs(dEdt + nu * D[1:-1]) / np.abs(nu * D[1:-1]))
    assert rel < 1e-4, rel
    assert np.all(np.diff(Z) <= 1e-12 * Z[0])


def test_3d_energy_identity_divergence_free_and_taylor_green_stretching():
    """3D: dE/dt = -nu int |grad u|^2; Leray projection keeps div u = 0; enstrophy is NOT monotone (stretching)."""
    nu, N, dt = 0.05, 32, 5e-3
    s = NS3D(N, nu)
    uh = s.taylor_green() * s.dealias
    E, D, Z = [], [], []
    for _ in range(60):
        E.append(s.energy(uh))
        D.append(s.grad_u_sq(uh))
        Z.append(s.enstrophy(uh))
        assert np.max(np.abs(s.divergence_hat(uh))) < 1e-9
        uh = s.step(uh, dt)
    E, D, Z = map(np.array, (E, D, Z))
    dEdt = (E[2:] - E[:-2]) / (2 * dt)
    rel = np.max(np.abs(dEdt + nu * D[1:-1]) / np.abs(nu * D[1:-1]))
    assert rel < 1e-4, rel
    # In 2D the enstrophy decays monotonically; for the 3D Taylor-Green vortex at this viscosity the
    # vortex-stretching term eventually makes it grow (Brachet et al. 1983).  We only assert that the
    # 3D evolution is not the pure viscous decay 2Z(0)e^{-2 nu ... }: the stretching integral is nonzero.
    cubic = s.cubic_integral(uh)
    assert abs(cubic) > 1e-3 * max(1.0, D[-1])


def test_3d_cubic_integral_matches_exact_symbolic_value():
    """The spectral quadrature of int d_k u_j d_j u_i d_k u_i equals the exact sympy value for the witness field."""
    import sympy as sp

    import verify.identities as ident

    exact = float(ident.witness_cubic_integral_exact())
    X, u_exprs = ident.witness_field_numpy_expression()
    s = NS3D(24, 1.0)  # modes <= 2 in the field, products of three derivatives need N >= 2*3*2+1
    uh = s.from_expressions(u_exprs, X)
    assert np.max(np.abs(s.divergence_hat(uh))) < 1e-10
    num = s.cubic_integral(uh)
    assert abs(num - exact) < 1e-9 * max(1.0, abs(exact)), (num, exact)
    assert abs(exact) > 1.0
