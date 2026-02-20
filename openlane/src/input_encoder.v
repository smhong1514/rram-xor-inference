// Input Encoder for XOR Inference (2-Array Architecture)
// Encodes inputs to SL control for two separate RRAM arrays
//
// Array 1 (Layer 1): OR + NAND computation
// Array 2 (Layer 2): AND computation
//
// SL[1:0]: digitally encoded inputs (or intermediate h1, h2)
// SL[3:2]: bias reference (digital 1 = VDD; actual analog bias via external mux)
//
// Phase 0 (Layer 1): SL1 = {1, 1, B, A},  SL2 = {0, 0, 0, 0}
// Phase 1 (Layer 2): SL1 = {0, 0, 0, 0},  SL2 = {1, 1, h2, h1}

module input_encoder (
    input  wire       phase,      // 0=Layer1, 1=Layer2
    input  wire       input_a,
    input  wire       input_b,
    input  wire       h1,         // Layer 1 OR result
    input  wire       h2,         // Layer 1 NAND result
    output reg  [3:0] sl_data_1,  // SL[3:0] to RRAM Array 1
    output reg  [3:0] sl_data_2   // SL[3:0] to RRAM Array 2
);

    always @(*) begin
        if (phase == 1'b0) begin
            // Layer 1: OR + NAND (Array 1 active, Array 2 idle)
            sl_data_1 = {1'b1, 1'b1, input_b, input_a};
            sl_data_2 = 4'b0000;
        end else begin
            // Layer 2: AND (Array 1 idle, Array 2 active)
            sl_data_1 = 4'b0000;
            sl_data_2 = {1'b1, 1'b1, h2, h1};
        end
    end

endmodule
