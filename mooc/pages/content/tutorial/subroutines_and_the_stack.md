Subroutines and the Stack
=========================
Hopefully by this point, you've visited the playground and seen all of the
opcodes available on the 6502. However, while you may have noticed that there
is addition, subtraction, and even boolean operations, there are no opcodes for
arithmetic operations like multiplication or division. In this lesson, we're
going to teach you how to make "subroutines", which are miniature programs that
you can write and run in many different locations in your games and applications.


Writing a subroutine
--------------------
For this example, let's try to write a "multiply" subroutine. For this
subroutine, we will multiply the value in the X register by the value in the
Y register and leave the result in the A register. For this example, we won't
worry about errors that could occur, such as the answer being too large to fit
in a byte.

    multiply:
        STY $01     ; Store the value of the Y register in memory location $0001
        LDA #0      ; Zero out the Y register
        mloop:
          CPX #0    ; Compare X to 0
          BEQ mend  ; If X is 0, go to the end
          CLC       ; Clear carry flag before addition
          ADC $01   ; Add the value in memory location 1 to the A register
          DEX       ; Decrease X by 1
          JMP mloop ; Jump back up to the loop
    mend:           ;
        RST         ; Return from subroutine
        
Hopefully you understand why this program is correct by now. We start by taking
the Y register value and putting it in memory, and then adds that value to the A
register X times.

The final opcode, [[RST|rst]], tells the program to return back to where the
program was when the subroutine was called. In order to call this subroutine,
we would do something like:

    LDX #5          ; Load 5 in X
    LDY #3          ; Load 3 in Y
    JSR multiply    ; Perform X times Y. 15 will be in A.
    STA $200        ; Store the result in memory location $0200.

The RST command makes the program return to the execution of the program right
after the multiply subroutine was executed. But how does it know where to go?


The stack
---------
On the 6502, the memory from locations $0100 to $01FF are designated as the
[[stack]], a special location in memory. The stack is a special data structure
that is like a deck of cards: rather than simply writing directly to memory
locations in this area, data is added and removed from the "top" of the data
structure. The "top" of the stack is pointed to by a special register called
the "stack pointer". You can change and see the value of the stack pointer
by using the TXS and TSX opcodes, which move values betwen the X register and
stack pointer.

Whenever the [[JSR|jsr]] command is executed, the current value of the program
counter is **pushed** on the top of the stack. Whenever the [[RST]] command
is executed, the program **pops** the value off the top of the stack and jumps
to that location. This way, it's possible to call subroutines inside of other
subroutines and ensure that when the end, you always go back to the right place.


Side effects
------------
While the goal of our subroutine was to do the multiplication and have the result
stored in the A register, we have to be careful, since that's not all that
happens when we run our program. After the subroutine executes, there are also
some *side effects*. In this case, there are two:
 * The value of Y is stored in memory location $0001.
 * The value of the X register is changed to 0.
 
There are two ways to deal with side effects. The first way is to simply document
the side effects and warn the programmer about them. However, this limits the
way our subroutine can be used: for example, if the multiplication is being done
in a loop, we can't just let the X register equal 0 (that might be the counter).
So we have to think of another way.

The other option is to store important data in a separate location while the
subroutine runs and then restore that data after the subrotuine is over. We
could just designate a location in memory to use as a scratch area to store
temporary values, but we could also put information in the same place where
we put the return address of the program - the stack!

The [[PHA|pha]] and [[PLA|pla]] instructions allow you to push and pull the
value stored in the A register to and from the top of the stack. So if we wanted
to get rid of the side effect where the X register is set to zero, we could do
the following:

    multiply:
        TXA         ; Put the X register value in the A register
        PHA         ; Push the A register to the stack
        STY $01     ; Store the value of the Y register in memory location $0001
        LDA #0      ; Zero out the Y register
        mloop:
          CPX #0    ; Compare X to 0
          BEQ mend  ; If X is 0, go to the end
          CLC       ; Clear carry flag before addition
          ADC $01   ; Add the value in memory location 1 to the A register
          DEX       ; Decrease X by 1
          JMP mloop ; Jump back up to the loop
    mend:           ;
        PLA         ; Pull the old X value off the stack
        TAX         ; Put it back in X
        LDA $01     ; Put the answer in A
        RST         ; Return from subroutine

While it might be tempting to try to get rid of the other side effect, it's
actually not possible! At least, not without incurring an additional side effect.
This is a limitation of the 6502 - because we want to put the result of the
subroutine in the A register, we have to find a place to store the answer while
we use the A register to pull other data off of the stack.

For this reason, you almost can't avoid using some space on the zero page as a
scratch location to store information temporarily, but as long as you document
how you are using your space, you can avoid unintended side effects from
ruining your programs.

 * [[Next Tutorial|nes_hardware]]
 * [[Back to Table of Contents|tutorial]]
 
