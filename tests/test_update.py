"""Offline verification for the actual BF program, Git-patch parsing, markers."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from update_readme import (added_brainfuck_bytes, bf_tally, format_langs,
                           replace_marked)


class BFTests(unittest.TestCase):
    def test_counter_boundaries(self):
        for n in [0, 1, 9, 255, 256, 257, 4096, 32557, 65535, 65536, 100000]:
            with self.subTest(n=n):
                self.assertEqual(bf_tally(n), n)

    def test_marker_preservation(self):
        raw = 'before <!-- hours:start -->old<!-- hours:end --> after\n'
        self.assertEqual(replace_marked(raw, 'hours', '1,234 hrs'),
                         'before <!-- hours:start -->1,234 hrs<!-- hours:end --> after\n')
        with self.assertRaises(ValueError):
            replace_marked('no markers', 'hours', '1')

    def test_languages(self):
        stats = {'Java': 500, 'Brainfuck': 1000, 'Python': 200}
        self.assertTrue(format_langs(stats, 'preferred').startswith('`.bf`, `.py`'))
        self.assertTrue(format_langs(stats, 'usage').startswith('`.bf`, `.java`, `.py`'))

    def test_historical_added_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            def git(*args, env=None):
                return subprocess.run(['git', '-C', str(repo), *args],
                                      env=env, check=True, capture_output=True).stdout
            git('init', '-q')
            git('config', 'user.name', 'Test')
            git('config', 'user.email', 'test@example.invalid')
            path = repo / 'test.bf'
            path.write_text('+'*1024+'\n')
            git('add', '.')
            env = os.environ.copy()
            env.update({'GIT_AUTHOR_DATE':'2020-01-01T00:00:00+0000',
                        'GIT_COMMITTER_DATE':'2020-01-01T00:00:00+0000'})
            git('commit', '-qm', 'old', env=env)
            with path.open('a') as f:
                f.write('++\n')
            git('add', '.')
            git('commit', '-qm', 'new')
            total, recent = added_brainfuck_bytes(repo, int(time.time())-14*86400)
            self.assertEqual(total, 1025+3)
            self.assertEqual(recent, 3)


if __name__ == '__main__':
    unittest.main()
