Registers and Memory
====================

What is a Byte?
---------------
On the NES, data is read, written, and moved in packages called **bytes**.
A byte is a unit of data that is made up of 8 **bits**, where each bit can either
be a 1 or a 0 (bit stands for "binary digit"). Let's look at the byte
```10110001``` as an example.

    MSB                         LSB
     7   6   5   4   3   2   1   0      MSB = Most significant byte
     1   0   1   1   0   0   0   1      LSB = Least significant byte

As you hopefully remember from the tutorial on [[binary numbers|binary_numbers]],
this byte has the value 177 in decimal ($B1 in hex). A byte is essentially a
number between 0 and 255. This means that the rightmost bit (bit 0) has the
lowest value, and the leftmost bit (bit 7) has the greatest value. We call
these bits the **least significant** and **most significant bits**, respectively.
If you've ever played games like Mario or Zelda, you may have noticed that the
maximum amount of lives or money you can carry was 255... this is why.

Sometimes you don't need to use all 8 bits. When this is the case, you can
actually store multiple values in the same byte. For example, you can split
the byte into two 4-bit containers called **nybbles**, where each nybble
can hold a value between 0 and 15. This is an effective way to fit more data
in less space, since space is tight on the NES.

    High      Low
    Nybble Nybble
    1011     0001

On the flip side, and as one might expect, it is possible to represent numbers
larger than 255 by combining bytes together. On the 6502, the way this is done
is by adding the larger byte to the right of the smaller byte. So, for example,
the number 861 would be represented by two bytes, in this order: 

    01011101 00000011

This may seem counter intuitive at first, since the numbers appear backwards
and all tangled up. However, imagine doing addition and trying to carry a value
across multiple bytes - the processor reads data from left to right, and it
is much easier to carry the 1 in the direction that the processor already reads
rather than trying to work backwards. While it is possible to add any number
of bytes together to make arbitrarily large numbers, two bytes together are
referred to as a **word**. Which we will discuss when we talk about...


Memory
------
**Memory** is the term given to the location that data is stored while a program
is running. From the player's score to the program code itself, memory is the
holding place for everything that makes up the game. Each byte of memory is
given a 16-bit address (two bytes... or, as we just read, a *word*), so in a
game, the byte at address ```$20A``` might be the player's remaining lives, and
```$215``` might be the vertical position of a monster on the screen.

In order to organize the memory, the 65536 possible memory addresses are
divided in to 256 pages of 256 bytes each. When represented in hex notation,
such as ```$4400```, the higher byte of the address ($44) represents the page
number, and the lower byte ($00) represents the byte number within that page.





Navigation
----------
 * [[Next Tutorial|control_flow]]
 * [[Back to Table of Contents|tutorial]]

