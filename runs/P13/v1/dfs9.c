/* Independent exhaustive search for a (9,6,1)-PMD, assuming (provably WLOG)
 * that the 12 block sets are the complements of the 12 lines of AG(2,3).
 * Enumerates all cyclic orderings (min element fixed at position 0, 5! = 120
 * per block) of each block with full backtracking over the "ordered pair used
 * at distance t" constraint. Prints the design if found, else "NO PMD".
 * Also counts search nodes. cc -O2 dfs9.c -o dfs9 */
#include <stdio.h>
#include <string.h>

static int blocks[12][6];
static int nblocks = 12;
/* used[t-1][x][y] */
static char used[5][9][9];
static int order[12][6];
static long long nodes = 0;

static int lines[12][3];

static void build_blocks(void) {
    int nl = 0, seen[9][9] = {{0}};
    for (int a = 0; a < 9; a++) for (int b = a + 1; b < 9; b++) {
        if (seen[a][b]) continue;
        int x3 = ((-(a % 3) - (b % 3)) % 3 + 3) % 3;
        int y3 = ((-(a / 3) - (b / 3)) % 3 + 3) % 3;
        int c = y3 * 3 + x3;
        int t[3] = {a, b, c}, tmp;
        for (int i = 0; i < 3; i++) for (int j = i + 1; j < 3; j++)
            if (t[j] < t[i]) { tmp = t[i]; t[i] = t[j]; t[j] = tmp; }
        seen[t[0]][t[1]] = seen[t[0]][t[2]] = seen[t[1]][t[2]] = 1;
        lines[nl][0] = t[0]; lines[nl][1] = t[1]; lines[nl][2] = t[2];
        nl++;
    }
    for (int l = 0; l < 12; l++) {
        int k = 0;
        for (int p = 0; p < 9; p++)
            if (p != lines[l][0] && p != lines[l][1] && p != lines[l][2])
                blocks[l][k++] = p;
    }
}

static int place(int j, const int *ord) {
    /* try to mark all 30 slots; on conflict unmark and fail */
    int marked[30][3], nm = 0;
    for (int t = 1; t <= 5; t++)
        for (int p = 0; p < 6; p++) {
            int x = ord[p], y = ord[(p + t) % 6];
            if (used[t - 1][x][y]) {
                while (nm--) used[marked[nm][0]][marked[nm][1]][marked[nm][2]] = 0;
                return 0;
            }
            used[t - 1][x][y] = 1;
            marked[nm][0] = t - 1; marked[nm][1] = x; marked[nm][2] = y; nm++;
        }
    return 1;
}

static void unplace(const int *ord) {
    for (int t = 1; t <= 5; t++)
        for (int p = 0; p < 6; p++)
            used[t - 1][ord[p]][ord[(p + t) % 6]] = 0;
}

static int dfs(int j) {
    if (j == nblocks) return 1;
    int *bs = blocks[j];
    int perm[6], rest[5];
    for (int i = 0; i < 5; i++) rest[i] = bs[i + 1];
    perm[0] = bs[0];
    /* enumerate permutations of rest via Heap's algorithm (recursive simple) */
    int idx[5] = {0, 1, 2, 3, 4};
    /* simple recursive permutation */
    int stack_ok = 0;
    int c[5] = {0};
    int arr[5]; memcpy(arr, rest, sizeof(arr));
    /* first permutation */
    for (;;) {
        nodes++;
        for (int i = 0; i < 5; i++) perm[i + 1] = arr[i];
        if (place(j, perm)) {
            memcpy(order[j], perm, sizeof(perm));
            if (dfs(j + 1)) return 1;
            unplace(perm);
        }
        /* next permutation via iterative Heap */
        int i = 0;
        for (i = 0; i < 5;) {
            if (c[i] < i) {
                if (i % 2 == 0) { int t = arr[0]; arr[0] = arr[i]; arr[i] = t; }
                else { int t = arr[c[i]]; arr[c[i]] = arr[i]; arr[i] = t; }
                c[i]++;
                break;
            } else { c[i++] = 0; }
        }
        if (i == 5) break;
    }
    (void)idx; (void)stack_ok;
    return 0;
}

int main(void) {
    build_blocks();
    if (dfs(0)) {
        printf("FOUND (9,6,1)-PMD:\n");
        for (int j = 0; j < 12; j++) {
            for (int p = 0; p < 6; p++) printf("%d ", order[j][p]);
            printf("\n");
        }
    } else {
        printf("NO PMD: exhaustive search over AG(2,3)-complement block sets "
               "found no valid cyclic ordering. nodes=%lld\n", nodes);
    }
    return 0;
}
