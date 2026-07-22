"""Schrijver's 1980 counterexample to Edmonds-Giles, transcribed from
Feofiloff's survey Figure 6 (woodall-conjecture-en.pdf, 2025-05-01).

12 vertices: outer hexagon TL,TR,R,BR,BL,L and inner hexagon uL,uR,mR,lR,lL,mL.
Weight-1 (solid) arcs form three alternating paths of length 3:
  a: TR->R, b: TR->uL, c: mL->uL   (path R<-TR->uL<-mL)
  d: L->TL, e: L->lL, f: lR->lL    (path TL<-L->lL<-lR)
  g: BR->BL, h: BR->mR, i: uR->mR  (path BL<-BR->mR<-uR)
Weight-0 (dashed): outer TR->TL, L->BL, BR->R; inner uR->uL, mL->lL, lR->mR;
radial TL->uL, TR->uR, R->mR, L->mL, BL->lL, BR->lR.
Expected: tau_w = 2, nu_w = 1.
"""

TL, TR, R, BR, BL, L, uL, uR, mR, lR, lL, mL = range(12)

ARCS_W1 = [(TR, R), (TR, uL), (mL, uL),
           (L, TL), (L, lL), (lR, lL),
           (BR, BL), (BR, mR), (uR, mR)]
ARCS_W0 = [(TR, TL), (L, BL), (BR, R),
           (uR, uL), (mL, lL), (lR, mR),
           (TL, uL), (TR, uR), (R, mR), (L, mL), (BL, lL), (BR, lR)]

N = 12
ARCS = ARCS_W1 + ARCS_W0
W = [1] * len(ARCS_W1) + [0] * len(ARCS_W0)

if __name__ == "__main__":
    from weighted import tau_w, pack_w
    t, cuts = tau_w(N, ARCS, W)
    print("num dicuts:", len(cuts), "tau_w =", t)
    ok2, _ = pack_w(N, ARCS, W, 2)
    ok1, _ = pack_w(N, ARCS, W, 1)
    print("pack 2 dijoins:", ok2, "| pack 1 dijoin:", ok1)
    if t == 2 and not ok2 and ok1:
        print("PASS: reproduces Schrijver tau_w=2, nu_w=1 "
              "-- detector validated end-to-end")
    else:
        print("MISMATCH with literature -- transcription or code issue")
