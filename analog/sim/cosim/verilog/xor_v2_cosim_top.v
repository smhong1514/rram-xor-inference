// XOR v2 Co-Simulation Top Wrapper for d_cosim (ngspice)
// Architecture: 3-input / 5-hidden / 2-output XOR neural network
// Instantiates: xor_controller + input_encoder + sae_control
//
// SA output latching: StrongARM SA returns to precharge (Q=VDD) when SAE=0.
// Solution: latch SA outputs while SAE is HIGH, feed latched values to FSM.
//
// d_cosim port mapping (MSB first for multi-bit):
//   Inputs  (17): clk, rst_n, start, input_a, input_b,
//                  sa1_q[4:0], sa1_qb[4:0], sa2_q[1:0]
//   Outputs (20): ready, result_valid, xor_result,
//                  wl_en_1[4:0], wl_en_2[1:0],
//                  phase, sae,
//                  sl_data_1[2:0], sl_data_2[4:0]

module xor_v2_cosim_top (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       start,
    input  wire       input_a,
    input  wire       input_b,

    // SA feedback from Array 1 (5 SAs, both Q and QB)
    input  wire [4:0] sa1_q,
    input  wire [4:0] sa1_qb,

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

    // SL data outputs
    output wire [2:0] sl_data_1,
    output wire [4:0] sl_data_2
);

    wire sae_trigger;
    wire sae_done;
    wire [4:0] h;
    wire sae_int;

    // Latch SA outputs while SAE is active
    // Captures valid SA output before precharge begins
    reg [4:0] sa1_q_latched, sa1_qb_latched;
    reg [1:0] sa2_q_latched;

    // Gate SA latch by phase to prevent poisoning:
    // Phase 0: only latch SA1 outputs (SA2 is precharged → would capture VDD=1)
    // Phase 1: only latch SA2 outputs (SA1 is precharged → would capture VDD=1)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sa1_q_latched   <= 5'b00000;
            sa1_qb_latched  <= 5'b00000;
            sa2_q_latched   <= 2'b00;
        end else if (sae_int && !phase) begin
            // Phase 0: latch Array 1 SA outputs only
            sa1_q_latched   <= sa1_q;
            sa1_qb_latched  <= sa1_qb;
        end else if (sae_int && phase) begin
            // Phase 1: latch Array 2 SA outputs only
            sa2_q_latched   <= sa2_q;
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
        .sa1_q        (sa1_q_latched),
        .sa1_qb       (sa1_qb_latched),
        .sa2_q        (sa2_q_latched),
        .h_out        (h)
    );

    input_encoder u_enc (
        .phase     (phase),
        .input_a   (input_a),
        .input_b   (input_b),
        .h         (h),
        .sl_data_1 (sl_data_1),
        .sl_data_2 (sl_data_2)
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
