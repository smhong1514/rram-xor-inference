// BL Write Driver Blackbox
// Tri-state buffer, 8 transistors (all 1.8V CMOS)
// EN=1: DATA→BL (full swing), EN=0: Hi-Z
// Power pins (VDD, VSS) handled by PDN, not in Verilog

(* blackbox *)
module bl_write_driver (
    input  wire EN,      // Enable (active high)
    input  wire DATA,    // Write data input
    output wire BL       // Bit line output (tri-state)
);
endmodule
