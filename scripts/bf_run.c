/* Eight-instruction Brainfuck interpreter. Byte cells wrap modulo 256.
 * Standard input supplies data; standard output receives raw bytes.
 * Deliberately no JavaScript, Node.js or external interpreter dependency.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define TAPE_SIZE 65536
#define SOURCE_LIMIT (1024 * 1024)

static void fail(const char *message) {
    fprintf(stderr, "brainfuck: %s\n", message);
    exit(EXIT_FAILURE);
}

int main(int argc, char **argv) {
    if (argc != 2) fail("usage: bf_run FILE.bf");
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return EXIT_FAILURE; }
    char *code = malloc(SOURCE_LIMIT + 1);
    size_t *match = calloc(SOURCE_LIMIT + 1, sizeof(size_t));
    size_t *stack = malloc((SOURCE_LIMIT + 1) * sizeof(size_t));
    unsigned char *tape = calloc(TAPE_SIZE, 1);
    if (!code || !match || !stack || !tape) fail("out of memory");
    size_t n = fread(code, 1, SOURCE_LIMIT + 1, f);
    if (ferror(f)) fail("cannot read program");
    fclose(f);
    if (n > SOURCE_LIMIT) fail("program too long");
    size_t top = 0;
    for (size_t i = 0; i < n; ++i) {
        if (code[i] == '[') stack[top++] = i;
        else if (code[i] == ']') {
            if (!top) fail("unmatched closing bracket");
            size_t j = stack[--top];
            match[j] = i;
            match[i] = j;
        }
    }
    if (top) fail("unmatched opening bracket");
    size_t ptr = 0;
    for (size_t ip = 0; ip < n; ++ip) {
        switch (code[ip]) {
        case '>': if (++ptr == TAPE_SIZE) fail("pointer beyond tape"); break;
        case '<': if (!ptr) fail("pointer before tape"); --ptr; break;
        case '+': ++tape[ptr]; break;
        case '-': --tape[ptr]; break;
        case '.': if (putchar(tape[ptr]) == EOF) fail("output failure"); break;
        case ',': {
            int byte = getchar();
            tape[ptr] = (byte == EOF ? 0 : (unsigned char)byte);
            break;
        }
        case '[': if (!tape[ptr]) ip = match[ip]; break;
        case ']': if (tape[ptr]) ip = match[ip]; break;
        default: break;  /* comments are legal */
        }
    }
    if (fflush(stdout) == EOF) fail("output flush failure");
    free(code); free(match); free(stack); free(tape);
    return 0;
}
