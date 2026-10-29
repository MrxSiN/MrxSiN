"""Development-only Brainfuck source generator.

The generated .bf source is checked in; GitHub Actions never runs this tool.
Generates an eight-instruction program that increments a 24-bit little-endian
counter once per nonzero input byte, stopping at the first zero/EOF.
"""
from pathlib import Path

class BF:
    def __init__(self):
        self.code = []
        self.pointer = 0

    def goto(self, index):
        d = index - self.pointer
        self.code.append(('>' if d > 0 else '<') * abs(d))
        self.pointer = index

    def op(self, opcode):
        self.code.append(opcode)

    def loop(self, cell, func):
        self.goto(cell)
        self.op('[')
        func()
        self.goto(cell)
        self.op(']')

    def increment_with_carry(self, digit):
        """Increment digit (mod 256), then recursively carry on overflow.

        Cells 4=flag, 5=copy1, 6=copy2 are transient and always restored to 0.
        This deliberately implements numeric arithmetic inside Brainfuck.
        """
        self.goto(digit)
        self.op('+')
        if digit == 3:
            return
        flag, copy1, copy2 = 4, 5, 6
        self.goto(flag)
        self.op('+')
        def copy_out():
            self.op('-')
            self.goto(copy1); self.op('+')
            self.goto(copy2); self.op('+')
        self.loop(digit, copy_out)
        def restore():
            self.op('-')
            self.goto(digit); self.op('+')
        self.loop(copy1, restore)
        def clear_flag_if_nonzero():
            self.goto(flag); self.op('[-]')
            self.goto(copy2); self.op('[-]')
        self.loop(copy2, clear_flag_if_nonzero)
        def do_carry():
            self.op('-')
            self.increment_with_carry(digit + 1)
        self.loop(flag, do_carry)

    def build(self):
        self.goto(0); self.op(',')
        def process():
            self.increment_with_carry(1)
            self.goto(0); self.op(',')
        self.loop(0, process)
        for i in [1,2,3]:
            self.goto(i); self.op('.')
        return ''.join(self.code)

if __name__ == '__main__':
    program = BF().build()
    assert program.count('[') == program.count(']')
    path = Path(__file__).with_name('tally.bf')
    path.write_text(program+'\n', encoding='ascii')
    print(f'wrote {path}: {len(program)} instructions')
