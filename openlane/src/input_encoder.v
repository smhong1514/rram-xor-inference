// Input Encoder v3 for XOR Inference (ReLU Activation)
// Only encodes Array 1 SL (Layer 1 input)
// Array 2 SL is driven directly by ReLU (analog, not by this encoder)
//
// Array 1 (3x5, Layer 1): SL[2:0] = {bias=1, x2, x1}

module input_encoder (
    input  wire       input_a,    // x1
    input  wire       input_b,    // x2
    output wire [2:0] sl_data_1   // SL[2:0] to RRAM Array 1 (3 rows)
);

    // SL[0]=x1, SL[1]=x2, SL[2]=bias(1)
    assign sl_data_1 = {1'b1, input_b, input_a};

endmodule
