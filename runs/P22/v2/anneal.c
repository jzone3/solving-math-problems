/* SAT-side local search for G127 -/-> (3,3)^e:
 * find a 2-coloring of the 2667 edges with zero monochromatic triangles.
 * Energy = #monochromatic triangles; moves = single edge flips;
 * simulated annealing with restarts. If energy 0 found, writes coloring
 * to best_coloring.txt (edge_index color) and exits 0; else keeps best.
 * Usage: ./anneal <seconds> [seed]
 */
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define NE 2667
#define NT 9779

static int tri[NT][3];              /* edge indices per triangle */
static int etris[NE][30]; static int ecnt[NE]; /* triangles per edge */
static int color[NE];               /* 0/1 */
static int mono[NT];                /* is triangle monochromatic */
static int energy;

static unsigned long long rng_s;
static inline unsigned long long rng(void){
    rng_s ^= rng_s << 13; rng_s ^= rng_s >> 7; rng_s ^= rng_s << 17; return rng_s;
}

static int tri_mono(int t){
    return color[tri[t][0]] == color[tri[t][1]] && color[tri[t][1]] == color[tri[t][2]];
}

static int delta_flip(int e){
    int d = 0;
    for (int i = 0; i < ecnt[e]; i++){
        int t = etris[e][i];
        int before = mono[t];
        color[e] ^= 1; int after = tri_mono(t); color[e] ^= 1;
        d += after - before;
    }
    return d;
}

static void apply_flip(int e){
    color[e] ^= 1;
    for (int i = 0; i < ecnt[e]; i++){
        int t = etris[e][i];
        int m = tri_mono(t);
        energy += m - mono[t];
        mono[t] = m;
    }
}

int main(int argc, char **argv){
    double secs = argc > 1 ? atof(argv[1]) : 60;
    rng_s = argc > 2 ? strtoull(argv[2], 0, 10) : 88172645463325252ULL;

    FILE *f = fopen("g127.tri_edges", "r");
    if (!f){ fprintf(stderr, "missing g127.tri_edges\n"); return 2; }
    for (int t = 0; t < NT; t++){
        if (fscanf(f, "%d %d %d", &tri[t][0], &tri[t][1], &tri[t][2]) != 3) return 2;
        for (int j = 0; j < 3; j++){
            int e = tri[t][j];
            etris[e][ecnt[e]++] = t;
        }
    }
    fclose(f);

    int best = NT + 1;
    clock_t start = clock();
    while ((double)(clock() - start) / CLOCKS_PER_SEC < secs){
        for (int e = 0; e < NE; e++) color[e] = rng() & 1;
        energy = 0;
        for (int t = 0; t < NT; t++){ mono[t] = tri_mono(t); energy += mono[t]; }
        double T = 3.0;
        for (long it = 0; it < 40000000L; it++){
            int e = rng() % NE;
            int d = delta_flip(e);
            if (d <= 0 || (double)(rng() % 1000000) / 1000000.0 < exp(-d / T))
                apply_flip(e);
            if (energy < best){
                best = energy;
                if (best == 0){
                    FILE *o = fopen("best_coloring.txt", "w");
                    for (int i = 0; i < NE; i++) fprintf(o, "%d %d\n", i, color[i]);
                    fclose(o);
                    printf("ZERO-MONO COLORING FOUND\n");
                    return 0;
                }
            }
            if ((it & 0xfffff) == 0){
                T *= 0.97;
                if (T < 0.05) T = 0.05;
                if ((double)(clock() - start) / CLOCKS_PER_SEC >= secs) break;
            }
        }
        fprintf(stderr, "restart: best=%d\n", best);
    }
    printf("best energy (min #mono triangles found): %d\n", best);
    return 1;
}
