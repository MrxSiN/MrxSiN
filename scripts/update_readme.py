#!/usr/bin/env python3
"""Refresh MrxSiN README markers without JavaScript or Node.js.

Architecture:
- Python standard library is ONLY the I/O adapter (Git/GitHub/README rendering).
- scripts/tally.bf performs the hours accumulation from unary one-hour units.
- scripts/bf_run.c is a tiny native Brainfuck interpreter, built before running.

Definition used here: committed BF bytes = UTF-8 byte length of lines ADDED
inside *.bf / *.b / *.brainfuck patches on non-merge commits in public owned
repositories, including one newline for each new line. It is NOT the size of
all BF files currently at HEAD. Recent = added lines on commits with committer
timestamp in the preceding 14 * 24 hours. Reverted changes are not subtracted.
This is a documented reconstruction, not a verified copy of original JS logic.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'scripts'
README = ROOT / 'README.md'
LANGS = [('Brainfuck', 'bf'), ('Python', 'py'), ('C', 'c'),
         ('Kotlin', 'kt'), ('Java', 'java'), ('C#', 'cs')]
FILE_GLOBS = ('*.bf', '*.b', '*.brainfuck')
REVIEW_DAYS = 14
MAX_HOURS = (1 << 24) - 1


def github_json(path: str, token: str | None):
    req = Request('https://api.github.com' + path, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'mrxsin-brainfuck-readme',
        'X-GitHub-Api-Version': '2022-11-28',
        **({'Authorization': f'Bearer {token}'} if token else {}),
    })
    with urlopen(req, timeout=40) as res:
        return json.load(res)


def owned_public_repos(owner: str, token: str | None):
    repos = []
    for page in range(1, 21):
        data = github_json(f'/users/{owner}/repos?per_page=100&page={page}&type=owner', token)
        if not isinstance(data, list):
            raise RuntimeError(f'GitHub returned invalid repository response on page {page}')
        repos.extend(r for r in data if not r.get('fork') and not r.get('private')
                     and r.get('owner', {}).get('login', '').casefold() == owner.casefold())
        if len(data) < 100:
            break
    else:
        raise RuntimeError('Repository pagination unexpectedly exceeded 2000 entries')
    return sorted(repos, key=lambda r: r['name'].casefold())


def github_language_bytes(repos, token: str | None):
    totals: dict[str, int] = {}
    for repo in repos:
        langs = github_json(f'/repos/{repo["full_name"]}/languages', token)
        for name, byte_count in langs.items():
            totals[name] = totals.get(name, 0) + int(byte_count)
    return totals


def format_langs(language_bytes: dict[str, int], ranking: str):
    entries = LANGS
    if ranking == 'usage':
        entries = sorted(entries,
                         key=lambda row: -language_bytes.get(row[0], 0))
    return ', '.join(f'`.{ext}`' for _, ext in entries)


def added_brainfuck_bytes(repo: Path, since: int) -> tuple[int, int]:
    """Read real Git patches, not GitHub API addition line counts.

    The sentinel is a format *line* at each commit boundary. Newline bytes are
    counted when reconstructing added lines. Binary patches are unsupported,
    and are explicitly rejected rather than producing understated totals.
    """
    cmd = ['git', '-C', str(repo), 'log', '--all', '--no-merges',
           '--no-ext-diff', '--no-textconv', '--no-renames',
           '--format=BF_COMMIT_TIMESTAMP_%ct', '-p', '--', *FILE_GLOBS]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None
    total = recent = 0
    timestamp = 0
    inside_hunk = False
    last_added = False
    try:
        for raw in proc.stdout:
            line = raw.rstrip(b'\n')
            if line.startswith(b'BF_COMMIT_TIMESTAMP_'):
                timestamp = int(line[len(b'BF_COMMIT_TIMESTAMP_'):])
                inside_hunk = False
                last_added = False
            elif line.startswith(b'diff --git '):
                inside_hunk = False
                last_added = False
            elif line.startswith((b'GIT binary patch', b'Binary files ')):
                raise ValueError(f'Binary Brainfuck file in {repo}; cannot count added bytes precisely')
            elif line.startswith(b'@@ '):
                inside_hunk = True
                last_added = False
            elif inside_hunk and line.startswith(b'+'):
                added = len(line[1:]) + 1
                total += added
                if timestamp >= since:
                    recent += added
                last_added = True
            elif inside_hunk and line == b'\\ No newline at end of file':
                if last_added:
                    total -= 1
                    if timestamp >= since:
                        recent -= 1
                last_added = False
            else:
                last_added = False
    except BaseException:
        proc.kill()
        proc.communicate()
        raise
    proc.stdout.close()
    err = proc.stderr.read() if proc.stderr else b''
    if proc.stderr:
        proc.stderr.close()
    result = proc.wait()
    if result:
        raise RuntimeError(f'git log failed ({repo}): {err.decode(errors="replace")[:300]}')
    return total, recent


def cloned_stats(repos, since: int, clone_root: Path) -> tuple[int, int]:
    total = recent = 0
    for i, repo in enumerate(repos):
        full_name = repo['full_name']
        print(f'Inspecting {i+1}/{len(repos)}: {full_name}', flush=True)
        dest = clone_root / f'repo-{i:03d}.git'
        # Public HTTPS clones deliberately avoid inserting tokens in process args.
        safe_name = re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', full_name)
        if not safe_name:
            raise ValueError(f'Unsafe GitHub repository name: {full_name}')
        subprocess.run(['git', 'clone', '--bare', '--quiet', '--filter=blob:none',
                        f'https://github.com/{full_name}.git', str(dest)],
                       check=True, timeout=900)
        a, b = added_brainfuck_bytes(dest, since)
        total += a
        recent += b
    return total, recent


def bf_tally(one_hour_units: int) -> int:
    if not 0 <= one_hour_units <= MAX_HOURS:
        raise ValueError(f'Brainfuck 24-bit tally supports 0..{MAX_HOURS} hours')
    binary = SCRIPTS / 'bf_run'
    if not binary.is_file():
        raise FileNotFoundError('Compile first: cc -O2 -o scripts/bf_run scripts/bf_run.c')
    # ONE input byte per completed KB; the BF program counts, carries and emits
    # three little-endian bytes. The host never substitutes a Python sum.
    result = subprocess.run([str(binary), str(SCRIPTS / 'tally.bf')],
                            input=b'\x01' * one_hour_units + b'\x00',
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            check=True, timeout=180)
    if len(result.stdout) != 3:
        raise ValueError(f'BF returned {len(result.stdout)} bytes instead of 3')
    return int.from_bytes(result.stdout, 'little')


def replace_marked(text: str, name: str, value: str) -> str:
    start = f'<!-- {name}:start -->'
    end = f'<!-- {name}:end -->'
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f'Expected exactly one valid pair of {name} README markers')
    pattern = re.compile(re.escape(start) + r'.*?' + re.escape(end), flags=re.DOTALL)
    return pattern.sub(lambda _m: start + value + end, text, count=1)


def main():
    parser = argparse.ArgumentParser(description='Update README via a Brainfuck tally')
    parser.add_argument('--owner', default='MrxSiN')
    parser.add_argument('--local-repo', action='append', type=Path,
                        help='Use local Git repository/repositories instead of cloning from GitHub')
    parser.add_argument('--langs', choices=['preferred', 'usage', 'unchanged'],
                        default='preferred',
                        help='Preferred maintains current regret order; usage sorts by GitHub bytes')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--readme', type=Path, default=README)
    args = parser.parse_args()
    since = int(time.time()) - REVIEW_DAYS * 86400
    original = args.readme.read_text(encoding='utf-8')

    if args.local_repo:
        total_bytes = recent_bytes = 0
        for repo in args.local_repo:
            a, b = added_brainfuck_bytes(repo, since)
            total_bytes += a
            recent_bytes += b
        # Local fixture mode need not access GitHub at all.
        repos = []
    else:
        token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
        repos = owned_public_repos(args.owner, token)
        if not repos:
            raise RuntimeError('No public owned repositories found; refusing to overwrite README')
        with tempfile.TemporaryDirectory(prefix='readme-bf-') as temp:
            total_bytes, recent_bytes = cloned_stats(repos, since, Path(temp))

    # Floor KB after accumulating bytes across all repositories, not per file.
    total_hours = bf_tally(total_bytes // 1024)
    recent_hours = bf_tally(recent_bytes // 1024)
    hours_line = f'{total_hours:,} hrs on record ({recent_hours:,} hrs at review time)'
    edited = replace_marked(original, 'hours', hours_line)

    if args.langs != 'unchanged':
        if not args.local_repo:
            measured_langs = github_language_bytes(repos, token)
            content = format_langs(measured_langs, args.langs)
        else:
            # Local preview keeps language list untouched rather than using fake data.
            content = None
        if content is not None:
            edited = replace_marked(edited, 'langs', content)

    print(f'Brainfuck hours: total={total_hours:,}, recent={recent_hours:,} '
          f'(source added bytes: total={total_bytes:,}, recent={recent_bytes:,})')
    if args.dry_run:
        print(f'Dry-run: README would change: {edited != original}')
    elif edited != original:
        args.readme.write_text(edited, encoding='utf-8')
        print('README updated')
    else:
        print('README unchanged')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, FileNotFoundError, subprocess.SubprocessError) as exc:
        print(f'Update failed without intentional README overwrite: {exc}', file=sys.stderr)
        sys.exit(1)
