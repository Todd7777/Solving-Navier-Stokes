# What is rigorously known about the 3D Navier–Stokes equations

This document collects the results that are actually **theorems**, and proves the core
a priori estimates in full. Everything in Sections 1–8 is proved here from a short list of
standard lemmas (Section 0). Section 9 states the deeper theorems precisely, with references,
but does not reprove them. Nothing in this document resolves Clay statements (A) or (B);
see `05-why-A-and-B-are-open.md` for why the estimates below cannot be pushed further.

All vector-calculus identities used below are also checked symbolically in
`verify/identities.py` (run `python verify/identities.py`).

## 0. Setting, notation, and the lemmas we take as given

We work on the periodic box $\mathbb{T}^n = (\mathbb{R}/2\pi\mathbb{Z})^n$, $n \in \{2,3\}$,
with viscosity $\nu > 0$ and, unless stated otherwise, no external force. The incompressible
Navier–Stokes system is

$$\partial_t u + (u\cdot\nabla)u = \nu\Delta u - \nabla p, \qquad \nabla\cdot u = 0, \qquad u(\cdot,0)=u_0 .$$

A *smooth solution on $[0,T)$* means $u, p \in C^\infty(\mathbb{T}^n\times[0,T))$ satisfying the
system pointwise. The periodic setting removes all questions of decay at infinity and lets every
integration by parts go through without boundary terms; the same estimates hold on $\mathbb{R}^n$
for Schwartz-class data, with the same constants.

We assume $\int_{\mathbb{T}^n} u_0 = 0$. The mean $\int u$ is conserved (integrate the equation),
so $u(t)$ stays mean-free; the general case reduces to this by a Galilean change of frame.

Notation: $\|\cdot\|$ is the $L^2(\mathbb{T}^n)$ norm, $\langle f,g\rangle = \int f\cdot g$,
$\Lambda = (-\Delta)^{1/2}$ acts on Fourier coefficients by $\widehat{\Lambda^s g}(k) = |k|^s \hat g(k)$,
and $\|\Lambda^s g\|^2 = \sum_k |k|^{2s}|\hat g(k)|^2$ (Parseval, up to the normalising constant).
Repeated indices are summed. $\omega = \nabla\times u$ in 3D, and $\omega = \partial_1 u_2 - \partial_2 u_1$ in 2D.

**Lemma 0.1 (integration by parts).** For smooth periodic $g, h$: $\int \partial_j g\, h = -\int g\, \partial_j h$.
*Proof.* $\int \partial_j(gh) = 0$ by periodicity. $\square$

**Lemma 0.2 (interpolation).** For $a \le s \le b$ and $s = \theta a + (1-\theta) b$:
$\|\Lambda^s g\| \le \|\Lambda^a g\|^{\theta}\|\Lambda^b g\|^{1-\theta}$.
*Proof.* Hölder's inequality for sums with exponents $1/\theta$ and $1/(1-\theta)$:
$\sum_k |k|^{2s}|\hat g_k|^2 = \sum_k \big(|k|^{2a}|\hat g_k|^2\big)^{\theta}\big(|k|^{2b}|\hat g_k|^2\big)^{1-\theta}
\le \big(\sum_k |k|^{2a}|\hat g_k|^2\big)^{\theta}\big(\sum_k |k|^{2b}|\hat g_k|^2\big)^{1-\theta}$. $\square$

Two consequences used constantly: $\|\nabla g\|^2 \le \|g\|\,\|\Delta g\|$ (take $a=0$, $s=1$, $b=2$), and
$\|\Lambda^{7/4} g\|^2 \le \|\Lambda^{5/4} g\|\,\|\Lambda^{9/4} g\|$.

**Lemma 0.3 (Sobolev embedding on the torus; cited).** Let $g$ be smooth and mean-free on $\mathbb{T}^n$.
For $0 \le s < n/2$ and $\frac1q = \frac12 - \frac sn$ there is $C_{n,s}$ with
$\|g\|_{L^q} \le C_{n,s}\|\Lambda^s g\|$.
This is the standard fractional Sobolev inequality (see e.g. Robinson–Rodrigo–Sadowski,
*The Three-Dimensional Navier–Stokes Equations*, CUP 2016, Ch. 1, or Temam, *Navier–Stokes
Equations*, Ch. 1). Combining it with Lemma 0.2 gives the Gagliardo–Nirenberg forms we need:

* ($n=3$) $\|g\|_{L^3} \le C\|g\|^{1/2}\|\nabla g\|^{1/2}$ ($s=\tfrac12$); $\|g\|_{L^4} \le C\|\Lambda^{3/4} g\|$; $\|g\|_{L^6}\le C\|\nabla g\|$;
  and for $3 < q \le \infty$, $\frac1r = \frac12 - \frac1q$, $a = \frac3q$: $\|g\|_{L^r} \le C_q \|g\|^{1-a}\|\nabla g\|^{a}$.
* ($n=2$, Ladyzhenskaya) $\|g\|_{L^4}^2 \le C\|g\|\,\|\nabla g\|$ ($s=\tfrac12$, then Lemma 0.2).

For vector- or matrix-valued fields (such as $\nabla u$) these inequalities are applied componentwise; the resulting
dimensional factors are absorbed into the constants, which are never tracked beyond their dependence on $\nu$.

**Lemma 0.4 (Fourier identities for divergence-free fields).** For smooth mean-free $u$ on $\mathbb{T}^n$:
$\|\nabla\nabla u\| = \|\Delta u\|$ and, if $\nabla\cdot u = 0$, $\|\nabla u\| = \|\omega\|$ and
$\|\Delta u\| = \|\nabla\omega\|$.
*Proof.* $\|\nabla\nabla u\|^2 = \sum_k |k|^4|\hat u_k|^2 = \|\Delta u\|^2$. For the second,
$|\hat\omega_k|^2 = |k\times\hat u_k|^2 = |k|^2|\hat u_k|^2 - |k\cdot \hat u_k|^2 = |k|^2|\hat u_k|^2$
when $k\cdot\hat u_k = 0$ (in 2D read $k\times\hat u_k = k_1\hat u_{2,k}-k_2\hat u_{1,k}$ and the same
Lagrange identity holds). The third is the second applied to each $\partial_j u$. $\square$

**Lemma 0.5 (pointwise identities; verified symbolically in `verify/identities.py`).** For smooth vector
fields $u$ and scalars $p$, with $|\nabla u|^2 = \partial_k u_i\,\partial_k u_i$:

1. $u\cdot\big((u\cdot\nabla)u\big) = \nabla\cdot\big(u\,\tfrac{|u|^2}{2}\big) - (\nabla\cdot u)\tfrac{|u|^2}{2}$.
2. $u\cdot\nabla p = \nabla\cdot(p\,u) - p\,(\nabla\cdot u)$.
3. $u\cdot\Delta u = \partial_k\big(u_i\,\partial_k u_i\big) - |\nabla u|^2$.
4. $\big((u\cdot\nabla)u\big)\cdot\Delta u = -\,\partial_k u_j\,\partial_j u_i\,\partial_k u_i
   + \partial_k\big(u_j\,\partial_j u_i\,\partial_k u_i\big) - \tfrac12\partial_j\big(u_j|\nabla u|^2\big)
   + \tfrac12(\nabla\cdot u)|\nabla u|^2$.
5. ($n=3$) $\nabla\times\big((u\cdot\nabla)u\big) = (u\cdot\nabla)\omega - (\omega\cdot\nabla)u + (\nabla\cdot u)\,\omega$;
   ($n=2$) $\operatorname{curl}\big((u\cdot\nabla)u\big) = (u\cdot\nabla)\omega + (\nabla\cdot u)\,\omega$.

These are direct expansions of the product rule.

**Young's inequality.** For $a,b\ge0$, $\frac1p+\frac1q=1$: $ab \le \frac{a^p}{p}+\frac{b^q}{q}$.

## 1. The energy identity

**Theorem 1.** Let $u$ be a smooth solution on $\mathbb{T}^n\times[0,T)$. Then for $0\le t<T$

$$\frac12\frac{d}{dt}\|u(t)\|^2 + \nu\|\nabla u(t)\|^2 = 0,
\qquad\text{hence}\qquad
\|u(t)\|^2 + 2\nu\int_0^t\|\nabla u(s)\|^2\,ds = \|u_0\|^2 .$$

*Proof.* Take the inner product of the equation with $u$ and integrate over $\mathbb{T}^n$.
$\int u\cdot\partial_t u = \frac12\frac{d}{dt}\|u\|^2$. By Lemma 0.5(1) and $\nabla\cdot u=0$,
$\int u\cdot(u\cdot\nabla)u = \int\nabla\cdot(u|u|^2/2) = 0$. By Lemma 0.5(2),
$\int u\cdot\nabla p = \int \nabla\cdot(pu) = 0$. By Lemma 0.5(3),
$\nu\int u\cdot\Delta u = -\nu\|\nabla u\|^2$. $\square$

With a force $f$ the same computation gives $\frac12\frac d{dt}\|u\|^2+\nu\|\nabla u\|^2=\langle f,u\rangle$.

**Why this matters.** In three dimensions this is the *only* coercive quantity known to be controlled
for all time by the data: $\sup_t\|u(t)\|$ and $\int_0^\infty\|\nabla u\|^2\,dt$ are bounded by $\|u_0\|^2$ and
$\|u_0\|^2/2\nu$. Section 5 shows this control is "half a derivative" short of what is needed.

## 2. Scaling

**Theorem 2.** If $(u,p)$ solves the unforced system on $\mathbb{R}^3\times(0,T)$ then so does
$u_\lambda(x,t) = \lambda u(\lambda x,\lambda^2 t)$, $p_\lambda(x,t) = \lambda^2 p(\lambda x,\lambda^2t)$ on
$\mathbb{R}^3\times(0,T/\lambda^2)$, for every $\lambda>0$ (with force, take $f_\lambda = \lambda^3 f(\lambda x,\lambda^2 t)$).

*Proof.* Chain rule: $\partial_t u_\lambda = \lambda^3(\partial_t u)(\lambda x,\lambda^2 t)$,
$(u_\lambda\cdot\nabla)u_\lambda = \lambda^3\big((u\cdot\nabla)u\big)(\lambda x,\lambda^2t)$,
$\Delta u_\lambda = \lambda^3(\Delta u)(\lambda x,\lambda^2 t)$, $\nabla p_\lambda = \lambda^3(\nabla p)(\lambda x,\lambda^2t)$,
$\nabla\cdot u_\lambda = \lambda^2(\nabla\cdot u)(\lambda x,\lambda^2 t)$. Every term picks up the same
factor $\lambda^3$, so the residual of the equation scales by $\lambda^3$ and vanishes iff the original does.
(Checked symbolically in `verify/identities.py`.) $\square$

Under this symmetry the norms transform as follows ($\mathbb{R}^n$, same time $t$ on the left, $\lambda^2t$ on the right):

| quantity | $n=3$ | $n=2$ | type in 3D |
|---|---|---|---|
| $\|u_\lambda\|_{L^2}$ | $\lambda^{-1/2}\|u\|_{L^2}$ | $\|u\|_{L^2}$ | supercritical |
| $\|\nabla u_\lambda\|_{L^2}$ | $\lambda^{1/2}\|\nabla u\|_{L^2}$ | $\lambda\|\nabla u\|_{L^2}$ | subcritical |
| $\|u_\lambda\|_{L^3}$, $\|u_\lambda\|_{\dot H^{1/2}}$ | unchanged | — | critical |
| $\|u_\lambda\|_{L^q}$ | $\lambda^{1-3/q}\|u\|_{L^q}$ | — | critical iff $q=3$ |

Zooming into small scales means $\lambda\to\infty$. A norm that *grows* under zoom controls small
scales (subcritical); one that *shrinks* gives no control at all (supercritical). In 3D the energy
shrinks; in 2D it is invariant. This single table is the structural reason 2D is solvable and 3D is open.

## 3. The vortex-stretching dichotomy

**Theorem 3.** Let $u$ be smooth, mean-free and divergence-free on $\mathbb{T}^n$.

* If $n=2$: $\displaystyle\int\big((u\cdot\nabla)u\big)\cdot\Delta u = 0$.
* If $n=3$: $\displaystyle\int\big((u\cdot\nabla)u\big)\cdot\Delta u = -\int \partial_k u_j\,\partial_j u_i\,\partial_k u_i$, and this cubic integral does not vanish in general.

*Proof.* Integrate Lemma 0.5(4) over $\mathbb{T}^n$; the three divergence terms integrate to zero and
$\nabla\cdot u=0$, giving $\int((u\cdot\nabla)u)\cdot\Delta u = -\int\partial_ku_j\partial_ju_i\partial_ku_i$ in any dimension.

In 2D we show the right-hand side vanishes. Since $u$ is mean-free and divergence-free, $k\cdot\hat u_k=0$
for all $k$, so $\hat u_k$ is parallel to $k^\perp=(-k_2,k_1)$: $\hat u_k = c_k k^\perp$ with $c_0 = 0$. Define
$\psi$ by $\hat\psi_k = -i c_k$; then $u = \nabla^\perp\psi := (-\partial_2\psi,\partial_1\psi)$. Consequently
$\omega = \partial_1u_2-\partial_2u_1 = \Delta\psi$ and $\Delta u = \nabla^\perp\Delta\psi = \nabla^\perp\omega$.
For any smooth vector field $F$ and scalar $g$, Lemma 0.1 gives
$\int F\cdot\nabla^\perp g = \int(-F_1\partial_2 g + F_2\partial_1 g) = -\int g\,(\partial_1F_2-\partial_2F_1) = -\int g\,\operatorname{curl}F$.
Apply this with $F=(u\cdot\nabla)u$, $g=\omega$, and Lemma 0.5(5) (2D, $\nabla\cdot u=0$):
$$\int\big((u\cdot\nabla)u\big)\cdot\Delta u = -\int\omega\,(u\cdot\nabla)\omega = -\frac12\int u\cdot\nabla(\omega^2) = \frac12\int(\nabla\cdot u)\,\omega^2 = 0.$$

In 3D the cubic integral is not identically zero: `verify/identities.py` exhibits an explicit divergence-free
trigonometric polynomial $u$ on $\mathbb{T}^3$ and evaluates $\int\partial_ku_j\,\partial_ju_i\,\partial_ku_i$ *exactly* (as a rational
multiple of $\pi^3$, by extracting the constant Fourier mode of the integrand), obtaining a non-zero value; `numerics/`
recomputes the same integral by spectral quadrature. $\square$

The 3D cubic term is the vortex-stretching term: for divergence-free $u$ it equals $\int \omega\cdot(\omega\cdot\nabla)u$,
the source term in the vorticity equation $\partial_t\omega+(u\cdot\nabla)\omega = (\omega\cdot\nabla)u+\nu\Delta\omega$
(Lemma 0.5(5)). In 2D the vorticity equation has no source term at all, and that is the whole story of the next section.

## 4. Two dimensions: global regularity

**Theorem 4.** Let $u$ be a smooth solution on $\mathbb{T}^2\times[0,T)$. Then for all $t<T$:

1. (enstrophy is non-increasing) $\|\omega(t)\|^2 + 2\nu\int_0^t\|\nabla\omega\|^2 = \|\omega_0\|^2$, and $\|\nabla u(t)\| = \|\omega(t)\|\le\|\omega_0\|$;
2. (maximum principle) $\|\omega(t)\|_{L^p}\le\|\omega_0\|_{L^p}$ for every $p\in[2,\infty]$;
3. (higher norms grow at most exponentially) $\|\nabla\omega(t)\|^2 \le \|\nabla\omega_0\|^2\exp\!\big(c\,\nu^{-3}\|u_0\|^2\|\omega_0\|^2\,t\big)$ with an absolute constant $c$.

Combined with the standard local existence theorem and continuation criterion (a smooth solution on
$[0,T)$ with $\sup_{t<T}\|u(t)\|_{H^2}<\infty$ extends smoothly past $T$; Temam, *Navier–Stokes Equations*,
Ch. III, or Robinson–Rodrigo–Sadowski Ch. 6–7), this gives: **for every smooth mean-free divergence-free
$u_0$ on $\mathbb{T}^2$ the solution is smooth for all time.** (Ladyzhenskaya 1959; Lions–Prodi 1959.)

*Proof.* Taking the 2D curl of the equation and using Lemma 0.5(5) with $\nabla\cdot u = 0$ (the curl of a
gradient is zero and curl commutes with $\Delta$) gives the vorticity equation
$$\partial_t\omega + (u\cdot\nabla)\omega = \nu\Delta\omega .$$

(1) Multiply by $\omega$ and integrate: $\int\omega\,(u\cdot\nabla)\omega = \frac12\int u\cdot\nabla(\omega^2) = 0$, and
$\int\omega\Delta\omega = -\|\nabla\omega\|^2$. So $\frac12\frac{d}{dt}\|\omega\|^2+\nu\|\nabla\omega\|^2=0$. The identity
$\|\nabla u\|=\|\omega\|$ is Lemma 0.4.

(2) For $2\le p<\infty$ multiply by $|\omega|^{p-2}\omega$: the transport term is $\frac1p\int u\cdot\nabla|\omega|^p = 0$ and the
viscous term is $-\nu(p-1)\int|\omega|^{p-2}|\nabla\omega|^2\le0$, so $\|\omega\|_{L^p}$ is non-increasing; let $p\to\infty$.

(3) Multiply the vorticity equation by $-\Delta\omega$ and integrate:
$\frac12\frac{d}{dt}\|\nabla\omega\|^2+\nu\|\Delta\omega\|^2 = \int(u\cdot\nabla\omega)\,\Delta\omega.$
By Hölder, Ladyzhenskaya (Lemma 0.3, applied to $u$ and to $\nabla\omega$, both mean-free) and Lemma 0.4,
$$\Big|\int(u\cdot\nabla\omega)\Delta\omega\Big| \le \|u\|_{L^4}\|\nabla\omega\|_{L^4}\|\Delta\omega\|
\le C\,(\|u\|\|\nabla u\|)^{1/2}\,\|\nabla\omega\|^{1/2}\|\Delta\omega\|^{3/2}.$$
Young with exponents $\frac43$ (on $\|\Delta\omega\|^{3/2}$) and $4$:
$\le \nu\|\Delta\omega\|^2 + c\,\nu^{-3}(\|u\|\|\nabla u\|)^2\|\nabla\omega\|^2$. Hence
$\frac{d}{dt}\|\nabla\omega\|^2 \le 2c\,\nu^{-3}\|u_0\|^2\|\omega_0\|^2\,\|\nabla\omega\|^2$ by Theorem 1 and part (1),
and Grönwall gives (3). The same pattern bounds every $H^m$ norm. $\square$

## 5. Three dimensions: Leray's local estimate and where it stops

**Theorem 5.** Let $u$ be a smooth solution on $\mathbb{T}^3\times[0,T)$ and $y(t) = \|\nabla u(t)\|^2$. Let $C_3$ be
the constant in $\|g\|_{L^3}^3\le C_3\|g\|^{3/2}\|\nabla g\|^{3/2}$ (Lemma 0.3, applied to the components of $\nabla u$) and $\kappa = 27C_3^4/16$. Then
$$ y'(t) + \nu\|\Delta u(t)\|^2 \le \kappa\,\nu^{-3}\,y(t)^3, \qquad\text{so}\qquad
y(t) \le \frac{y_0}{\sqrt{1-2\kappa\nu^{-3}y_0^2\,t}} \quad\text{for } t < T_* := \frac{\nu^3}{2\kappa\,y_0^2}. $$

*Proof.* Take the inner product of the equation with $-\Delta u$. Using $\int\partial_t u\cdot(-\Delta u) = \frac12 y'$,
$\int\nabla p\cdot\Delta u = -\int p\,\Delta(\nabla\cdot u) = 0$ and $\int\Delta u\cdot\Delta u=\|\Delta u\|^2$:
$$\tfrac12 y' + \nu\|\Delta u\|^2 = \int\big((u\cdot\nabla)u\big)\cdot\Delta u = -\int\partial_ku_j\,\partial_ju_i\,\partial_ku_i \le \|\nabla u\|_{L^3}^3$$
by Theorem 3 and Hölder. Each $\partial_k u_i$ is mean-free, so Lemma 0.3 and Lemma 0.4 give
$\|\nabla u\|_{L^3}^3\le C_3\|\nabla u\|^{3/2}\|\nabla\nabla u\|^{3/2} = C_3\,y^{3/4}\|\Delta u\|^{3/2}$.
Young with $a = (2\nu/3)^{3/4}\|\Delta u\|^{3/2}$, $b = C_3(2\nu/3)^{-3/4}y^{3/4}$, exponents $\frac43,4$:
$ab \le \frac34 a^{4/3}+\frac14 b^4 = \frac\nu2\|\Delta u\|^2 + \frac{27C_3^4}{32}\nu^{-3}y^3$. Therefore
$\frac12 y' + \nu\|\Delta u\|^2 \le \frac\nu2\|\Delta u\|^2 + \frac{27C_3^4}{32}\nu^{-3}y^3$, i.e. $y'+\nu\|\Delta u\|^2\le\kappa\nu^{-3}y^3$
with $\kappa = 27C_3^4/16$. Finally $(y^{-2})' = -2y'y^{-3}\ge-2\kappa\nu^{-3}$ (dropping the dissipation term), so
$y(t)^{-2}\ge y_0^{-2}-2\kappa\nu^{-3}t$, which is the stated bound. $\square$

**Consequences and limits.**
* With the Galerkin method this estimate yields Leray's 1934 theorem: a smooth solution exists at least on
  $[0,T_*)$, $T_*\sim\nu^3/\|\nabla u_0\|^4$. Note $T_*$ is scale-invariant (Theorem 2: $\nu^3/\|\nabla u_\lambda\|^4 = T_*/\lambda^2$).
* The differential inequality $y'\le\kappa\nu^{-3}y^3$ is *sharp as an inequality*: nothing prevents $y$ from blowing up at $T_*$.
  Every "soft" argument that only uses $\|\nabla u\|^3_{L^3}\le C\|\nabla u\|^{3/2}\|\Delta u\|^{3/2}$ stops exactly here. This is where the
  3D problem has stood since 1934.
* Contrast with 2D: by Theorem 3 the cubic term is identically zero, so $y' + 2\nu\|\Delta u\|^2 = 0$ and $y$ is non-increasing.

**Theorem 5′ (the half-derivative gap).** Theorem 1 controls $u\in L^\infty_tL^2_x\cap L^2_t\dot H^1_x$. By Theorem 2,
$\|u_\lambda\|_{L^\infty_tL^2_x} = \lambda^{-1/2}\|u\|_{L^\infty_tL^2_x}$ and $\|u_\lambda\|_{L^2_t\dot H^1_x} = \lambda^{-1/2}\|u\|_{L^2_t\dot H^1_x}$:
both controlled quantities are supercritical by exactly the factor $\lambda^{-1/2}$. In general
$\|\Lambda^s u_\lambda\|_{L^p_tL^2_x} = \lambda^{\,s-\frac12-\frac2p}\|\Lambda^s u\|_{L^p_tL^2_x}$, so the norm is critical iff $s = \frac12+\frac2p$:
$L^\infty_t\dot H^{1/2}_x$ and $L^2_t\dot H^{3/2}_x$ are critical, and each sits exactly one half derivative above what Theorem 1
provides ($s=0,p=\infty$ and $s=1,p=2$ both give exponent $-\tfrac12$). No unconditional estimate at or above critical scaling is known in 3D.

## 6. Three dimensions: small data

**Theorem 6 (Leray).** With $C_3$ as in Theorem 5: if $\|u_0\|\,\|\nabla u_0\| < (\nu/C_3)^2$, then any smooth solution satisfies
$\|\nabla u(t)\|\le\|\nabla u_0\|$ for all $t$ in its interval of existence, and therefore (continuation criterion) exists and is smooth for all time.

*Proof.* From the proof of Theorem 5, $\frac12y'+\nu\|\Delta u\|^2\le C_3\|\nabla u\|^{3/2}\|\Delta u\|^{3/2}$. By Lemma 0.2,
$\|\nabla u\|^2\le\|u\|\|\Delta u\|$, so $\|\Delta u\|^{3/2} = \|\Delta u\|^2\|\Delta u\|^{-1/2}\le\|\Delta u\|^2\|u\|^{1/2}\|\nabla u\|^{-1}$ (if $\nabla u\ne0$). Hence with $\theta(t) := \|u(t)\|\,\|\nabla u(t)\|$,
$$\tfrac12 y' + \big(\nu - C_3\,\theta^{1/2}\big)\|\Delta u\|^2 \le 0 .$$
Let $t_1 = \sup\{t : \theta(s) < (\nu/C_3)^2 \text{ on }[0,t]\}$. On $[0,t_1)$ the bracket is positive, so $y'\le0$; also $\|u\|$ is
non-increasing (Theorem 1), so $\theta$ is non-increasing on $[0,t_1)$ and $\theta(t_1)\le\theta(0)<(\nu/C_3)^2$ by continuity. If $t_1<T$ this
contradicts the definition of $t_1$; so $t_1 = T$ and $y$ is non-increasing on $[0,T)$. $\square$

The condition $\|u_0\|\|\nabla u_0\|<(\nu/C_3)^2$ is dimensionless and scale-invariant ($\|u_\lambda\|\|\nabla u_\lambda\| = \|u\|\|\nabla u\|$). Later
small-data results (Kato 1984 in $L^3$, Koch–Tataru 2001 in $BMO^{-1}$) are the same statement in critical spaces.

## 7. Three dimensions: conditional regularity (Prodi–Serrin–Ladyzhenskaya type)

**Theorem 7.** Let $u$ be a smooth solution on $\mathbb{T}^3\times[0,T)$ and suppose that for some $3<q\le\infty$ and $p = \frac{2q}{q-3}$
(equivalently $\frac2p+\frac3q = 1$)
$$\int_0^T\|u(t)\|_{L^q}^p\,dt < \infty .$$
Then $\sup_{t<T}\|\nabla u(t)\|<\infty$, and hence the solution extends smoothly past $T$.

*Proof.* Let $a = 3/q\in[0,1)$ and $\frac1r=\frac12-\frac1q$. From the proof of Theorem 5 and Hölder ($\frac1q+\frac1r+\frac12=1$),
$$\tfrac12 y'+\nu\|\Delta u\|^2 = \int u_j\,\partial_ju_i\,\Delta u_i \le \|u\|_{L^q}\|\nabla u\|_{L^r}\|\Delta u\|
\le C_q\|u\|_{L^q}\|\nabla u\|^{1-a}\|\Delta u\|^{1+a},$$
using Lemma 0.3 (Gagliardo–Nirenberg form, applied to the mean-free components of $\nabla u$) and Lemma 0.4. Young with exponents
$\frac{2}{1+a}$ on $\|\Delta u\|^{1+a}$ and $\frac{2}{1-a}$ on the rest gives
$\le \nu\|\Delta u\|^2 + C(\nu,q)\|u\|_{L^q}^{2/(1-a)}\|\nabla u\|^2$, and $\frac{2}{1-a} = \frac{2q}{q-3} = p$. So
$y'\le 2C(\nu,q)\|u\|_{L^q}^p\,y$ and Grönwall gives $y(t)\le y_0\exp\big(2C(\nu,q)\int_0^t\|u\|_{L^q}^p\big)$. $\square$

**Why the exponents are what they are.** By Theorem 2, $\int_0^T\|u_\lambda\|_{L^q}^p\,dt = \lambda^{p(1-3/q)-2}\int_0^{\lambda^2T}\|u\|_{L^q}^p$,
which is scale-invariant exactly when $\frac2p+\frac3q=1$. The energy bounds give $u\in L^\infty_tL^2_x$ ($\frac2p+\frac3q=\frac32$) and
$u\in L^2_tL^6_x$ ($\frac2p+\frac3q = \frac32$): again short by $\frac12$. The endpoint $q=3$, $p=\infty$ is the
Escauriaza–Seregin–Šverák theorem (2003), proved by a completely different (backward uniqueness) argument.

## 8. Hyperviscosity: the problem becomes solvable at $(-\Delta)^{5/4}$

Replace $-\nu\Delta$ by $\nu(-\Delta)^{\alpha} = \nu\Lambda^{2\alpha}$. The scaling symmetry becomes
$u_\lambda = \lambda^{2\alpha-1}u(\lambda x,\lambda^{2\alpha}t)$ and $\|u_\lambda\|_{L^2(\mathbb{R}^3)} = \lambda^{2\alpha-5/2}\|u\|_{L^2}$:
the energy is critical exactly at $\alpha = 5/4$ and subcritical above. Lions (1969) proved global regularity for $\alpha\ge5/4$;
here is the complete a priori estimate at the endpoint.

**Theorem 8 (Lions, $\alpha = 5/4$).** Let $u$ be a smooth solution of $\partial_tu+(u\cdot\nabla)u = -\nu\Lambda^{5/2}u-\nabla p$, $\nabla\cdot u=0$,
on $\mathbb{T}^3\times[0,T)$. Then
$$\|\nabla u(t)\|^2 \le \|\nabla u_0\|^2\exp\!\Big(\frac{C^2}{2\nu^2}\|u_0\|^2\Big)\quad\text{for all }t<T,$$
with $C$ the constant in $\|g\|_{L^4}\le C\|\Lambda^{3/4}g\|$. Consequently the solution is global.

*Proof.* Energy: as in Theorem 1, $\frac12\frac d{dt}\|u\|^2+\nu\|\Lambda^{5/4}u\|^2=0$ (since $\langle\Lambda^{5/2}u,u\rangle=\|\Lambda^{5/4}u\|^2$),
so $\int_0^\infty\|\Lambda^{5/4}u\|^2\le\|u_0\|^2/2\nu$.
$H^1$: pairing with $-\Delta u = \Lambda^2u$, $\frac12 y'+\nu\|\Lambda^{9/4}u\|^2 = \int((u\cdot\nabla)u)\cdot\Delta u = -\int\partial_ku_j\partial_ju_i\partial_ku_i$ (Theorem 3), so
$$\tfrac12y'+\nu\|\Lambda^{9/4}u\|^2\le\|\nabla u\|\,\|\nabla u\|_{L^4}^2\le C^2\|\nabla u\|\,\|\Lambda^{7/4}u\|^2\le C^2\|\nabla u\|\,\|\Lambda^{5/4}u\|\,\|\Lambda^{9/4}u\|,$$
by Hölder, Lemma 0.3 ($\|\nabla u\|_{L^4}\le C\|\Lambda^{3/4}\nabla u\| = C\|\Lambda^{7/4}u\|$) and Lemma 0.2. Young ($ab\le\frac{\nu}{2}a^2+\frac1{2\nu}b^2$):
$\le\frac\nu2\|\Lambda^{9/4}u\|^2+\frac{C^2}{2\nu}\|\Lambda^{5/4}u\|^2\,y$. Hence $y'\le\frac{C^2}{\nu}\|\Lambda^{5/4}u\|^2\,y$ and Grönwall with the energy bound gives the claim. $\square$

For $\alpha>5/4$ the same argument works with room to spare; Tao (2009) pushed it to a logarithmically supercritical dissipation.
For the true Navier–Stokes ($\alpha=1$) the $\|\Lambda^{7/4}u\|^2$ term cannot be absorbed: interpolating between the available
$\|\Lambda u\|$ and $\|\Lambda^2u\|$ gives $\|\Lambda^{7/4}u\|^2\le\|\Lambda u\|^{1/2}\|\Lambda^2u\|^{3/2}$ and one is back to Theorem 5.

## 9. Deeper theorems (stated, not reproved)

The following are established results with full proofs in the literature. Statements are given in the
form relevant to the Clay problem.

**9.1 Leray–Hopf weak solutions (Leray 1934, Hopf 1951).** For every divergence-free $u_0\in L^2$ (on $\mathbb{R}^3$ or $\mathbb{T}^3$)
there exists $u\in L^\infty(0,\infty;L^2)\cap L^2(0,\infty;\dot H^1)$, weakly continuous in time, satisfying the equations in the
sense of distributions (with the pressure eliminated by divergence-free test functions) and the energy *inequality*
$\|u(t)\|^2+2\nu\int_0^t\|\nabla u\|^2\le\|u_0\|^2$. Uniqueness is unknown.

**9.2 Weak–strong uniqueness (Prodi 1959, Serrin 1963; endpoint Escauriaza–Seregin–Šverák 2003).** If a Leray–Hopf solution
$u$ satisfies $u\in L^p(0,T;L^q)$ with $\frac2p+\frac3q=1$, $3\le q\le\infty$, then it is smooth on $(0,T]$ and coincides with every
Leray–Hopf solution with the same data. Theorem 7 above is the a priori version for $q>3$.

**9.3 Beale–Kato–Majda (1984).** A smooth solution on $[0,T)$ (Euler or Navier–Stokes) extends past $T$ if and only if
$\int_0^T\|\omega(t)\|_{L^\infty}\,dt<\infty$.

**9.4 Partial regularity (Caffarelli–Kohn–Nirenberg 1982; Scheffer 1976–80; Lin 1998).** For *suitable* weak solutions (Leray–Hopf
solutions satisfying a local energy inequality) the singular set $S\subset\mathbb{R}^3\times(0,\infty)$ has one-dimensional parabolic
Hausdorff measure zero: $\mathcal P^1(S)=0$. In particular singularities, if any, cannot fill a curve in space-time.

**9.5 Global regularity in special classes.** 2D (Theorem 4); axisymmetric flows without swirl (Ladyzhenskaya 1968; Ukhovskii–Yudovich 1968);
helically symmetric flows (Mahalov–Titi–Leibovich 1990); small data in critical spaces (Theorem 6; Kato 1984; Koch–Tataru 2001);
hyperdissipation $\alpha\ge5/4$ (Theorem 8; Lions 1969; Tao 2009 for a logarithmic improvement).

**9.6 Obstructions (what a proof of (A) cannot look like).**
* Tao, *Finite time blowup for an averaged three-dimensional Navier–Stokes equation*, J. Amer. Math. Soc. 29 (2016): there is an
  "averaged" bilinear operator $\tilde B$, obeying the same energy identity, the same scaling, and the same harmonic-analysis
  estimates as the true nonlinearity, for which smooth Schwartz data blow up in finite time. Any proof of (A) must therefore use a
  property of the true nonlinearity that the averaged one lacks.
* Buckmaster–Vicol, *Nonuniqueness of weak solutions to the Navier–Stokes equation*, Ann. of Math. 189 (2019): distributional
  solutions with finite energy (not Leray–Hopf) are not unique; in fact the kinetic energy profile can be prescribed.
* Albritton–Brué–Colombo, *Non-uniqueness of Leray solutions of the forced Navier–Stokes equations*, Ann. of Math. 196 (2022):
  with a suitable (singular in time, but $L^1_tL^2_x$) body force, Leray–Hopf solutions from zero initial data are not unique.
  Uniqueness of unforced Leray–Hopf solutions remains open.

**9.7 Blowup for related equations.**
* Elgindi (Ann. of Math. 2021): finite-time singularity for 3D Euler from $C^{1,\alpha}$ (not smooth) data on $\mathbb{R}^3$.
* Chen–Hou (2022–23, computer-assisted): finite-time blowup for 3D axisymmetric Euler with smooth data in a cylinder with boundary,
  and for 2D Boussinesq.
* Córdoba–Martínez-Zoroa (2023–25): finite-time blowup for 3D Euler and related models *with a forcing term*.
* Alpöge–Buckmaster (September 2026, with Coiculescu for IPM): finite-time blowup with smooth forcing for the incompressible porous
  medium equation, 2D Boussinesq and 3D Euler, with Lean formalizations. Their hypodissipative Navier–Stokes result is announced but withheld pending formal verification.
* OpenAI (8 September 2026): forced finite-time blowup for 3D Navier–Stokes on $\mathbb{R}^3$ and $\mathbb{T}^3$ (Clay (C) and (D)), and
  unforced blowup for 3D Euler from smooth compactly supported data on $\mathbb{R}^3$, with Lean formalizations. Under review; see
  `02-status-november-2026.md` and `03-audit-openai-lean-formalization.md`.

None of 9.6–9.7 proves or disproves (A) or (B).
