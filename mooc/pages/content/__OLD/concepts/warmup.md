





Code
----
Below is a basic template that you can use to help get started on making
programs. This code will take care of the entire warmup process for you.
All you have to do is initialize your program in the START block, and then
put your main loop in the NMI block.


    ;----------------------------------------
    ; Put the name of your program and a basic explanation
    ; of how it works here.
    ;
    ; The START label is where the program begins. Here you
    ; should initialize your program's variables. Make sure
    ; you turn on your graphics before the infinite loop
    ; starts!
    ;----------------------------------------
    START:                                  ;
                                            ;
                                            ;
    INFLOOP: JMP INFLOOP                    ;
    ;----------------------------------------
    ;
    ; The NMI (non-maskable interrupt) code is run whenever
    ; the screen refreshes.
    ;----------------------------------------
    NMI:                                    ;
                                            ;
        RTI                                 ; Return from interrupt whenever
    ;---------------------------------------- the frame code is finished.


    ; ******************************************************
    ; STOP STOP STOP STOP STOP STOP STOP STOP STOP STOP STOP
    ;
    ; Don't change any of the code underneath this line unless
    ; you know what you are doing. Unlike many computers, the
    ; NES has to have time to warm up before it can run code.
    ; This code will warm up the NES, clear out the memory,
    ; and put it in a known state so that you can write the
    ; important stuff up above.
    ;*******************************************************
    .org $F000                              ;
    RESET:                                  ;
            SEI                             ; Disable IRQs
            CLD                             ; Disable decimal mode (not on NES)
            LDX #$40                        ;
            STX FRAMECTRL                   ; Disable APU frame IRQ
            LDX #$FF                        ;
            TXS                             ; Set stack pointer to top of stack
            INX                             ; Set X to 0
            STX PPUCTRL                     ; Disable NMI
            STX PPUMASK                     ; Disable rendering
            STX DMCFREQ                     ; Disable DMC IRQs
    vblankwait1:                            ; Wait for the first vertical blank to
            BIT PPUSTATUS                   ;    ensure PPU is ready.
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
            BIT PPUSTATUS                   ;    is ready to go.
            BPL vblankwait2                 ;
    ;----------------------------------------
    ; Now we load our sprite palettes.
    ;----------------------------------------
            LDA PPUSTATUS                   ; read PPU status to reset the high/low latch
            LDA #$3F                        ;
            STA PPUADDR                     ; write the high byte of $3F00 address
            LDA #$00                        ;
            STA PPUADDR                     ; write the low byte of $3F00 address
            LDX #$00                        ; start out at 0
    loadpalettes:                           ;
            LDA palette, x                  ; load data from address (palette + the value in x)
            STA PPUDATA                     ; write to PPU
            INX                             ; X = X + 1
            CPX #$20                        ; Compare X to hex $10, decimal 16 - copying 16 bytes = 4 sprites
            BNE loadpalettes                ; Branch to LoadPalettesLoop if compare was Not Equal to zero
                                            ; if compare was equal to 32, keep going down
    ;----------------------------------------
    ; Now load a blank background. We need to fill $1000 bytes from $2000 to $3000
    ;----------------------------------------
            LDA PPUSTATUS                   ; read PPU status to reset the high/low latch                                      
            LDA #$20                        ; Background VRAM starts at $2000
            STA PPUADDR                     ;
            LDA #$00                        ;
            STA PPUADDR                     ;
            LDA #$00                        ; We will zero out the VRAM.
            LDX #$10                        ; We have to iterate over 0-256 only $10 times.
            LDY #$00                        ;
    bkgloop:                                ;
            STA PPUDATA                     ; Write to the VRAM. Note that no matter how the
            DEY                             ; scroll mirroring is set, this will work.
            BNE bkgloop                     ; BNE will jump if Y != 0
            DEX                             ;
            BNE bkgloop                     ; BNE will jump if X != 0
            LDA PPUSTATUS                   ; read PPU status to reset the high/low latch  
            LDA #$00                        ;
            STA PPUSCROLL                   ; Set the scrolling to 0
            STA PPUSCROLL                   ;
            JMP START                       ;
    ;----------------------------------------
    ; Here's the color palette.
    ;----------------------------------------
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
    ; Interrupt table - located in the last six bytes of memory.
    ;----------------------------------------
            .org $FFFA                      ; Interrupt table is last three words
            .dw NMI                         ; When an NMI happens (once per frame
                                            ;   if enabled, the draw loop)
            .dw RESET                       ; When the processor first turns on or
                                            ;   is reset, it will jump to RESET
            .dw 0                           ; External interrupt IRQ is not used
    ;----------------------------------------
    ; Define all of the memory locations in the memory map.
    ;----------------------------------------
        .define ZEROPAGE=$0000              ;
        .define STACK=$0100                 ;
        .define PPUCTRL=$2000               ;
        .define PPUMASK=$2001               ;
        .define PPUSTATUS=$2002             ;
        .define OAMADDR=$2003               ;
        .define OAMDATA=$2004               ;
        .define PPUSCROLL=$2005             ;
        .define PPUADDR=$2006               ;
        .define PPUDATA=$2007               ;
        .define SQ1VOL=$4000                ;
        .define SQ1SWEEP=$4001              ;
        .define SQ1LO=$4002                 ;
        .define SQ1HI=$4003                 ;
        .define SQ2VOL=$4004                ;
        .define SQ2SWEEP=$4005              ;
        .define SQ2LO=$4006                 ;
        .define SQ2HI=$4007                 ;
        .define TRILIN=$4008                ;
        .define TRILO=$400A                 ;
        .define TRIHI=$400B                 ;
        .define NOISEVOL=$400C              ;
        .define NOISELO=$400E               ;
        .define NOISEHI=$400F               ;
        .define DMCFREQ=$4010               ;
        .define DMCRAW=$4011                ;
        .define DMCSTART=$4012              ;
        .define DMCLEN=$4013                ;
        .define OAMDMA=$4014                ;
        .define SNDCHNL=$4015               ;
        .define CONTROL1=$4016              ;
        .define CONTROL2=$4017              ;
        .define FRAMECTRL=$4018             ;
        .define PRGROM=$8000                ;
    ;----------------------------------------



