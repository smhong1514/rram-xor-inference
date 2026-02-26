// XOR v3 Co-Simulation Top Wrapper for d_cosim (ngspice)
// Architecture: 3-input / 5-hidden(ReLU) / 2-output XOR neural network
// v3: Layer 1 SAs replaced by analog ReLU — no digital hidden layer
// Instantiates: xor_controller(v3) + input_encoder(v3) + sae_control
//
// d_cosim port mapping (MSB first for multi-bit):
//   Inputs  (7): clk, rst_n, start, input_a, input_b,
//                 sa2_q[1:0]
//   Outputs (15): ready, result_valid, xor_result,
//                  wl_en_1[4:0], wl_en_2[1:0],
//                  phase, sae,
//                  sl_data_1[2:0]

module xor_v3_cosim_top (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       start,
    input  wire       input_a,
    input  wire       input_b,

    // SA feedback from Array 2 (2 SAs, Q only)
    input  wire [1:0] sa2_q,

    // Status outputs
    output wire       ready,
    output wire       result_valid,
    output wire       xor_result,

    // WL driver controls
    output wire [4:0] wl_en_1,
    output wire [1:0] wl_en_2,

    // Control signals
    output wire       phase,
    output wire       sae,

    // SL data for Array 1 (3 bits)
    output wire [2:0] sl_data_1
);

    wire sae_trigger;
    wire sae_done;
    wire sae_int;

    // Latch SA2 outputs while SAE is active (StrongARM returns to precharge when SAE=0)
    reg [1:0] sa2_q_latched;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sa2_q_latched <= 2'b00;
        end else if (sae_int && phase) begin
            // Phase 1: latch Array 2 SA outputs
            sa2_q_latched <= sa2_q;
        end
    end

    xor_controller u_ctrl (
        .clk          (clk),
        .rst_n        (rst_n),
        .start        (start),
        .input_a      (input_a),
        .input_b      (input_b),
        .xor_result   (xor_result),
        .result_valid (result_valid),
        .ready        (ready),
        .wl_en_1      (wl_en_1),
        .wl_en_2      (wl_en_2),
        .phase        (phase),
        .sae_trigger  (sae_trigger),
        .sae_done     (sae_done),
        .sa2_q        (sa2_q_latched)
    );

    input_encoder u_enc (
        .input_a   (input_a),
        .input_b   (input_b),
        .sl_data_1 (sl_data_1)
    );

    sae_control u_sae (
        .clk     (clk),
        .rst_n   (rst_n),
        .trigger (sae_trigger),
        .sae     (sae_int),
        .done    (sae_done)
    );

    assign sae = sae_int;

endmodule
