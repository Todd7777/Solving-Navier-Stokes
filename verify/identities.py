#!/usr/bin/env python3
"""Exact symbolic verification of every pointwise identity used in docs/04-rigorously-proven-results.md.

Run:  python verify/identities.py        (exit status 0 iff every check passes)

Each check is an exact algebraic statement about generic smooth functions, verified with sympy.
Nothing here is numerical: a PASS is a proof of the identity (for the generic symbols used),
and the cubic-term witness in Section C is an exact Fourier-mode computation.
"""
from __future__ import annotations

import sys

import sympy as sp

RESULTS: list[tuple[str, bool]] = []


def check(name: str, expr) -> bool:
    ok = sp.simplify(sp.expand(expr)) == 0
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name)
    return ok


# ----------------------------------------------------------------------------
# A. Generic vector-calculus identities (Lemma 0.5 of docs/04)
# ----------------------------------------------------------------------------

def coords(n: int):
    return sp.symbols(f"x1:{n + 1}", real=True)


def field(name: str, X):
    return [sp.Function(f"{name}{i + 1}")(*X) for i in range(len(X))]


def div(u, X):
    return sum(sp.diff(u[j], X[j]) for j in range(len(X)))


def lap(f, X):
    return sum(sp.diff(f, x, 2) for x in X)


def advect(u, v, X):
    """(u . grad) v"""
    return [sum(u[j] * sp.diff(v[i], X[j]) for j in range(len(X))) for i in range(len(X))]


def dot(a, b):
    return sum(ai * bi for ai, bi in zip(a, b))


def grad_sq(u, X):
    """|grad u|^2 = sum_{i,k} (d_k u_i)^2"""
    return sum(sp.diff(u[i], X[k]) ** 2 for i in range(len(X)) for k in range(len(X)))


def curl3(u, X):
    return [sp.diff(u[2], X[1]) - sp.diff(u[1], X[2]),
            sp.diff(u[0], X[2]) - sp.diff(u[2], X[0]),
            sp.diff(u[1], X[0]) - sp.diff(u[0], X[1])]


def curl2(u, X):
    return sp.diff(u[1], X[0]) - sp.diff(u[0], X[1])


def section_A():
    for n in (2, 3):
        X = coords(n)
        u = field("u", X)
        p = sp.Function("p")(*X)
        usq2 = dot(u, u) / 2
        # (1) u.((u.grad)u) = div(u |u|^2/2) - (div u)|u|^2/2
        lhs = dot(u, advect(u, u, X))
        rhs = div([ui * usq2 for ui in u], X) - div(u, X) * usq2
        check(f"[{n}D] identity 1: u.((u.grad)u) = div(u|u|^2/2) - (div u)|u|^2/2", lhs - rhs)
        # (2) u.grad p = div(p u) - p div u
        lhs = sum(u[i] * sp.diff(p, X[i]) for i in range(n))
        rhs = div([p * ui for ui in u], X) - p * div(u, X)
        check(f"[{n}D] identity 2: u.grad p = div(p u) - p div u", lhs - rhs)
        # (3) u.Lap u = d_k(u_i d_k u_i) - |grad u|^2
        lhs = sum(u[i] * lap(u[i], X) for i in range(n))
        rhs = sum(sp.diff(sum(u[i] * sp.diff(u[i], X[k]) for i in range(n)), X[k]) for k in range(n)) - grad_sq(u, X)
        check(f"[{n}D] identity 3: u.Lap u = d_k(u_i d_k u_i) - |grad u|^2", lhs - rhs)
        # (4) ((u.grad)u).Lap u = -d_k u_j d_j u_i d_k u_i + d_k(u_j d_j u_i d_k u_i) - (1/2) d_j(u_j|grad u|^2) + (1/2)(div u)|grad u|^2
        lhs = dot(advect(u, u, X), [lap(ui, X) for ui in u])
        cubic = sum(sp.diff(u[j], X[k]) * sp.diff(u[i], X[j]) * sp.diff(u[i], X[k])
                    for i in range(n) for j in range(n) for k in range(n))
        divterm = sum(sp.diff(sum(u[j] * sp.diff(u[i], X[j]) * sp.diff(u[i], X[k]) for i in range(n) for j in range(n)), X[k])
                      for k in range(n))
        transport = sum(sp.diff(u[j] * grad_sq(u, X), X[j]) for j in range(n)) / 2
        rhs = -cubic + divterm - transport + div(u, X) * grad_sq(u, X) / 2
        check(f"[{n}D] identity 4: ((u.grad)u).Lap u = -cubic + divergence terms", lhs - rhs)
        # (5) curl of the advection term
        if n == 3:
            w = curl3(u, X)
            lhs = curl3(advect(u, u, X), X)
            rhs = [a - b + div(u, X) * wi for a, b, wi in zip(advect(u, w, X), advect(w, u, X), w)]
            for i in range(3):
                check(f"[3D] identity 5 (component {i + 1}): curl((u.grad)u) = (u.grad)w - (w.grad)u + (div u) w", lhs[i] - rhs[i])
        else:
            w = curl2(u, X)
            lhs = curl2(advect(u, u, X), X)
            rhs = sum(u[j] * sp.diff(w, X[j]) for j in range(2)) + div(u, X) * w
            check("[2D] identity 5: curl((u.grad)u) = (u.grad)w + (div u) w", lhs - rhs)
    # Lemma 0.4 pointwise versions: |grad u|^2 = |curl u|^2 + (div u)^2 + divergence terms
    X = coords(2)
    u = field("u", X)
    detJ = sp.diff(u[0], X[0]) * sp.diff(u[1], X[1]) - sp.diff(u[1], X[0]) * sp.diff(u[0], X[1])
    divform = sp.diff(u[0] * sp.diff(u[1], X[1]), X[0]) - sp.diff(u[0] * sp.diff(u[1], X[0]), X[1])
    check("[2D] det(grad u) is a divergence: det = d_1(u_1 d_2 u_2) - d_2(u_1 d_1 u_2)", detJ - divform)
    check("[2D] |grad u|^2 = w^2 + (div u)^2 - 2 det(grad u)", grad_sq(u, X) - curl2(u, X) ** 2 - div(u, X) ** 2 + 2 * detJ)
    X = coords(3)
    u = field("u", X)
    w = curl3(u, X)
    divterms = sum(sp.diff(sum(u[j] * sp.diff(u[i], X[j]) for j in range(3)), X[i]) for i in range(3)) \
        - sum(sp.diff(u[j] * div(u, X), X[j]) for j in range(3))
    check("[3D] |grad u|^2 = |curl u|^2 + (div u)^2 + d_i(u_j d_j u_i) - d_j(u_j div u)",
          grad_sq(u, X) - dot(w, w) - div(u, X) ** 2 - divterms)


# ----------------------------------------------------------------------------
# B. Scaling symmetry (Theorem 2) and the 2D Taylor-Green exact solution
# ----------------------------------------------------------------------------

def residual(u, p, f, X, t, nu):
    """Residual of  d_t u + (u.grad)u - nu Lap u + grad p - f  (zero iff Navier-Stokes holds)."""
    adv = advect(u, u, X)
    return [sp.diff(u[i], t) + adv[i] - nu * lap(u[i], X) + sp.diff(p, X[i]) - f[i] for i in range(len(X))]


def section_B():
    X = coords(3)
    t, lam = sp.symbols("t lambda", positive=True)
    nu = sp.symbols("nu", positive=True)
    u = [sp.Function(f"u{i + 1}")(*X, t) for i in range(3)]
    f = [sp.Function(f"f{i + 1}")(*X, t) for i in range(3)]
    p = sp.Function("p")(*X, t)
    scale = {X[0]: lam * X[0], X[1]: lam * X[1], X[2]: lam * X[2], t: lam ** 2 * t}
    u_l = [lam * ui.subs(scale, simultaneous=True) for ui in u]
    f_l = [lam ** 3 * fi.subs(scale, simultaneous=True) for fi in f]
    p_l = lam ** 2 * p.subs(scale, simultaneous=True)
    R = residual(u, p, f, X, t, nu)
    R_l = residual(u_l, p_l, f_l, X, t, nu)
    for i in range(3):
        diff_expr = (R_l[i] - lam ** 3 * R[i].subs(scale, simultaneous=True)).doit()
        check(f"[3D] scaling: residual(u_lam,p_lam,f_lam)(x,t) = lam^3 residual(u,p,f)(lam x, lam^2 t), component {i + 1}",
              diff_expr)
    d_l = div(u_l, X).doit() - lam ** 2 * div(u, X).subs(scale, simultaneous=True).doit()
    check("[3D] scaling: div(u_lam)(x,t) = lam^2 (div u)(lam x, lam^2 t)", d_l)

    # 2D Taylor-Green vortex is an exact solution with p = (cos 2x + cos 2y)/4 e^{-4 nu t}
    X2 = coords(2)
    x, y = X2
    uTG = [sp.sin(x) * sp.cos(y) * sp.exp(-2 * nu * t), -sp.cos(x) * sp.sin(y) * sp.exp(-2 * nu * t)]
    pTG = (sp.cos(2 * x) + sp.cos(2 * y)) / 4 * sp.exp(-4 * nu * t)
    RTG = residual(uTG, pTG, [0, 0], X2, t, nu)
    check("[2D] Taylor-Green: Navier-Stokes residual vanishes (component 1)", RTG[0])
    check("[2D] Taylor-Green: Navier-Stokes residual vanishes (component 2)", RTG[1])
    check("[2D] Taylor-Green: divergence free", div(uTG, X2))
    wTG = curl2(uTG, X2)
    check("[2D] Taylor-Green: vorticity = 2 sin x sin y e^{-2 nu t}", wTG - 2 * sp.sin(x) * sp.sin(y) * sp.exp(-2 * nu * t))


# ----------------------------------------------------------------------------
# C. Exact evaluation of the cubic (vortex-stretching) integral for trigonometric fields
# ----------------------------------------------------------------------------
# A real trigonometric polynomial on the 2*pi-torus is a Laurent polynomial in E_j = exp(i x_j).
# d/dx_j acts as  i * E_j * d/dE_j.  The integral over the torus equals (2*pi)^n times the constant term.

E = sp.symbols("E1 E2 E3")


def d(expr, j):
    return sp.I * E[j] * sp.diff(expr, E[j])


def cos_mode(k):
    m = sp.prod([E[j] ** int(k[j]) for j in range(3)])
    return (m + 1 / m) / 2


def sin_mode(k):
    m = sp.prod([E[j] ** int(k[j]) for j in range(3)])
    return (m - 1 / m) / (2 * sp.I)


def laurent_constant_term(expr, N: int = 12):
    P = sp.Poly(sp.expand(expr * (E[0] * E[1] * E[2]) ** N), *E)
    return sp.nsimplify(P.coeff_monomial(E[0] ** N * E[1] ** N * E[2] ** N))


def torus_integral(expr, N: int = 12):
    """Exact integral over [0,2pi]^3 of a Laurent polynomial in E_j = exp(i x_j)."""
    return sp.simplify((2 * sp.pi) ** 3 * laurent_constant_term(expr, N))


def cubic_density(u):
    """T = d_k u_j  d_j u_i  d_k u_i   (indices 0..2)"""
    M = [[d(u[i], j) for j in range(3)] for i in range(3)]  # M[i][j] = d_j u_i
    return sp.expand(sum(M[j][k] * M[i][j] * M[i][k] for i in range(3) for j in range(3) for k in range(3)))


def curl_laurent(A):
    return [d(A[2], 1) - d(A[1], 2), d(A[0], 2) - d(A[2], 0), d(A[1], 0) - d(A[0], 1)]


# The witness field: u = curl A with
#   A1 = -cos(2x1 + 2x2 + 2x3) + sin(2x2 + x3)
#   A2 = -2 cos(x1 - 2x3)      - 2 sin(-x1 + 2x2 - 2x3)
#   A3 = -2 cos(-x1 + 2x2)     + 2 sin(2x1 - 2x2)
# (found by a random search over small integer modes; the exact value below is what matters).
WITNESS_TERMS = [
    [(-1, (2, 2, 2), "cos"), (1, (0, 2, 1), "sin")],
    [(-2, (1, 0, -2), "cos"), (-2, (-1, 2, -2), "sin")],
    [(-2, (-1, 2, 0), "cos"), (2, (2, -2, 0), "sin")],
]


def _laurent_potential():
    out = []
    for terms in WITNESS_TERMS:
        out.append(sum(c * (cos_mode(k) if f == "cos" else sin_mode(k)) for c, k, f in terms))
    return out


WITNESS_A = _laurent_potential()


def witness_field_numpy_expression():
    """The same witness velocity field as sympy expressions in real coordinates (for numerics/ cross-check)."""
    X = coords(3)
    A = []
    for terms in WITNESS_TERMS:
        a = 0
        for c, k, f in terms:
            ph = k[0] * X[0] + k[1] * X[1] + k[2] * X[2]
            a += c * (sp.cos(ph) if f == "cos" else sp.sin(ph))
        A.append(a)
    return X, curl3(A, X)


def witness_cubic_integral_exact():
    u = curl_laurent(WITNESS_A)
    return torus_integral(cubic_density(u))


def section_C():
    u = curl_laurent(WITNESS_A)
    divu = sp.expand(d(u[0], 0) + d(u[1], 1) + d(u[2], 2))
    check("[3D] witness field u = curl A is exactly divergence free", divu)
    val = witness_cubic_integral_exact()
    nonzero = val != 0
    RESULTS.append(("[3D] witness cubic integral is NON-zero (vortex stretching does not vanish)", nonzero))
    print(("PASS " if nonzero else "FAIL ") + f"[3D] cubic integral  int d_k u_j d_j u_i d_k u_i  = {val}  (exact)")
    # Consistency with Theorem 3 in 2D: for a field independent of x3 with u3 = 0 the integral must vanish.
    A2 = [0, 0, sin_mode((1, 0, 0)) * cos_mode((0, 1, 0)) + cos_mode((1, 1, 0)) + sin_mode((0, 2, 0))]
    u2 = curl_laurent(A2)
    check("[2D] planar field u = curl(0,0,psi): cubic integral vanishes exactly (Theorem 3)", torus_integral(cubic_density(u2)))
    # Lemma 0.4 integrated: ||grad u||^2 = ||curl u||^2 for the divergence-free witness
    M = [[d(u[i], j) for j in range(3)] for i in range(3)]
    gradsq = sum(M[i][j] ** 2 for i in range(3) for j in range(3))
    w = curl_laurent(u)
    check("[3D] witness: int |grad u|^2 = int |curl u|^2 (Lemma 0.4, exact)", torus_integral(gradsq) - torus_integral(sum(wi ** 2 for wi in w)))


def main() -> int:
    section_A()
    section_B()
    section_C()
    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    if failed:
        print("FAILED:", *failed, sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
