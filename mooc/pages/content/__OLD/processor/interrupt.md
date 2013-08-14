Interrupt Flag
==============
The Interrupt flag is a bit in the [[status]] register that the programmer sets
in order to disable Interrupt Requests (IRQs) from the processor.

There are two types of interrupts on the 6502 - maskable Interrupt Requests
(IRQs) and Non-Maskable Interrupts. A maskable Interrupt is one where the
processor can *choose to ignore it* (which is done by setting the Interrupt
flag). IRQs are produced by the [[APU|apu]]. When an IRQ is serviced, the
processor begins a subroutine by jumping to memory location specified in the
[[vector table|vector_table]] at ```$FFFE```.

A non-maskable interrupt (NMI) can not be prevented by the processor - such an
interrupt will always cause the processor to begin the subroutine specified in
the vector table at ```$FFFA```. The [[PPU|ppu]] produces an NMI whenever the
screen is ready to refresh.

The programmer can set the Interrupt Flag using [[SEI|sei]] and can clear
it using [[CLI|cli]]. In general, it is a good idea to set the flag to
disable interrupts when the NES starts while waiting for the [[PPU|ppu]] to warm
up, and then clearing it if the programmer expects to handle interrupts from the
APU.

