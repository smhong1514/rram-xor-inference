// ReLU Activation Function Blackbox
// 5T OTA: PMOS current mirror + NMOS differential pair + tail current source
// Analog: VBL < VREF → OUT HIGH, VBL > VREF → OUT LOW
// Power pins (VDD, VSS) handled by PDN, not in Verilog

(* blackbox *)
module relu (
    inout  wire VBL,     // Analog input (from Array 1 BL)
    inout  wire VREF,    // Reference voltage (~0.9V)
    inout  wire OUT,     // Analog output (to Array 2 SL)
    inout  wire VBIAS    // Tail current bias (~0.8V)
);
endmodule
