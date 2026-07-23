/* Direct exhaustive Gallai-3 check via subset DP (no path enumeration).
 *
 * For each connected graph G (graph6, n <= 16) decide:
 *   do there exist three longest paths with empty common vertex intersection?
 *
 * reach[mask] = bitset over v of "exists path with vertex set exactly mask
 * ending at v".  Longest-path vertex sets = masks of max popcount with
 * reach[mask] != 0.  Then check triples of these masks for empty
 * intersection (fast skip if the AND of all masks is nonzero).
 *
 * Usage: direct_dp [-m] < graphs.g6
 *   -m : report the global minimum triple intersection (near-miss) found.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 20

static int n;
static uint32_t adj[MAXN];
static uint32_t *reach;      /* size 2^n, bitset of endpoints */
static int reach_size;

static int parse_g6(const char *s){
    int k = 0;
    n = s[k++] - 63;
    if (n < 1 || n > MAXN) return -1;
    memset(adj, 0, sizeof(adj));
    int bitpos = 0, need = n*(n-1)/2;
    int i = 0, j = 1;
    while (bitpos < need){
        int v = s[k++] - 63;
        if (v < 0) return -1;
        for (int b = 5; b >= 0 && bitpos < need; b--, bitpos++){
            if ((v>>b)&1){ adj[i] |= 1u<<j; adj[j] |= 1u<<i; }
            if (++i == j){ i = 0; j++; }
        }
    }
    return 0;
}

int main(int argc, char **argv){
    int report_nm = (argc > 1 && !strcmp(argv[1], "-m"));
    char line[256];
    long processed = 0, hits = 0;
    int global_nm = 999;
    char nm_g6[256] = "";
    reach = NULL; reach_size = 0;
    /* mask list for longest paths */
    int cap_masks = 1<<20;
    uint32_t *lp = malloc(cap_masks*sizeof(uint32_t));
    while (fgets(line, sizeof line, stdin)){
        char *nl = strchr(line, '\n'); if (nl) *nl = 0;
        if (!line[0]) continue;
        if (parse_g6(line)){ fprintf(stderr, "bad g6: %s\n", line); continue; }
        int full = 1<<n;
        if (full > reach_size){
            free(reach); reach = malloc(full*sizeof(uint32_t)); reach_size = full;
        }
        memset(reach, 0, full*sizeof(uint32_t));
        for (int v = 0; v < n; v++) reach[1<<v] = 1u<<v;
        int best_pc = 1;
        /* iterate masks in increasing order (any order with submask before
           supermask works: numeric order does since mask < mask|bit) */
        for (int mask = 1; mask < full; mask++){
            uint32_t ends = reach[mask];
            if (!ends) continue;
            int pc = __builtin_popcount(mask);
            if (pc > best_pc) best_pc = pc;
            uint32_t e = ends;
            while (e){
                int v = __builtin_ctz(e); e &= e-1;
                uint32_t ext = adj[v] & ~mask;
                while (ext){
                    int w = __builtin_ctz(ext); ext &= ext-1;
                    reach[mask | (1<<w)] |= 1u<<w;
                }
            }
        }
        /* collect longest-path vertex sets */
        int m = 0;
        uint32_t andall = 0xFFFFFFFF;
        for (int mask = 1; mask < full; mask++){
            if (reach[mask] && __builtin_popcount(mask) == best_pc){
                if (m < cap_masks) lp[m++] = (uint32_t)mask;
                andall &= mask;
            }
        }
        if (andall == 0){
            /* need real triple check */
            int found = 0, local_nm = 999;
            for (int i1 = 0; i1 < m && !found; i1++){
                for (int i2 = i1+1; i2 < m && !found; i2++){
                    uint32_t i12 = lp[i1] & lp[i2];
                    if (report_nm){
                        for (int i3 = i2+1; i3 < m; i3++){
                            int sz = __builtin_popcount(i12 & lp[i3]);
                            if (sz < local_nm) local_nm = sz;
                            if (sz == 0){ found = 1; break; }
                        }
                    } else {
                        if (i12 == 0) continue; /* impossible: two longest paths intersect, but harmless */
                        for (int i3 = i2+1; i3 < m; i3++){
                            if ((i12 & lp[i3]) == 0){ found = 1; break; }
                        }
                    }
                }
            }
            if (found){
                hits++;
                printf("HIT %s L=%d nmasks=%d\n", line, best_pc-1, m);
                fflush(stdout);
            } else if (report_nm && local_nm < global_nm){
                global_nm = local_nm; strcpy(nm_g6, line);
            }
        }
        processed++;
        if (processed % 10000000 == 0)
            fprintf(stderr, "... %ld graphs, %ld hits\n", processed, hits);
    }
    fprintf(stderr, "processed %ld graphs, %ld hits\n", processed, hits);
    if (report_nm)
        fprintf(stderr, "min triple intersection seen: %d on %s\n", global_nm, nm_g6);
    return 0;
}
