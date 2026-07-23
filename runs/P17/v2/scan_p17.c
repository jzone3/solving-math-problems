/* P17 (WoW 20 & 21) exhaustive scanner.
 *   WoW20: n+(G) <= sum of positive adjacency eigenvalues (violation score s20 = n+ - sumpos)
 *   WoW21: n-(G) <= sum of positive adjacency eigenvalues (violation score s21 = n- - sumpos)
 * Reads graph6 lines (n <= 62) from stdin (pipe from nauty-geng -q -c n).
 * Prints the top-K scores for both. Float filter only; exact verification is
 * done separately (verify.py) on any candidate with score > -EPS_REPORT.
 * Compile: gcc -O3 -march=native -o scan_p17 scan_p17.c -llapack -lm
 * Usage: nauty-geng -q -c 11 res/mod | ./scan_p17 11
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

extern void dsyev_(const char*, const char*, const int*, double*, const int*,
                   double*, double*, const int*, int*);

#define TOPK 8
typedef struct { double s; char g6[64]; } Ent;
static void insert(Ent *top, double s, const char *g6) {
    if (s <= top[TOPK-1].s) return;
    int i = TOPK - 1;
    while (i > 0 && top[i-1].s < s) { top[i] = top[i-1]; i--; }
    top[i].s = s; strncpy(top[i].g6, g6, 63); top[i].g6[63] = 0;
}

int main(int argc, char **argv) {
    int n = atoi(argv[1]);
    int nb = (n * (n - 1) / 2 + 5) / 6;
    Ent t20[TOPK], t21[TOPK];
    for (int i = 0; i < TOPK; i++) { t20[i].s = -1e18; t21[i].s = -1e18; t20[i].g6[0]=t21[i].g6[0]=0; }
    char line[256];
    long long cnt = 0;
    double A[64*64], w[64], work[64*34];
    int lwork = 64*34, info;
    const double ZTOL = 1e-9; /* eigenvalue > ZTOL counts as positive; graphs with
                                 |eig| <= 1e-7 near zero are re-checked exactly anyway
                                 because their scores land in the reported band */
    while (fgets(line, sizeof line, stdin)) {
        int len = (int)strlen(line);
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        if (len != nb + 1) continue;
        memset(A, 0, sizeof(double)*n*n);
        int bitpos = 0;
        for (int j = 1; j < n; j++)
            for (int i = 0; i < j; i++, bitpos++) {
                int c = line[1 + bitpos / 6] - 63;
                if ((c >> (5 - bitpos % 6)) & 1) { A[i*n+j] = 1.0; A[j*n+i] = 1.0; }
            }
        cnt++;
        int nn = n;
        dsyev_("N", "U", &nn, A, &nn, w, work, &lwork, &info);
        if (info) { fprintf(stderr, "dsyev info=%d on %s\n", info, line); continue; }
        int npos = 0, nneg = 0; double sumpos = 0;
        for (int i = 0; i < n; i++) {
            if (w[i] > ZTOL) { npos++; sumpos += w[i]; }
            else if (w[i] < -ZTOL) nneg++;
        }
        insert(t20, (double)npos - sumpos, line);
        insert(t21, (double)nneg - sumpos, line);
    }
    printf("graphs=%lld n=%d\n", cnt, n);
    printf("top WoW20 (n+ - sumpos, violation if >0):\n");
    for (int i = 0; i < TOPK; i++) printf("  %+.10f  %s\n", t20[i].s, t20[i].g6);
    printf("top WoW21 (n- - sumpos, violation if >0):\n");
    for (int i = 0; i < TOPK; i++) printf("  %+.10f  %s\n", t21[i].s, t21[i].g6);
    return 0;
}
