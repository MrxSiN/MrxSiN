# Brainfuck 24 bit unary tally
# Three bytes of arithmetic because a regular integer was apparently too generous
# Input is N bytes with value 1 followed by a zero byte
# Output is exactly three raw bytes in little endian order
# Cell 0 is the input byte and loop guard
# Cells 1 2 and 3 are the low middle and high digits
# Cell 4 is the carry flag
# Cells 5 and 6 are temporary cells which have seen things
# The comments contain none of the eight Brainfuck commands on purpose
# One misplaced symbol here is not a typo but a feature nobody requested

# Consume the first unary unit or stop immediately on zero
,
[
    # Increment the low digit and arm the possible carry
    >+>>>+<<<

    # Copy the low digit into scratch to see if it survived the increment
    # Restore the digit after the inspection because this is not a democracy
    [->>>>+>+<<<<<]
    >>>>[-<<<<+>>>>]
    >[<<[-]>>[-]]
    <<

    # A surviving carry flag means the low digit wrapped to zero
    # Advance the middle digit and make the same terrible life decision again
    [-<<+>>+
        <<[->>>+>+<<<<]
        >>>[-<<<+>>>]
        >[<<[-]>>[-]]
        <<

        # If the middle digit also wrapped then increment the high digit
        # Three bytes of range and absolutely no emotional support
        [-<+>]
    ]

    # Return to input and ask for another byte of suffering
    <<<<,
]

# Export the low middle and high digits as raw binary
# Decimal formatting is a problem for someone who still believes in functions
>.>.>.
