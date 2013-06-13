;------------------------------------------------------------------------------
;
; PING PONG
; An NES Game
;
; This portion of our code puts the system back into a known state. We don't
; exit this code until the memory is reset and the PPU has warmed up (two
; vertical blanks).
;   RESET       : Vector label when power on or reset button pressed
;   vblankwait1 : Wait for the first vertical blank
;   clrmem      : Zero out all memory
;   vblankwait2 : Wait for the second vertical blank - PPU is now warmed up
;----------------------------------------
RESET:                                  ;
        SEI                             ; Disable IRQs
        CLD                             ; Disable decimal mode (not on NES)
        LDX #$40                        ;
        STX $4017                       ; Disable APU frame IRQ
        LDX #$FF                        ;
        TXS                             ; Set stack pointer to top of stack
        INX                             ; Set X to 0
        STX $2000                       ; Disable NMI
        STX $2001                       ; Disable rendering
        STX $4010                       ; Disable DMC IRQs
vblankwait1:                            ; Wait for the first vertical blank to
        BIT $2002                       ;    ensure PPU is ready.
        BPL vblankwait1                 ;
clrmem:                                 ; Zero out all memory
        LDA #$00                        ;
        STA $0000, x                    ;
        STA $0100, x                    ;
        STA $0200, x                    ;
        STA $0400, x                    ;
        STA $0500, x                    ;
        STA $0600, x                    ;
        STA $0700, x                    ;
        LDA #$FE                        ;
        STA $0300, x                    ;
        INX                             ;
        BNE clrmem                      ;
vblankwait2:                            ; After 2 vertical blanks, the PPU is
        BIT $2002                       ;    is ready to go.
        BPL vblankwait2                 ;
                                        ;
;----------------------------------------
;
;
; Now we load our sprite palettes.
;----------------------------------------
        LDA $2002                       ; read PPU status to reset the high/low latch
        LDA #$3F                        ;
        STA $2006                       ; write the high byte of $3F00 address
        LDA #$00                        ;
        STA $2006                       ; write the low byte of $3F00 address
        LDX #$00                        ; start out at 0
loadpalettes:                           ;
        LDA palette, x                  ; load data from address (palette + the value in x)
        STA $2007                       ; write to PPU
        INX                             ; X = X + 1
        CPX #$20                        ; Compare X to hex $10, decimal 16 - copying 16 bytes = 4 sprites
        BNE loadpalettes                ; Branch to LoadPalettesLoop if compare was Not Equal to zero
;end of loadpalettes                    ; if compare was equal to 32, keep going down
;----------------------------------------
;
;
; Now load a blank background. We need to fill $1000 bytes from $2000 to $3000
;----------------------------------------
        LDA $2002                       ; read PPU status to reset the high/low latch                                      
        LDA #$20                        ; Background VRAM starts at $2000
        STA $2006                       ;
        LDA #$00                        ;
        STA $2006                       ;
        LDA #$00                        ; We will zero out the VRAM.
        LDX #$10                        ; We have to iterate over 0-256 only $10 times.
        LDY #$00                        ;
bkgloop:                                ;
        STA $2007                       ; Write to the VRAM. Note that no matter how the
        DEY                             ; scroll mirroring is set, this will work.
        BNE bkgloop                     ; BNE will jump if Y != 0
        DEX                             ;
        BNE bkgloop                     ; BNE will jump if X != 0
;----------------------------------------
;
;
; Now we enable the sprites, graphics, and NMI interrupts. We set the sprites
; to the left pattern table and the graphics to the right.
;----------------------------------------
        LDA #%10010000                  ; enable NMI, sprites from Pattern Table 1
        STA $2000                       ;
        LDA #%00011110                  ; enable sprites
        STA $2001                       ;
        LDA #$00                        ;
        STA $2005                       ; Set the scrolling to 0
        STA $2005                       ;
;----------------------------------------
;
;
; This is the initial game start code. We simply set the initial values of
; all of the variables, then go into an infinite loop, since the game logic
; occurs during the NMI.
;----------------------------------------
gamestart:                              ;
        LDX #100                        ; DEBUG: Starting position of the ball
        LDY #120                        ; and the paddles.
        STY PADDLE_1Y                   ;
        STY PADDLE_2Y                   ;
        STX BALL_X                      ;
        STY BALL_Y                      ;
        LDA #1                          ;
        STA BALL_DX                     ;
        STA BALL_DY                     ;
forever:                                ; Infinite loop - we do all of our
        JMP forever                     ;   logic during NMI.
;----------------------------------------
;
;
;         NMI Section (main loop)
;         Each frame, we...
;            Advance the ball a step
;            Check player 1's controller
;            If up/down are pressed, move the paddle
;            Check for collisions
;            Change ball's direction if it collides with the paddle
;            If either player hits 10 points, start them both over
;            Draw the paddles, score, etc.
; 
;----------------------------------------
        .define BALL_X=$200             ;
        .define BALL_Y=$201             ;
        .define BALL_DX=$202            ;
        .define BALL_DY=$203            ;
        .define PADDLE_1Y=$204          ;
        .define PADDLE_2Y=$205          ;
        .define P1_SCORE=$206           ;
        .define P2_SCORE=$207           ;
NMI:                                    ;
        LDX BALL_DX                     ; Prepare the 'balladvance' script
        LDY BALL_DY                     ;
        JSR balladvance                 ; Move the ball based on X/Y
        JSR controller                  ; Inc/Dec PADDLE_1Y value
        JSR ai                          ; Inc/Dec PADDLE_2Y value
        LDX BALL_X                      ; Prepare the 'collisions' subroutine
        LDY BALL_Y                      ;
        JSR collisions                  ; 
        JSR resetscore                  ;
        JSR draw                        ; Draw paddles, ball, scores
        RTI                             ;
;----------------------------------------
;
;
; Subroutine    : balladvance
; Precondition  : X and Y registers contain velocity of the ball
; Postcondition : BALL_X and BALL_Y contain new position of the ball
; Cleanup       : N/A
; Errors        : N/A
;----------------------------------------
balladvance:                            ;
        TXA                             ; X register contains DX
        CLC                             ; Clear carry
        ADC BALL_X                      ; Add the current ball position
        STA BALL_X                      ; Update the ball position
        TYA                             ; Y register contains DY
        CLC                             ; Clear carry before addition
        ADC BALL_Y                      ; Add the current ball position
        STA BALL_Y                      ; Update the ball position
        RTS                             ; Hop back, no cleanup needed
;----------------------------------------
;
;
; Subroutine    : controller
; Precondition  : PADDLE_1Y contains current paddle center
; Postcondition : If player has pressed up/down, paddle moves up or down
; Cleanup       : N/A
; Errors        : N/A
;----------------------------------------
controller:                             ;
        LDX #%00000001                  ; Strobe the controller by writing a
        STX $4016                       ;   one followed by a zero to $4016.0
        DEX                             ;
        STX $4016                       ;
                                        ;
        LDA $4016                       ; Read $4016.0 to get whether a button is
        LDA $4016                       ;   pressed. The first four reads are
        LDA $4016                       ;   A,B,Select,Start (not used).
        LDA $4016                       ;
        LDA $4016                       ; Now we check and see if Up is pressed.
        AND #%00000001                  ;
        BEQ upnotpressed                ;
        DEC PADDLE_1Y                   ;
upnotpressed:                           ;
        LDA $4016                       ; Now check and see if Down is pressed.
        AND #%00000001                  ;
        BEQ downnotpressed              ;
        INC PADDLE_1Y                   ;
downnotpressed:                         ; We don't check left or right.
        RTS                             ; No need to clean up. We're done.
;----------------------------------------
;
;
; Subroutine    : ai
; Precondition  : PADDLE_2Y contains current paddle center
; Postcondition : Arbitrarily increase/decrease PADDLE_2Y
; Cleanup       : N/A
; Errors        : N/A
;----------------------------------------
ai:                                     ;
        DEC PADDLE_2Y                   ;
        RTS                             ;
;----------------------------------------
;
;
; Subroutine    : collisions
; Precondition  : X and Y registers contain current ball position
; Postcondition : Multiply BALL_DX by -1 if there was a collision with a paddle
;                 Multiply BALL_DY by -1 if there was a collision with the floor
;                 Increase score if the ball crosses the boundary and set
;                    BALL_X to the middle of the field.
; Cleanup       : N/A
; Errors        : N/A
;----------------------------------------
collisions:                             ;
        CPY #$E0
        BCS hitbottom  
        CPY #$08
        BCC hitbottom  
        JMP checksides
hitbottom:
        LDA BALL_DY
        EOR #$FF
        STA BALL_DY
        INC BALL_DY
checksides:
        TYA
        CPX #$2
        BCC crossleft  
        CPX #$FD
        BCS crossright  
        CPX #24
        BEQ leftpaddle  
        CPX #222
        BEQ rightpaddle  
        JMP endcollisions
leftpaddle:
        SEC
        SBC PADDLE_1Y
        ADC #8
        CMP #40
        BCC flipflop  
        JMP endcollisions
rightpaddle:
        SEC
        SBC PADDLE_2Y
        ADC #8
        CMP #40
        BCC flipflop  
        JMP endcollisions
crossleft:
        INC P2_SCORE
        LDX #100                        ; DEBUG: Starting position of the ball
        LDY #120
        STX BALL_X
        JMP flipflop
crossright:
        INC P1_SCORE
        LDX #100                        ; DEBUG: Starting position of the ball
        LDY #120
        STX BALL_X
flipflop:
        LDA BALL_DX
        EOR #$FF
        STA BALL_DX
        INC BALL_DX
endcollisions:
        RTS                             ;
;----------------------------------------
;
;
; Subroutine    : resetscore
; Precondition  : 
; Postcondition :
; Cleanup       :
; Errors        :
;
; This resets the score to zero if either player gets 10 points.
;----------------------------------------
resetscore:                             ;
        LDA #10                         ; If the score is 10 for either player,
        CMP P1_SCORE                    ; go and actually reset the score.
        BEQ doresetscore                ;
        CMP P2_SCORE                    ;
        BEQ doresetscore                ;
        RTS                             ; Otherwise, do an early return.
doresetscore:                           ;
        LDA #0                          ; Set both player's scores to 0 and
        STA P1_SCORE                    ; then return.
        STA P2_SCORE                    ;
        RTS                             ;
;----------------------------------------
;
;
; Subroutine    : draw
; Precondition  : 
; Postcondition : The ball, paddles, and scores are displayed.
; Cleanup       : N/A
; Errors        : N/A
;
; This code works by taking the parameters from the code and setting the
; OAM sprites on page $3.
;----------------------------------------
        .define SPR_BALL=$304           ; The ball is just one 8x8 tile
        .define SPR_LPAD1=$308          ; The paddles are 8x32
        .define SPR_LPAD2=$30C          ;
        .define SPR_LPAD3=$310          ;
        .define SPR_LPAD4=$314          ;
        .define SPR_RPAD1=$318          ; The right paddle is also 8x32
        .define SPR_RPAD2=$31C          ;
        .define SPR_RPAD3=$320          ;
        .define SPR_RPAD4=$324          ;
        .define SPR_LSCR1=$328          ; The score is an 8x16 sprite
        .define SPR_LSCR2=$32C          ;
        .define SPR_RSCR1=$330          ; The right score is also an 8x16 sprite
        .define SPR_RSCR2=$334          ;
draw:                                   ;
        LDX BALL_X                      ; First load the position of the ball
        LDY BALL_Y                      ;
        STY SPR_BALL+0                  ; Store the position of the ball
        STX SPR_BALL+3                  ;
        LDX #$30                        ; Pick the ball's sprite
        STX SPR_BALL+1                  ;
        LDX #$00                        ; Set the ball's palette
        STX SPR_BALL+2                  ;
                                        ;
        ; paddle                        ;
        LDX #16                         ; The X position of the paddle is fixed
        LDA PADDLE_1Y                   ; The Y position marks the top pixel.
        STA SPR_LPAD1                   ; We add 8 pixels each time
        CLC                             ;
        ADC #8                          ; 
        STA SPR_LPAD2                   ;
        CLC                             ;
        ADC #8                          ;
        STA SPR_LPAD3                   ;
        CLC                             ;
        ADC #8                          ;
        STA SPR_LPAD4                   ;
        STX SPR_LPAD1+3                 ;
        STX SPR_LPAD2+3                 ;
        STX SPR_LPAD3+3                 ;
        STX SPR_LPAD4+3                 ;
                                        ;
        LDX #$0                         ; Set the sprites for the left paddle equal to
        STX SPR_LPAD1+1                 ; the three sprites on the top left.
        LDX #$10                        ;
        STX SPR_LPAD2+1                 ;
        STX SPR_LPAD3+1                 ;
        LDX #$20                        ;
        STX SPR_LPAD4+1                 ;
        LDX #$01                        ;
        STX SPR_LPAD1+2                 ; Set the palette and flipping to 0.
        STX SPR_LPAD2+2                 ;
        STX SPR_LPAD3+2                 ;
        STX SPR_LPAD4+2                 ;
                                        ;
        ; right paddle                  ;
        LDX #230                        ;
        LDA PADDLE_2Y                   ;
        STA SPR_RPAD1                   ;
        CLC                             ;
        ADC #8                          ;
        STA SPR_RPAD2                   ;
        CLC                             ;
        ADC #8                          ;
        STA SPR_RPAD3                   ;
        CLC                             ;
        ADC #8                          ;
        STA SPR_RPAD4                   ;
        STX SPR_RPAD1+3                 ;
        STX SPR_RPAD2+3                 ;
        STX SPR_RPAD3+3                 ;
        STX SPR_RPAD4+3                 ;
                                        ;
        LDX #$0                         ; Set the sprites for the right paddle equal to
        STX SPR_RPAD1+1                 ; the three sprites on the top left.
        LDX #$10                        ;
        STX SPR_RPAD2+1                 ;
        STX SPR_RPAD3+1                 ;
        LDX #$20                        ;
        STX SPR_RPAD4+1                 ;
        LDX #$02                        ;
        STX SPR_RPAD1+2                 ; Set the palette and flipping to 0.
        STX SPR_RPAD2+2                 ;
        STX SPR_RPAD3+2                 ;
        STX SPR_RPAD4+2                 ;
                                        ;
        ; Now we draw score             ;
        CLC                             ;
        LDA P1_SCORE                    ;
        ADC #$E0                        ;
        STA SPR_LSCR1+1                 ;
        ADC #$10                        ;
        STA SPR_LSCR2+1                 ;
        LDX #$01                        ;
        STX SPR_LSCR1+2                 ;
        STX SPR_LSCR2+2                 ;
        LDA #60                         ;
        STA SPR_LSCR1+3                 ;
        STA SPR_LSCR2+3                 ;
        LDA #200                        ;
        STA SPR_LSCR1+0                 ;
        ADC #8                          ;
        STA SPR_LSCR2+0                 ;
        LDA P2_SCORE                    ;
        ADC #$E0                        ;
        STA SPR_RSCR1+1                 ;
        ADC #$10                        ;
        STA SPR_RSCR2+1                 ;
        LDX #$02                        ;
        STX SPR_RSCR1+2                 ;
        STX SPR_RSCR2+2                 ;
        LDA #200                        ;
        STA SPR_RSCR1+3                 ;
        STA SPR_RSCR2+3                 ;
        LDA #200                        ;
        STA SPR_RSCR1+0                 ;
        ADC #8                          ;
        STA SPR_RSCR2+0                 ;
                                        ;
        ; OAM                           ;
        LDA #$00                        ; Now pass the OAM parameters to the PPU
        STA $2003                       ;   and do DMA
        LDA #$03                        ; Page 3 has our sprites.
        STA $4014                       ; Start DMA
        RTS                             ;
;----------------------------------------






;----------------------------------------
;
;
; Palettes and and interrupt table
;----------------------------------------
        .org $E000                      ;
palette:                                ;
        .db $0F,$31,$32,$33             ;
        .db $0F,$35,$36,$37             ;
        .db $0F,$39,$3A,$3B             ;
        .db $0F,$3D,$3E,$0F             ;
        .db $0F,$28,$18,$38             ;
        .db $0F,$1C,$0C,$2C             ;
        .db $0F,$15,$05,$25             ;
        .db $0F,$02,$38,$3C             ;
;----------------------------------------
;
;
; Interrupt table - located in the last six bytes of memory.
;----------------------------------------
        .org $FFFA                      ; Interrupt table is last three words
        .dw NMI                         ; When an NMI happens (once per frame
                                        ;   if enabled, the draw loop)
        .dw RESET                       ; When the processor first turns on or
                                        ;   is reset, it will jump to RESET
        .dw 0                           ; External interrupt IRQ is not used
;----------------------------------------



