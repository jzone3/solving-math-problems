/* Exhaustive search for <t>-fixed integer vectors on Z_m with entries in
 * [-d,d], squared norm k, and flat periodic autocorrelation.
 * Usage: ./cw_fold m d k t [timeout_seconds]
 * Prints "COUNT <c>" if the search completed, or "TIMEOUT" if it hit the
 * wall-clock limit.  Exhaustive DFS over orbit coefficient assignments with
 * norm pruning; flat check at leaves with early exit.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int m, d, k, t;
static int orb_of[1024];          /* element -> orbit index */
static int sizes[1024], no = 0;
static int reps[1024][1024];      /* orbit -> elements */
static long long suffix[1030];
static int cs[1030];
static int w[1024];
static long long cnt = 0, leaves = 0;
static time_t deadline;
static int timed_out = 0;

static int flat(void) {
    for (int s = 1; s < m; s++) {
        long long acc = 0;
        for (int i = 0; i < m; i++) acc += (long long)w[i] * w[(i + s) % m];
        if (acc) return 0;
    }
    return 1;
}

static void dfs(int pos, long long norm) {
    if (timed_out) return;
    if (norm > k || norm + suffix[pos] < k) return;
    if (pos == no) {
        if (norm != k) return;
        if ((++leaves & 0xFFFF) == 0 && time(NULL) > deadline) {
            timed_out = 1; return;
        }
        for (int i = 0; i < no; i++)
            for (int j = 0; j < sizes[i]; j++) w[reps[i][j]] = cs[i];
        if (flat()) {
            cnt++;
            printf("SOLUTION:");
            for (int i = 0; i < no; i++) printf(" %d", cs[i]);
            printf("\n");
        }
        return;
    }
    for (int c = -d; c <= d; c++) {
        cs[pos] = c;
        dfs(pos + 1, norm + (long long)c * c * sizes[pos]);
        if (timed_out) return;
    }
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s m d k t [timeout]\n", argv[0]); return 2; }
    m = atoi(argv[1]); d = atoi(argv[2]); k = atoi(argv[3]); t = atoi(argv[4]);
    int tmo = argc > 5 ? atoi(argv[5]) : 600;
    deadline = time(NULL) + tmo;
    int seen[1024]; memset(seen, 0, sizeof(seen));
    for (int x = 0; x < m; x++) {
        if (seen[x]) continue;
        int y = x, s = 0;
        while (!seen[y]) { seen[y] = 1; reps[no][s++] = y; y = (int)(((long long)y * t) % m); }
        sizes[no] = s;
        for (int j = 0; j < s; j++) orb_of[reps[no][j]] = no;
        no++;
    }
    suffix[no] = 0;
    for (int i = no - 1; i >= 0; i--)
        suffix[i] = suffix[i + 1] + (long long)d * d * sizes[i];
    dfs(0, 0);
    if (timed_out) { printf("TIMEOUT\n"); return 1; }
    printf("COUNT %lld\n", cnt);
    return 0;
}
