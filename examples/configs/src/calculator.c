/*
 * calculator.c — simple integer calculator used to demonstrate Bazel
 * named configurations (--config=debug / release / asan) and CodeQL analysis.
 *
 * Build variants (defined in .bazelrc):
 *   default : -Wall -Wextra -Wpedantic
 *   debug   : + -O0 -g -DDEBUG
 *   release : + -O2 -DNDEBUG --strip=always
 *   asan    : + -fsanitize=address (runtime memory-error detection)
 *
 * The #ifdef DEBUG block only compiles in the debug config, showing how
 * compile-time flags can gate diagnostic output.
 */

#include <stdio.h>
#include <stdlib.h>

/* Maximum number of operations kept in the history ring buffer. */
#define HISTORY_MAX 32

typedef struct {
    int    a;
    char   op;
    int    b;
    int    result;
    int    ok;   /* 1 = success, 0 = error (e.g. division by zero) */
} Record;

static Record s_history[HISTORY_MAX];
static int    s_count = 0;

/* Store one operation in the history (silently drops when full). */
static void record(int a, char op, int b, int result, int ok)
{
    if (s_count < HISTORY_MAX) {
        s_history[s_count].a      = a;
        s_history[s_count].op     = op;
        s_history[s_count].b      = b;
        s_history[s_count].result = result;
        s_history[s_count].ok     = ok;
        s_count++;
    }
}

/* Divide a by b; prints an error and returns 0 on division-by-zero. */
static int safe_divide(int a, int b)
{
    if (b == 0) {
        fprintf(stderr, "error: division by zero (%d / %d)\n", a, b);
        return 0;
    }
    return a / b;
}

/* Evaluate one binary operation. Returns the result; sets *ok=0 on error. */
static int calculate(int a, char op, int b, int *ok)
{
    *ok = 1;
    switch (op) {
        case '+': return a + b;
        case '-': return a - b;
        case '*': return a * b;
        case '/':
            if (b == 0) { *ok = 0; }
            return safe_divide(a, b);
        default:
            fprintf(stderr, "error: unknown operator '%c'\n", op);
            *ok = 0;
            return 0;
    }
}

/* Print the full operation history to stdout. Only compiled in debug builds
 * where it is actually called; omitting it in release avoids -Wunused-function
 * warnings produced by -Wextra. */
#ifdef DEBUG
static void print_history(void)
{
    printf("\n--- operation history (%d entries) ---\n", s_count);
    for (int i = 0; i < s_count; i++) {
        const Record *r = &s_history[i];
        if (r->ok) {
            printf("  [%2d]  %4d %c %4d  =  %d\n",
                   i, r->a, r->op, r->b, r->result);
        } else {
            printf("  [%2d]  %4d %c %4d  =  ERROR\n",
                   i, r->a, r->op, r->b);
        }
    }
}
#endif /* DEBUG */

int main(void)
{
    /* Test cases: {a, op, b} */
    static const struct { int a; char op; int b; } ops[] = {
        { 10, '+',  5 },
        { 10, '-',  3 },
        {  6, '*',  7 },
        { 22, '/',  7 },
        {100, '/', 10 },
        {  1, '/',  0 },   /* division by zero — handled gracefully */
        {  5, '+',  3 },
        {255, '-',255 },
    };

    int n = (int)(sizeof(ops) / sizeof(ops[0]));

#ifdef DEBUG
    fprintf(stderr, "[debug] running %d operations\n", n);
#endif

    for (int i = 0; i < n; i++) {
        int ok     = 0;
        int result = calculate(ops[i].a, ops[i].op, ops[i].b, &ok);
        record(ops[i].a, ops[i].op, ops[i].b, result, ok);

        if (ok) {
            printf("%4d %c %4d  =  %d\n",
                   ops[i].a, ops[i].op, ops[i].b, result);
        } else {
            printf("%4d %c %4d  =  ERROR\n",
                   ops[i].a, ops[i].op, ops[i].b);
        }
    }

#ifdef DEBUG
    print_history();
    fprintf(stderr, "[debug] done — %d ok, %d error(s)\n",
            s_count,
            n - s_count);
#endif

    return 0;
}
