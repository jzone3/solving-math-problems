/* Enumerate ALL 2-colorings of E(K_n) (n<=9), compute the set ("mask") of
 * monochromatic triples, and write out distinct masks with popcount <= THRESH.
 * Usage: ./enum_mono n thresh nthreads outfile
 * Each output line: hex mask (little-endian over triple index order of
 * combinations(range(n),3) lexicographic). Colorings are enumerated with the
 * first edge fixed to color 0 (complement symmetry).
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>

static int n, thresh, nthreads;
static int ne, nt;
static int tri_e[130][3]; /* edge indices of each triple */

#define MAXKEEP (1u<<26)
typedef unsigned __int128 u128;
typedef struct { u128 *arr; size_t cnt, cap; pthread_mutex_t mu; } bag_t;
static bag_t bag;

static void bag_add(u128 m) {
    pthread_mutex_lock(&bag.mu);
    if (bag.cnt == bag.cap) { bag.cap *= 2; bag.arr = realloc(bag.arr, bag.cap*sizeof(u128)); }
    bag.arr[bag.cnt++] = m;
    pthread_mutex_unlock(&bag.mu);
}

typedef struct { uint64_t start, end; } job_t;

static void *work(void *arg) {
    job_t *jb = (job_t *)arg;
    for (uint64_t c = jb->start; c < jb->end; c++) {
        uint64_t col = c << 1; /* edge 0 fixed to 0 */
        u128 mask = 0;
        int pc = 0;
        for (int t = 0; t < nt; t++) {
            int b1 = (col >> tri_e[t][0]) & 1;
            int b2 = (col >> tri_e[t][1]) & 1;
            int b3 = (col >> tri_e[t][2]) & 1;
            if (b1 == b2 && b2 == b3) {
                mask |= ((u128)1) << t;
                if (++pc > thresh) break;
            }
        }
        if (pc <= thresh) bag_add(mask);
    }
    return NULL;
}

static int cmp128(const void *a, const void *b) {
    u128 x = *(const u128 *)a, y = *(const u128 *)b;
    return x < y ? -1 : x > y;
}

int main(int argc, char **argv) {
    n = atoi(argv[1]); thresh = atoi(argv[2]); nthreads = atoi(argv[3]);
    ne = n*(n-1)/2;
    /* edge index map */
    int eid[16][16]; int k = 0;
    for (int i = 0; i < n; i++) for (int j = i+1; j < n; j++) eid[i][j] = k++;
    nt = 0;
    for (int a = 0; a < n; a++) for (int b = a+1; b < n; b++) for (int c = b+1; c < n; c++) {
        tri_e[nt][0] = eid[a][b]; tri_e[nt][1] = eid[a][c]; tri_e[nt][2] = eid[b][c]; nt++;
    }
    if (nt > 120) { fprintf(stderr, "nt too large\n"); return 1; }
    bag.cap = 1<<20; bag.arr = malloc(bag.cap*sizeof(u128)); bag.cnt = 0;
    pthread_mutex_init(&bag.mu, NULL);
    uint64_t total = 1ULL << (ne - 1);
    pthread_t th[64]; job_t jobs[64];
    for (int i = 0; i < nthreads; i++) {
        jobs[i].start = total*i/nthreads; jobs[i].end = total*(i+1)/nthreads;
        pthread_create(&th[i], NULL, work, &jobs[i]);
    }
    for (int i = 0; i < nthreads; i++) pthread_join(th[i], NULL);
    /* dedupe */
    qsort(bag.arr, bag.cnt, sizeof(u128), cmp128);
    FILE *f = fopen(argv[4], "w");
    u128 prev = ~(u128)0; size_t uniq = 0;
    for (size_t i = 0; i < bag.cnt; i++) {
        if (bag.arr[i] != prev) {
            fprintf(f, "%llx:%llx\n", (unsigned long long)(bag.arr[i]>>64),
                    (unsigned long long)bag.arr[i]);
            prev = bag.arr[i]; uniq++;
        }
    }
    fclose(f);
    fprintf(stderr, "n=%d thresh=%d: %zu kept, %zu unique\n", n, thresh, bag.cnt, uniq);
    return 0;
}
