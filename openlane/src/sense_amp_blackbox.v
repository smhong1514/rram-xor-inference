// Sense Amplifier Blackbox
// StrongARM Latch-type, 10 transistors
// Differential input → full-swing digital output
// Power pins (VDD, VSS) handled by PDN, not in Verilog

(* blackbox *)
module sense_amp (
    input  wire SAE,     // Sense Amplifier Enable (active high)
    input  wire INP,     // Positive differential input
    input  wire INN,     // Negative differential input
    output wire Q,       // Digital output
    output wire QB       // Complementary digital output
);
endmodule
