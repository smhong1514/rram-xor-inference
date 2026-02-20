// RRAM 4x4 Array Blackbox Definition
// Matches rram_4x4_array.gds/lef from rram_sky130_project

(* blackbox *)
module rram_4x4_array (
    // GND pin - connects all NFET body terminals, must be routed to chip ground
    inout  wire       GND,     // NFET body ground connection
    // Signal pins
    input  wire [3:0] WL,      // Word Lines - row select
    inout  wire [3:0] BL,      // Bit Lines - column data (bidirectional)
    inout  wire [3:0] SL       // Source Lines - write current return path
);
    // Blackbox - physical layout in GDS/LEF with ReRAM layer (201/20)
endmodule
