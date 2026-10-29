# Brainfuck README automation — installation and accuracy notes

## Status / provenance

This is a **reconstructed working replacement**, NOT a literal clone or exact
translation of the original JavaScript. Network isolation prevented `git clone`
and reading the original source scripts. `README.md` was reconstructed from the
publicly displayed raw README on 2026-10-29; other files are newly authored.
Do not claim this preserves old numeric calculation semantics until comparing
against the original JavaScript.

## Components

- `scripts/tally.bf`: genuine 8-instruction Brainfuck **24-bit counter**. It
  consumes one nonzero byte for each completed KB and returns a three-byte
  binary value. No JavaScript or Node.js.
- `scripts/bf_run.c`: minimal standard Brainfuck interpreter. Compiles with GCC. Git checkout uses native Git, not the JavaScript-based `actions/checkout`.
- `scripts/update_readme.py`: **Python I/O adapter**, collecting public Git
  history and metadata and patching the README between existing HTML markers.
  The adapter does not implement the hours tally; it invokes Brainfuck.
- `.github/workflows/update-profile-brainfuck.yml`: daily workflow plus manual
  trigger. Tests before updating and commits only when content changes.
- `tests/test_update.py`: offline tests of real Brainfuck and parser.

## Accounting method used by this replacement

- Repositories: public, owned, nonfork GitHub repos under `MrxSiN`.
- Hours on record: for every nonmerge commit in the cloned histories, count
  **added lines** in `*.bf`, `*.b`, `*.brainfuck` Git diffs, including their
  newline bytes (where present). Total bytes across all repos divided by 1024,
  floored once; the Brainfuck tally then counts the completed KB units.
- Review hours: same measure, but only commits with committer timestamp
  within the past 14 x 24 hours. This is a rolling period in UTC.
- Reverts do **not** subtract historical additions; merges are excluded;
  renames may appear as additions if Git represents them as new files;
  binary patches raise an error. Forks and private repositories are excluded.
- Languages: the six existing language labels remain in the original order.
  Use `--langs usage` to sort them by GitHub-reported repository language bytes.

**These rules may not be identical to the previous JavaScript algorithm.**
Commit history scanning can also be much slower than an API-only script.

## Merge into your actual clone

1. On a machine with GitHub access, run
   `git clone https://github.com/MrxSiN/MrxSiN.git`.
2. Copy `scripts/tally.bf`, `scripts/bf_run.c`, `scripts/update_readme.py`,
   `tests/test_update.py` and `.github/workflows/update-profile-brainfuck.yml`
   into that clone. The full reconstructed `README.md` is supplied only for
   comparison. **Keep your latest upstream README.md**.
3. **Disable or remove the old JavaScript update workflow(s)** after verifying
   which files invoke them. Otherwise the two scheduled jobs can fight.
4. Test:

   ```sh
   cc -O2 -Wall -Wextra -Werror -o scripts/bf_run scripts/bf_run.c
   python3 -m unittest discover -s tests -v
   python3 scripts/update_readme.py --local-repo . --dry-run
   ```

5. Commit/push your changes. GitHub Actions needs `contents: write` permission
   and an enabled Actions runner. Use `workflow_dispatch` for the first run.
6. Compare the hours with the original JavaScript result before switching off
   the existing job permanently. Do not publish these as identical accounting
   algorithms without that comparison.

The workflow is deliberately not auto-published. No repo settings, remote
branches or GitHub files were modified by creating this bundle.
