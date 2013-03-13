;------------------------------------------------------------------------------
;
; PING PONG
; An NES Game
;
;
; iNES header
;----------------------------------------
        .inesprg 1                      ; 1x 16KB PRG code
        .ineschr 1                      ; 1x  8KB CHR data
        .inesmap 0                      ; mapper 0 = NROM, no bank swapping
        .inesmir 1                      ; background mirroring
;----------------------------------------
;
;
; Bank 0 - The main program code.
;----------------------------------------
        .bank 0=$C000                   ;
        .org $C000                      ;
;----------------------------------------
;
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
        BPL vblankwait1-*               ;
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
        BNE clrmem-*                    ;
vblankwait2:                            ; After 2 vertical blanks, the PPU is
        BIT $2002                       ;    is ready to go.
        BPL vblankwait2-*               ;
                                        ;
;----------------------------------------
;
;
; Here, we prepare our sprites.
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
        BNE loadpalettes-*              ; Branch to LoadPalettesLoop if compare was Not Equal to zero
                                        ; if compare was equal to 32, keep going down
        LDA #%10000000                  ; enable NMI, sprites from Pattern Table 1
        STA $2000                       ;
        LDA #%00010000                  ; enable sprites
        STA $2001                       ;
;----------------------------------------
;
;
; This is an infinite loop. In a "real program", we might put logic here.
; We do all of the logic in the NMI segment, though.
;----------------------------------------
gamestart:                              ;
        LDX #100                         ; DEBUG: Starting position of the ball
        LDY #120
        STY PADDLE_1Y
        STY PADDLE_2Y
        STX BALL_X                      ;
        STY BALL_Y                      ;
        LDA #2                          ;
        STA BALL_DX                     ;
        LDA #1                          ;
        STA BALL_DY                     ;
forever:                                ; Infinite loop - we do all of our
        JMP forever                     ;   logic during NMI.
;----------------------------------------
;
;         NMI Section (main loop)
;         Each frame, we...
;            Advance the ball a step
;            Check player 1's controller
;            If up/down are pressed, move the paddle
;            Check for collisions
;            Change ball's direction if it collides with the paddle
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
        BEQ upnotpressed-*              ;
        DEC PADDLE_1Y                   ;
upnotpressed:                           ;
        LDA $4016                       ; Now check and see if Down is pressed.
        AND #%00000001                  ;
        BEQ downnotpressed-*            ;
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
; OAM sprites on page 3.
;   Sprite 1: ball (8x8)
;   Sprite 2-5: top of paddle 1
;   Sprite 6-9: paddle 2
;----------------------------------------
draw:                                   ;
        LDX BALL_X                      ; First load the position of the ball
        LDY BALL_Y                      ;
        STY $304                        ; Store the position of the ball
        STX $307                        ;
        LDX #$00                        ; Pick the ball's sprite
        STX $305                        ;
        STX $306                        ;
        
        LDX #16
        LDA PADDLE_1Y
        STA $308
        CLC
        ADC #8
        STA $30C
        CLC
        ADC #8
        STA $310
        CLC
        ADC #8
        STA $314
        STX $30B
        STX $30F
        STX $313
        STX $317
        

        LDX #230
        LDA PADDLE_2Y
        STA $318
        CLC
        ADC #8
        STA $31C
        CLC
        ADC #8
        STA $320
        CLC
        ADC #8
        STA $324
        STX $31B
        STX $31F
        STX $323
        STX $327
        
        LDA #$00                        ; Now pass the OAM parameters to the PPU
        STA $2003                       ;   and do DMA
        LDA #$03                        ; Page 3 has our sprites.
        STA $4014                       ; Start DMA
        RTS                             ;
;----------------------------------------






;----------------------------------------
;
;
; Bank 1 - ROM Data segment and interrupt table
;----------------------------------------
        .bank 1=$E000                   ;
        .org $E000                      ;
palette:                                ;
        .db $0F,$31,$32,$33             ;
        .db $34,$35,$36,$37             ;
        .db $38,$39,$3A,$3B             ;
        .db $3C,$3D,$3E,$0F             ;
        .db $0F,$1C,$15,$14             ;
        .db $31,$02,$38,$3C             ;
        .db $0F,$1C,$15,$14             ;
        .db $31,$02,$38,$3C             ;
sprites:                                ; vert tile attr horiz
        .db $80, $32, $00, $80          ; sprite 0
        .db $80, $33, $00, $88          ; sprite 1
        .db $88, $34, $00, $80          ; sprite 2
        .db $88, $35, $00, $88          ; sprite 3
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
;
;
; Bank 2 - Pattern table
; Contains our sprite sheet.
;----------------------------------------
        .bank 2=$0000                   ;
        .org $0000                      ;
        ;.incbin "empty"                 ; Include an 8-kb "empty" palette #TODO
;----------------------------------------

