// RRAM 3x5 Array Blackbox (3 rows x 5 columns)
// Input→Hidden layer: 3 inputs (x1, x2, bias) → 5 hidden neurons
// Matches rram_array_3x5_260222.gds/lef

(* blackbox *)
module rram_array_3x5_260222 (
    inout  wire       GND,     // NFET body ground (met1, left)
    input  wire [4:0] WL,      // Word Lines (met3, bottom) — 5 columns
    inout  wire [4:0] BL,      // Bit Lines (met3, bottom) — 5 columns
    inout  wire [2:0] SL       // Source Lines (met2, right) — 3 rows
);
endmodule
