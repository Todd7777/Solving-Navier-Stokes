#!/usr/bin/env python3
"""Exact verification of every constant, exponent and elementary inequality step in docs/04.

Run:  python verify/constants.py        (exit status 0 iff every check passes)

verify/identities.py checks the pointwise vector-calculus identities. This script checks the
*bookkeeping* that sits on top of them: each Young's-inequality step (computed as an exact supremum),
each Groenwall/ODE solution, every scaling exponent (both by exponent arithmetic and, for the
energy, by an explicit Gaussian integral), and the exponent relations in the Serrin-type criterion.
"""
from __future__ import annotations

import sys

import sympy as sp

RESULTS: list[tuple[str, bool]] = []


def check(name: str, ok) -> bool:
    ok = bool(ok)
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name)
    return ok


def is_zero(expr) -> bool:
    return sp.simplify(sp.powsimp(sp.expand(expr), force=True)) == 0


def sup_over_positive(f, Z):
    """Exact sup over Z > 0 of f(Z), where f(0) = 0, f -> -oo and f has one positive critical point."""
    crit = [c for c in sp.solve(sp.Eq(sp.diff(f, Z), 0), Z) if c.is_positive]
    assert len(crit) == 1, crit
    second = sp.simplify(sp.diff(f, Z, 2).subs(Z, crit[0]))
    assert second.is_negative, second
    return sp.simplify(f.subs(Z, crit[0]))


nu, C, C3, y, y0, t, U, G, W, Z, P, lam = sp.symbols("nu C C3 y y0 t U G W Z P lambda", positive=True)


def theorem5():
    # 1/2 y' + nu Z^2 <= C3 y^(3/4) Z^(3/2),  Z = ||Lap u||
    S = sup_over_positive(C3 * y ** sp.Rational(3, 4) * Z ** sp.Rational(3, 2) - nu / 2 * Z ** 2, Z)
    check("Thm 5: sup_Z [C3 y^(3/4) Z^(3/2) - (nu/2) Z^2] = 27 C3^4 y^3 / (32 nu^3)",
          is_zero(S - sp.Rational(27, 32) * C3 ** 4 * y ** 3 / nu ** 3))
    kappa = 2 * sp.Rational(27, 32) * C3 ** 4
    check("Thm 5: kappa = 2 * 27/32 C3^4 = 27 C3^4 / 16", is_zero(kappa - sp.Rational(27, 16) * C3 ** 4))
    Y = y0 / sp.sqrt(1 - 2 * kappa / nu ** 3 * y0 ** 2 * t)
    check("Thm 5: y(t) = y0 / sqrt(1 - 2 kappa nu^-3 y0^2 t) solves y' = kappa nu^-3 y^3",
          is_zero(sp.diff(Y, t) - kappa / nu ** 3 * Y ** 3))
    Tstar = nu ** 3 / (2 * kappa * y0 ** 2)
    check("Thm 5: the bound blows up exactly at T* = nu^3 / (2 kappa y0^2)",
          is_zero((1 - 2 * kappa / nu ** 3 * y0 ** 2 * t).subs(t, Tstar)))
    # T* is consistent with scaling: ||grad u_lam||^2 = lam y0 in 3D, so T*(lam) = T* / lam^2
    check("Thm 5: T*(u_lambda) = T*(u) / lambda^2 (since ||grad u_lambda||^2 = lambda ||grad u||^2)",
          is_zero(Tstar.subs(y0, lam * y0) - Tstar / lam ** 2))


def theorem4():
    # 1/2 d/dt ||grad w||^2 + nu Z^2 <= B Z^(3/2),  B = C^2 (U G)^(1/2) W^(1/2),  Z = ||Lap w||, W = ||grad w||
    B = C ** 2 * sp.sqrt(U * G) * sp.sqrt(W)
    S = sup_over_positive(B * Z ** sp.Rational(3, 2) - nu * Z ** 2, Z)
    check("Thm 4(3): sup_Z [B Z^(3/2) - nu Z^2] = 27 B^4 / (256 nu^3) = (27 C^8/256) nu^-3 (U G)^2 W^2",
          is_zero(S - sp.Rational(27, 256) * C ** 8 * (U * G) ** 2 * W ** 2 / nu ** 3))


def theorem6():
    # If Z >= G^2/U (interpolation ||grad u||^2 <= ||u|| ||Lap u||) then G^(3/2) Z^(3/2) <= (U G)^(1/2) Z^2.
    s = sp.symbols("s", nonnegative=True)
    Zs = G ** 2 / U * (1 + s)
    ratio = sp.simplify((sp.sqrt(U * G) * Zs ** 2) / (G ** sp.Rational(3, 2) * Zs ** sp.Rational(3, 2)))
    check("Thm 6: (U G)^(1/2) Z^2 / (G^(3/2) Z^(3/2)) = sqrt(1+s) >= 1 when Z = (G^2/U)(1+s)",
          is_zero(ratio - sp.sqrt(1 + s)))
    check("Thm 6: the smallness quantity ||u|| ||grad u|| is scale invariant in 3D (exponents -1/2 + 1/2)",
          sp.Rational(-1, 2) + sp.Rational(1, 2) == 0)


def theorem7():
    a, K = sp.symbols("a K", positive=True)
    q = sp.symbols("q", positive=True)
    # Hoelder: 1/q + 1/r + 1/2 = 1 ; Gagliardo-Nirenberg exponent for ||g||_{L^r} <= ||g||^(1-a) ||grad g||^a on T^3
    r = 1 / (sp.Rational(1, 2) - 1 / q)
    s_needed = 3 * (sp.Rational(1, 2) - 1 / r)
    check("Thm 7: Sobolev order needed for L^r, 1/r = 1/2 - 1/q, is s = 3/q", is_zero(s_needed - 3 / q))
    # Young: sup_Z [K Z^(1+a) - nu Z^2] is homogeneous of degree 2/(1-a) in K
    for aval in (sp.Rational(0), sp.Rational(1, 4), sp.Rational(1, 2), sp.Rational(3, 4)):
        S = sup_over_positive(K * Z ** (1 + aval) - nu * Z ** 2, Z) if aval != 0 else sp.simplify(K ** 2 / (4 * nu))
        deg = sp.simplify(sp.diff(sp.log(S), K) * K)
        check(f"Thm 7: sup_Z [K Z^(1+a) - nu Z^2] has degree 2/(1-a) in K (a = {aval})", is_zero(deg - 2 / (1 - aval)))
    pexp = sp.simplify(2 / (1 - 3 / q))
    check("Thm 7: 2/(1-a) with a = 3/q equals p = 2q/(q-3)", is_zero(pexp - 2 * q / (q - 3)))
    p = 2 * q / (q - 3)
    check("Thm 7: p = 2q/(q-3) satisfies 2/p + 3/q = 1", is_zero(2 / p + 3 / q - 1))
    # scaling of int_0^T ||u_lam||_{L^q}^p dt :  lam^(p(1-3/q)) * lam^(-2)
    pp = sp.symbols("p", positive=True)
    expo = pp * (1 - 3 / q) - 2
    check("Thm 7: the Serrin norm is scale invariant iff 2/p + 3/q = 1",
          is_zero(sp.solve(sp.Eq(expo, 0), pp)[0] - 2 * q / (q - 3)))
    check("Thm 7: energy class L^inf L^2 has 2/p + 3/q = 3/2", sp.Rational(0) + sp.Rational(3, 2) == sp.Rational(3, 2))
    check("Thm 7: energy class L^2 L^6 has 2/p + 3/q = 3/2", sp.Rational(2, 2) + sp.Rational(3, 6) == sp.Rational(3, 2))


def theorem8():
    # 1/2 y' + nu Z^2 <= C^2 sqrt(y) P Z,  P = ||Lambda^(5/4) u||, Z = ||Lambda^(9/4) u||
    S = sup_over_positive(C ** 2 * sp.sqrt(y) * P * Z - nu / 2 * Z ** 2, Z)
    check("Thm 8: sup_Z [C^2 sqrt(y) P Z - (nu/2) Z^2] = C^4 y P^2 / (2 nu)", is_zero(S - C ** 4 * y * P ** 2 / (2 * nu)))
    # => y' <= (C^4/nu) P^2 y ;  int_0^oo P^2 <= ||u0||^2/(2 nu)  =>  exponent C^4 ||u0||^2 / (2 nu^2)
    U0 = sp.symbols("U0", positive=True)
    exponent = (C ** 4 / nu) * U0 ** 2 / (2 * nu)
    check("Thm 8: Groenwall exponent = C^4 ||u0||^2 / (2 nu^2)", is_zero(exponent - C ** 4 * U0 ** 2 / (2 * nu ** 2)))
    # hyperviscous scaling u_lam = lam^(2 alpha - 1) u(lam x, lam^(2 alpha) t): every term scales like lam^(4 alpha - 1)
    al = sp.symbols("alpha", positive=True)
    beta, gam = 2 * al - 1, 2 * al
    terms = {"d_t u": beta + gam, "(u.grad)u": 2 * beta + 1, "Lambda^(2 alpha) u": beta + 2 * al, "grad p (p ~ lam^(2 beta))": 2 * beta + 1}
    check("Thm 8: all terms of the hyperviscous equation scale like lambda^(4 alpha - 1)",
          all(is_zero(e - (4 * al - 1)) for e in terms.values()))
    check("Thm 8: ||u_lam||_{L^2(R^3)} = lam^(2 alpha - 5/2) ||u||, critical exactly at alpha = 5/4",
          is_zero(beta - sp.Rational(3, 2) - (2 * al - sp.Rational(5, 2))) and sp.solve(2 * al - sp.Rational(5, 2), al) == [sp.Rational(5, 4)])
    # interpolation exponents used: 7/4 = (5/4 + 9/4)/2 ; Sobolev L^4 in 3D needs s = 3/4
    check("Thm 8: 7/4 is the midpoint of 5/4 and 9/4", sp.Rational(7, 4) == (sp.Rational(5, 4) + sp.Rational(9, 4)) / 2)
    check("Thm 8: L^4(T^3) embedding needs s = 3(1/2 - 1/4) = 3/4", 3 * (sp.Rational(1, 2) - sp.Rational(1, 4)) == sp.Rational(3, 4))


def scaling():
    # exponent of || d^k u_lam(t) ||_{L^q(R^n)} for u_lam = lam u(lam x, lam^2 t):  1 + k - n/q
    def e(k, q, n):
        return 1 + k - sp.Integer(n) / q
    table = {
        "3D ||u||_{L^2}": (e(0, 2, 3), sp.Rational(-1, 2)),
        "3D ||grad u||_{L^2}": (e(1, 2, 3), sp.Rational(1, 2)),
        "3D ||u||_{L^3}": (e(0, 3, 3), 0),
        "2D ||u||_{L^2}": (e(0, 2, 2), 0),
        "2D ||grad u||_{L^2}": (e(1, 2, 2), 1),
    }
    for name, (got, want) in table.items():
        check(f"scaling table: {name} ~ lambda^{want}", is_zero(got - want))
    q = sp.symbols("q", positive=True)
    check("scaling table: 3D ||u||_{L^q} ~ lambda^(1 - 3/q)", is_zero(e(0, q, 3) - (1 - 3 / q)))
    # Theorem 5': || Lambda^s u_lam ||_{L^p_t L^2_x} = lam^(s - 1/2 - 2/p)
    s, p = sp.symbols("s p", positive=True)
    check("Thm 5': exponent of L^p_t dot-H^s_x is s - 1/2 - 2/p",
          is_zero((1 + s - sp.Rational(3, 2)) - 2 / p - (s - sp.Rational(1, 2) - 2 / p)))
    check("Thm 5': energy-level norms (s,p) = (0,oo) and (1,2) both have exponent -1/2",
          sp.limit(0 - sp.Rational(1, 2) - 2 / p, p, sp.oo) == sp.Rational(-1, 2) and (1 - sp.Rational(1, 2) - 1) == sp.Rational(-1, 2))
    # explicit integral: u(x) = (1,0,0) exp(-|x|^2) on R^3;  ||u_lam||_{L^2}^2 = lam^(-1) ||u||_{L^2}^2
    x1, x2, x3 = sp.symbols("x1 x2 x3", real=True)
    dens = lambda L: (L * sp.exp(-(L ** 2) * (x1 ** 2 + x2 ** 2 + x3 ** 2))) ** 2
    I = lambda L: sp.integrate(dens(L), (x1, -sp.oo, sp.oo), (x2, -sp.oo, sp.oo), (x3, -sp.oo, sp.oo))
    check("scaling (explicit Gaussian integral): ||u_lam||_{L^2(R^3)}^2 = lambda^-1 ||u||_{L^2}^2",
          is_zero(I(lam) - I(1) / lam))


def sobolev_exponents():
    # Lemma 0.3: 1/q = 1/2 - s/n
    for n, q, s in ((3, 3, sp.Rational(1, 2)), (3, 4, sp.Rational(3, 4)), (3, 6, 1), (2, 4, sp.Rational(1, 2))):
        check(f"Lemma 0.3: n={n}, q={q} needs s={s}", sp.Rational(1, q) == sp.Rational(1, 2) - sp.Integer(s) / n if isinstance(s, int) else sp.Rational(1, q) == sp.Rational(1, 2) - s / n)


def main() -> int:
    theorem4()
    theorem5()
    theorem6()
    theorem7()
    theorem8()
    scaling()
    sobolev_exponents()
    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    if failed:
        print("FAILED:", *failed, sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
