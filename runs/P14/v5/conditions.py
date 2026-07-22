"""P14 V5: machine-verified standard necessary conditions for the 4 open BTD instances.

BTD(V,B; r1,r2,R; K,L): V x B matrix N over {0,1,2};
- each row has exactly r1 ones and r2 twos (so row sum R = r1+2*r2)
- each column sums to K
- for v != w: sum_b N[v,b]*N[w,b] = L
Hence N N^T = (r1+4*r2-L) I + L J.
"""
from fractions import Fraction

INSTANCES = [
    ("I1", 14, 18, 7, 1, 9, 7, 4),
    ("I2", 12, 15, 6, 2, 10, 8, 6),
    ("I3", 12, 20, 4, 3, 10, 6, 4),
    ("I4", 14, 28, 8, 3, 14, 7, 6),
]

def check(name, V, B, r1, r2, R, K, L):
    out = [name]
    ok = True
    def rec(label, cond, detail=""):
        nonlocal ok
        out.append(f"  {label}: {'OK' if cond else 'FAIL'} {detail}")
        ok = ok and cond
    rec("R = r1+2r2", R == r1 + 2*r2, f"{R} vs {r1+2*r2}")
    rec("VR = BK", V*R == B*K, f"{V*R} vs {B*K}")
    # pair count through a fixed element: sum_b m_vb(K - m_vb) = L(V-1)
    rec("L(V-1) = RK - (r1+4r2)", L*(V-1) == R*K - (r1+4*r2),
        f"{L*(V-1)} vs {R*K-(r1+4*r2)}")
    # global pair count: B*K(K-1)/2 - V*r2 = L*V(V-1)/2
    rec("global pairs", B*K*(K-1)//2 - V*r2 == L*V*(V-1)//2,
        f"{B*K*(K-1)//2 - V*r2} vs {L*V*(V-1)//2}")
    # Gram matrix eigenvalues: theta = r1+4r2-L (mult V-1), tau = r1+4r2+L(V-1)
    theta = r1 + 4*r2 - L
    tau = r1 + 4*r2 + L*(V-1)
    rec("Gram eigen theta>0 => Fisher B>=V", not (theta > 0 and tau > 0) or B >= V,
        f"theta={theta}, tau={tau}, B={B}, V={V}")
    # det of Gram (if square-ish; here B>V so only PSD/rank conditions apply)
    det = Fraction(theta)**(V-1) * tau
    out.append(f"  det Gram = {det} = theta^(V-1)*tau (theta={theta}, tau={tau})")
    # column doubles d_b: 0 <= d_b <= K//2, sum d_b = V*r2, K-2d_b singles need K-d_b <= V
    out.append(f"  sum d_b = V*r2 = {V*r2}; d_b in [max(0,ceil((K-V)/1))..{K//2}]; blocks B={B}")
    # max pairs-of-doubles per pair mu <= L//4
    out.append(f"  mu_max (pair both doubled same block) = {L//4}")
    print("\n".join(out))
    return ok

if __name__ == "__main__":
    allok = all(check(*inst) for inst in INSTANCES)
    print("ALL STANDARD NECESSARY CONDITIONS SATISFIED" if allok else "SOME CONDITION FAILS")
