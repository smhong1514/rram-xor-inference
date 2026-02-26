// RRAM 5x2 Array Blackbox (5 rows x 2 columns)
// Hidden→Output layer: 5 hidden neurons → 2 outputs (z1=z2)
// Matches rram_array_5x2_260222.gds/lef

(* blackbox *)
module rram_array_5x2_260222 (
    inout  wire       GND,     // NFET body ground (met1, left)
    input  wire [1:0] WL,      // Word Lines (met3, bottom) — 2 columns
    inout  wire [1:0] BL,      // Bit Lines (met3, bottom) — 2 columns
    inout  wire [4:0] SL       // Source Lines (met2, right) — 5 rows
);
endmodule
