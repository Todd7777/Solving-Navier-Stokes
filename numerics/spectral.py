"""Pseudo-spectral Navier-Stokes solvers on the 2*pi-periodic box (2D vorticity form, 3D velocity form).

These are *instruments*, not evidence for or against regularity: a finite computation can never
decide Clay statements (A)/(B).  They exist to (i) check the identities in docs/04 numerically,
(ii) exhibit the 2D monotone quantities and the 3D vortex-stretching term, and (iii) provide a
tested starting point for experiments.  Fourier differentiation is spectrally accurate; products
are 2/3-dealiased; time stepping is classical RK4.
"""
from __future__ import annotations

import numpy as np

TWO_PI = 2.0 * np.pi


def _wavenumbers(N: int) -> np.ndarray:
    return np.fft.fftfreq(N, 1.0 / N)  # integer wavenumbers 0,1,...,N/2-1,-N/2,...,-1


class NS2D:
    """2D incompressible Navier-Stokes in vorticity form: w_t + u.grad w = nu Lap w on [0,2pi]^2."""

    def __init__(self, N: int, nu: float):
        self.N, self.nu = N, nu
        k = _wavenumbers(N)
        self.kx, self.ky = np.meshgrid(k, k, indexing="ij")
        self.k2 = self.kx ** 2 + self.ky ** 2
        self.k2inv = np.zeros_like(self.k2)
        self.k2inv[self.k2 > 0] = 1.0 / self.k2[self.k2 > 0]
        kmax = N / 3.0
        self.dealias = (np.abs(self.kx) < kmax) & (np.abs(self.ky) < kmax)
        x = np.arange(N) * TWO_PI / N
        self.X, self.Y = np.meshgrid(x, x, indexing="ij")

    # --- transforms -------------------------------------------------------------------------
    def fft(self, f):
        return np.fft.fft2(f)

    def ifft(self, fh):
        return np.fft.ifft2(fh).real

    def velocity_hat(self, wh):
        """u = grad^perp psi, w = Lap psi  =>  psi_hat = -w_hat/|k|^2."""
        psih = -wh * self.k2inv
        return -1j * self.ky * psih, 1j * self.kx * psih

    def velocity(self, wh):
        uh, vh = self.velocity_hat(wh)
        return self.ifft(uh), self.ifft(vh)

    # --- dynamics ---------------------------------------------------------------------------
    def rhs(self, wh):
        u, v = self.velocity(wh)
        wx = self.ifft(1j * self.kx * wh)
        wy = self.ifft(1j * self.ky * wh)
        nl = self.fft(u * wx + v * wy) * self.dealias
        return -nl - self.nu * self.k2 * wh

    def step(self, wh, dt):
        k1 = self.rhs(wh)
        k2 = self.rhs(wh + 0.5 * dt * k1)
        k3 = self.rhs(wh + 0.5 * dt * k2)
        k4 = self.rhs(wh + dt * k3)
        return (wh + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)) * self.dealias

    # --- diagnostics (integrals over [0,2pi]^2 via Parseval) --------------------------------
    def _integral_sq(self, fh):
        return TWO_PI ** 2 / self.N ** 4 * np.sum(np.abs(fh) ** 2)

    def energy(self, wh):
        uh, vh = self.velocity_hat(wh)
        return 0.5 * (self._integral_sq(uh) + self._integral_sq(vh))

    def enstrophy(self, wh):
        return 0.5 * self._integral_sq(wh)

    def palinstrophy(self, wh):
        return 0.5 * (self._integral_sq(1j * self.kx * wh) + self._integral_sq(1j * self.ky * wh))

    def grad_u_sq(self, wh):
        """int |grad u|^2 ( = int w^2 for divergence-free periodic u, Lemma 0.4)."""
        uh, vh = self.velocity_hat(wh)
        return sum(self._integral_sq(1j * k * fh) for fh in (uh, vh) for k in (self.kx, self.ky))

    def taylor_green(self, t=0.0):
        """Exact solution w = 2 sin x sin y exp(-2 nu t)."""
        return 2.0 * np.sin(self.X) * np.sin(self.Y) * np.exp(-2.0 * self.nu * t)

    def random_field(self, seed=0, kmax=4, amplitude=1.0):
        rng = np.random.default_rng(seed)
        w = np.zeros((self.N, self.N))
        for kx in range(-kmax, kmax + 1):
            for ky in range(-kmax, kmax + 1):
                if kx == 0 and ky == 0:
                    continue
                w += rng.normal() * np.cos(kx * self.X + ky * self.Y + rng.uniform(0, TWO_PI))
        w *= amplitude / np.max(np.abs(w))
        return w


class NS3D:
    """3D incompressible Navier-Stokes in velocity form on [0,2pi]^3 with the Leray projector."""

    def __init__(self, N: int, nu: float):
        self.N, self.nu = N, nu
        k = _wavenumbers(N)
        self.K = np.array(np.meshgrid(k, k, k, indexing="ij"))  # shape (3,N,N,N)
        self.k2 = np.sum(self.K ** 2, axis=0)
        self.k2inv = np.zeros_like(self.k2)
        self.k2inv[self.k2 > 0] = 1.0 / self.k2[self.k2 > 0]
        kmax = N / 3.0
        self.dealias = np.all(np.abs(self.K) < kmax, axis=0)
        x = np.arange(N) * TWO_PI / N
        self.X = np.array(np.meshgrid(x, x, x, indexing="ij"))

    def fft(self, f):
        return np.fft.fftn(f, axes=(-3, -2, -1))

    def ifft(self, fh):
        return np.fft.ifftn(fh, axes=(-3, -2, -1)).real

    def project(self, fh):
        """Leray projection: remove the gradient part, (I - k k^T/|k|^2) f_hat."""
        kdotf = np.sum(self.K * fh, axis=0)
        return fh - self.K * (kdotf * self.k2inv)

    def divergence_hat(self, uh):
        return 1j * np.sum(self.K * uh, axis=0)

    def gradient(self, uh):
        """Physical-space Jacobian G[i][j] = d_j u_i."""
        return [[self.ifft(1j * self.K[j] * uh[i]) for j in range(3)] for i in range(3)]

    def advection_hat(self, uh):
        """Fourier transform of (u.grad)u, dealiased."""
        u = self.ifft(uh)
        G = self.gradient(uh)
        adv = np.array([sum(u[j] * G[i][j] for j in range(3)) for i in range(3)])
        return self.fft(adv) * self.dealias

    def rhs(self, uh):
        return self.project(-self.advection_hat(uh)) - self.nu * self.k2 * uh

    def step(self, uh, dt):
        k1 = self.rhs(uh)
        k2 = self.rhs(uh + 0.5 * dt * k1)
        k3 = self.rhs(uh + 0.5 * dt * k2)
        k4 = self.rhs(uh + dt * k3)
        return (uh + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)) * self.dealias

    # --- diagnostics --------------------------------------------------------------------------
    def _integral_sq(self, fh):
        return TWO_PI ** 3 / self.N ** 6 * np.sum(np.abs(fh) ** 2)

    def integral(self, f):
        """int f dx by the trapezoidal rule (exact for resolved trigonometric polynomials)."""
        return TWO_PI ** 3 / self.N ** 3 * np.sum(f)

    def energy(self, uh):
        return 0.5 * sum(self._integral_sq(uh[i]) for i in range(3))

    def grad_u_sq(self, uh):
        return sum(self._integral_sq(1j * self.K[j] * uh[i]) for i in range(3) for j in range(3))

    def enstrophy(self, uh):
        w = self.vorticity_hat(uh)
        return 0.5 * sum(self._integral_sq(w[i]) for i in range(3))

    def vorticity_hat(self, uh):
        K = self.K
        return np.array([1j * (K[1] * uh[2] - K[2] * uh[1]),
                         1j * (K[2] * uh[0] - K[0] * uh[2]),
                         1j * (K[0] * uh[1] - K[1] * uh[0])])

    def cubic_integral(self, uh):
        """int d_k u_j d_j u_i d_k u_i  (the vortex-stretching integral of Theorem 3)."""
        G = self.gradient(uh)
        T = sum(G[j][k] * G[i][j] * G[i][k] for i in range(3) for j in range(3) for k in range(3))
        return self.integral(T)

    def taylor_green(self):
        X, Y, Z = self.X
        u = np.array([np.sin(X) * np.cos(Y) * np.cos(Z), -np.cos(X) * np.sin(Y) * np.cos(Z), np.zeros_like(X)])
        return self.fft(u)

    def from_expressions(self, exprs, symbols):
        """Evaluate sympy expressions u_i(x1,x2,x3) on the grid and return their Fourier transform."""
        import sympy as sp
        fns = [sp.lambdify(symbols, e, "numpy") for e in exprs]
        u = np.array([np.broadcast_to(fn(*self.X), self.X[0].shape).astype(float) for fn in fns])
        return self.fft(u)
