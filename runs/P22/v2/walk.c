/* Focused random-walk (WalkSAT-style) search for a zero-monochromatic-triangle
 * 2-coloring of E(G127). Maintains list of mono triangles; each step picks a
 * random mono triangle and flips one of its 3 edges (greedy with noise).
 * Usage: ./walk <seconds> <seed> [noise_pct=15]
 */
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>

#define NE 2667
#define NT 9779

static int tri[NT][3];
static int etris[NE][30]; static int ecnt[NE];
static int color[NE];
static int mono[NT];
static int monolist[NT], monopos[NT], nmono; /* mono triangle set */

static unsigned long long rng_s;
static inline unsigned long long rng(void){
    rng_s ^= rng_s << 13; rng_s ^= rng_s >> 7; rng_s ^= rng_s << 17; return rng_s;
}

static inline int tri_mono(int t){
    return color[tri[t][0]] == color[tri[t][1]] && color[tri[t][1]] == color[tri[t][2]];
}

static void set_mono(int t, int m){
    if (m == mono[t]) return;
    mono[t] = m;
    if (m){ monopos[t] = nmono; monolist[nmono++] = t; }
    else {
        int p = monopos[t], last = monolist[--nmono];
        monolist[p] = last; monopos[last] = p;
    }
}

static void flip(int e){
    color[e] ^= 1;
    for (int i = 0; i < ecnt[e]; i++){
        int t = etris[e][i];
        set_mono(t, tri_mono(t));
    }
}

static int delta(int e){
    int d = 0;
    for (int i = 0; i < ecnt[e]; i++){
        int t = etris[e][i];
        color[e] ^= 1; int after = tri_mono(t); color[e] ^= 1;
        d += after - mono[t];
    }
    return d;
}

int main(int argc, char **argv){
    double secs = argc > 1 ? atof(argv[1]) : 60;
    rng_s = argc > 2 ? strtoull(argv[2], 0, 10) : 1234567891ULL;
    int noise = argc > 3 ? atoi(argv[3]) : 15;

    FILE *f = fopen("g127.tri_edges", "r");
    if (!f){ fprintf(stderr, "missing g127.tri_edges\n"); return 2; }
    for (int t = 0; t < NT; t++){
        if (fscanf(f, "%d %d %d", &tri[t][0], &tri[t][1], &tri[t][2]) != 3) return 2;
        for (int j = 0; j < 3; j++) etris[tri[t][j]][ecnt[tri[t][j]]++] = t;
    }
    fclose(f);

    int best = NT + 1;
    time_t start = time(0);
    unsigned long long steps = 0;
    while (time(0) - start < (time_t)secs){
        for (int e = 0; e < NE; e++) color[e] = rng() & 1;
        nmono = 0;
        for (int t = 0; t < NT; t++){ mono[t] = 0; }
        for (int t = 0; t < NT; t++) set_mono(t, tri_mono(t));
        for (unsigned long long it = 0; it < 200000000ULL && nmono; it++, steps++){
            int t = monolist[rng() % nmono];
            int e;
            if ((int)(rng() % 100) < noise) e = tri[t][rng() % 3];
            else {
                int bd = 1 << 30; e = tri[t][0];
                for (int j = 0; j < 3; j++){
                    int d = delta(tri[t][j]);
                    if (d < bd){ bd = d; e = tri[t][j]; }
                }
            }
            flip(e);
            if (nmono < best){
                best = nmono;
                {
                    char name[64];
                    snprintf(name, sizeof name, "walk_best_%llu.txt",
                             (unsigned long long)strtoull(argv[2] ? argv[2] : "0", 0, 10));
                    FILE *o = fopen(name, "w");
                    fprintf(o, "c nmono %d\n", best);
                    for (int i = 0; i < NE; i++) fprintf(o, "%d", color[i]);
                    fprintf(o, "\n");
                    fclose(o);
                }
                if (best == 0){
                    FILE *o = fopen("best_coloring.txt", "w");
                    for (int i = 0; i < NE; i++) fprintf(o, "%d %d\n", i, color[i]);
                    fclose(o);
                    printf("ZERO-MONO COLORING FOUND after %llu steps\n", steps);
                    return 0;
                }
            }
            if ((it & 0xffffff) == 0 && time(0) - start >= (time_t)secs) break;
        }
        fprintf(stderr, "restart: best=%d steps=%llu\n", best, steps);
    }
    printf("best (min #mono triangles): %d\n", best);
    return 1;
}
