"""Numeric verification of the equitable eigen-decomposition used by
hub_gadget_proof.py (Theorem M3): full spectrum of M(sigma_c) on hub+k*gadget
equals {t_o - gam*nu : nu in spec(A_g), nu != g} (mult k) + {t_o - gam*g}
(mult k-1) + eig of the 2x2 hub block."""
import numpy as np
from common import (build_base, with_diag, sigma_cap, hub_gadgets,
                    gadget_cycle, gadget_clique)

for (gad, g, L, name) in [(gadget_cycle(4), 2, 4, 'C4'),
                          (gadget_clique(4), 3, 4, 'K4'),
                          (gadget_cycle(5), 2, 5, 'C5')]:
    for kk in (12, 20):
        for c in (2.0, 4.0):
            A = hub_gadgets([gad] * kk)
            b = build_base(A)
            s = sigma_cap(b['d'], b['m'], c)
            M = with_diag(b, s)['M']
            ev = np.linalg.eigvalsh(M)
            t_o = M[1, 1]
            Ag = A[1:1 + L, 1:1 + L]
            nus = np.linalg.eigvalsh(Ag)
            gam = None
            for i in range(1, 1 + L):
                for j in range(i + 1, 1 + L):
                    if A[i, j]:
                        gam = -M[i, j]
                        break
                if gam:
                    break
            Mhh, Mho = M[0, 0], M[0, 1]
            pred = []
            for nu in nus:
                if abs(nu - g) < 1e-9:
                    continue
                pred += [t_o - gam * nu] * kk
            pred += [t_o - gam * g] * (kk - 1)
            b2 = np.array([[Mhh, np.sqrt(kk * L) * Mho],
                           [np.sqrt(kk * L) * Mho, t_o - gam * g]])
            pred += list(np.linalg.eigvalsh(b2))
            match = np.allclose(sorted(pred), ev, atol=1e-8)
            print(name, kk, c, 'decomposition matches:', match,
                  'min eig %.4f' % ev[0])
            assert match
print("DECOMPOSITION VERIFIED")
