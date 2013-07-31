ace.define('ace/mode/nes', function(require, exports, module) {

var oop = require("ace/lib/oop");
var TextMode = require("ace/mode/text").Mode;
var Tokenizer = require("ace/tokenizer").Tokenizer;
var NesHighlightRules = require("ace/mode/nes_highlight_rules").NesHighlightRules;

var Mode = function() {
    this.$tokenizer = new Tokenizer(new NesHighlightRules().getRules());
};
oop.inherits(Mode, TextMode);

(function() {
    // Extra logic goes here. (see below)
}).call(Mode.prototype);

exports.Mode = Mode;
});




ace.define('ace/mode/nes_highlight_rules', function(require, exports, module) {

var oop = require("ace/lib/oop");
var TextHighlightRules = require("ace/mode/text_highlight_rules").TextHighlightRules;

var NesHighlightRules = function() {

    this.$rules = {
        "start" : [
        {
            token : "comment",
            regex : ";.*$"
        },
        {
            token : "constant",
            regex : "#\\S+"
        },
        {
            token : "string", // " string
            regex : '"(?=.)',
            next : "qqstring"
        },
        {
            token : "string", // ' string
            regex : "'(?=.)",
            next : "qstring"
        },
        {
            token : "keyword",
            regex : "ADC|AND|ASL|BCC|BCS|BEQ|BIT|BMI|BNE|BPL|BRK|BVC|BVS|CLC|"+
                    "CLD|CLI|CLV|CMP|CPX|CPY|DEC|DEX|DEY|EOR|INC|INX|INY|JMP|"+
                    "JSR|LDA|LDX|LDY|LSR|NOP|ORA|PHA|PHP|PLA|PLP|ROL|ROR|RTI|"+
                    "RTS|SBC|SEC|SED|SEI|STA|STX|STY|TAX|TAY|TSX|TXA|TXS|TYA|"+
                    "\\.org|\\.db|\\.dw|\\.bytes|\\.words|\\.define|\\.ascii"
        },
        ],
        
        "qqstring" : [
        {
            token : "string",
            regex : "\\\\$",
            next : "qqstring"
        },
        {
            token : "string",
            regex : '"|$',
            next : "start"
        },
        {
            defaultToken: "string"
        }],
        
        "qstring" : [
        {
            token : "string",
            regex : "\\\\$",
            next : "qstring"
        },
        {
            token : "string",
            regex : "'|$",
            next : "start"
        },
        {
            defaultToken: "string"
        }]
    };
    
}

oop.inherits(NesHighlightRules, TextHighlightRules);

exports.NesHighlightRules = NesHighlightRules;
});
