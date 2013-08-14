Break Flag
==========
The Break Flag is a special flag that does not exist in the [[status]] register,
and only exists on the [[stack]]. Whenever the processor status is pushed to
the stack, either by means on the [[PHP|php]] operation or an [[interrupt]],
the Break flag at bit 4 indicates what operation was responsible for pushing
the status register.

The break flag is True whenever the [[PHP|php]] or [[BRK|brk]] opcode was used
to push the status register to the stack. If a hardware interrupt such as an
IRQ or NMI was responsible, the break flag will be False.

