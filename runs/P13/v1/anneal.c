/* Simulated annealing search for a (v,6,1)-PMD witness.
 * State: b x 6 array, each row 6 distinct symbols from 0..v-1.
 * Cost: sum over t=1..5 and ordered pairs (x,y) of max(0, cnt[t][x][y]-1)
 *       + number of missing pairs, i.e. sum |cnt-1| (cnt>=0).
 * Moves: (a) change one cell to a symbol not in that block,
 *        (b) swap two cells within a block.
 * cc -O2 anneal.c -o anneal ; ./anneal v seed [maxiters]
 * Prints the design and VALID if cost 0 reached.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define K 6
static int v, b;
static int blk[64][K];
static int cnt[5][20][20];
static long long cost;

static unsigned long long rng_state;
static unsigned long long rnd(void) {
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return rng_state;
}
static double rndd(void) { return (double)(rnd() >> 11) / 9007199254740992.0; }

static long long pair_pen(int c) { return c > 1 ? c - 1 : (c < 1 ? 1 - c : 0); }

static void add_block(int j, int sgn) {
    for (int t = 1; t <= 5; t++)
        for (int p = 0; p < K; p++) {
            int x = blk[j][p], y = blk[j][(p + t) % K];
            cost -= pair_pen(cnt[t - 1][x][y]);
            cnt[t - 1][x][y] += sgn;
            cost += pair_pen(cnt[t - 1][x][y]);
        }
}

static void init_cost(void) {
    memset(cnt, 0, sizeof(cnt));
    cost = 0;
    for (int t = 0; t < 5; t++)
        for (int x = 0; x < v; x++)
            for (int y = 0; y < v; y++)
                if (x != y) cost += 1; /* missing */
    for (int j = 0; j < b; j++) {
        /* add block incrementally: emulate via add_block but cost of missing
           already counted; add_block handles transitions since pen(0)=1 */
        add_block(j, +1);
    }
}

int main(int argc, char **argv) {
    v = atoi(argv[1]);
    rng_state = argc > 2 ? strtoull(argv[2], 0, 10) : 12345;
    long long maxit = argc > 3 ? atoll(argv[3]) : 2000000000LL;
    b = v * (v - 1) / K;
    /* init: random rows */
    for (int j = 0; j < b; j++) {
        int used[20] = {0};
        for (int p = 0; p < K; p++) {
            int s;
            do { s = rnd() % v; } while (used[s]);
            used[s] = 1;
            blk[j][p] = s;
        }
    }
    init_cost();
    double T = 2.0;
    long long best = cost;
    for (long long it = 0; it < maxit && cost > 0; it++) {
        if ((it & 0xFFFFF) == 0) {
            T *= 0.999;
            if (T < 0.05) T = 0.6; /* reheat cycles */
        }
        int j = rnd() % b;
        int p = rnd() % K;
        long long old = cost;
        int savedcell = blk[j][p];
        int mode = rnd() & 1;
        int q = 0, saved2 = 0, news = 0;
        if (mode == 0) {
            /* change cell to symbol not in block */
            int inblk[20] = {0};
            for (int i = 0; i < K; i++) inblk[blk[j][i]] = 1;
            do { news = rnd() % v; } while (inblk[news]);
            add_block(j, -1);
            blk[j][p] = news;
            add_block(j, +1);
        } else {
            q = rnd() % K;
            if (q == p) q = (q + 1) % K;
            add_block(j, -1);
            saved2 = blk[j][q];
            blk[j][q] = blk[j][p];
            blk[j][p] = saved2;
            add_block(j, +1);
        }
        long long d = cost - old;
        if (d > 0 && rndd() > exp(-d / T)) {
            /* revert */
            add_block(j, -1);
            if (mode == 0) blk[j][p] = savedcell;
            else { blk[j][q] = saved2; blk[j][p] = savedcell; /* wrong order fix */ }
            add_block(j, +1);
        }
        if (cost < best) {
            best = cost;
            if ((best < 6) || (it & 0xFFFFFF) == 0)
                fprintf(stderr, "it=%lld best=%lld T=%.3f\n", it, best, T);
        }
    }
    if (cost == 0) {
        printf("VALID\n");
        for (int j = 0; j < b; j++) {
            for (int p = 0; p < K; p++) printf("%d ", blk[j][p]);
            printf("\n");
        }
        return 0;
    }
    printf("NOT FOUND best=%lld\n", best);
    return 1;
}
