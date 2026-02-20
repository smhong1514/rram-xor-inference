// XOR Co-Simulation Top Wrapper for d_cosim (ngspice)
// Instantiates: xor_controller + input_encoder + sae_control
//
// SA output latching: StrongARM SA returns to precharge (Q=VDD) when SAE=0.
// The FSM reads SA in LATCH state (after sae_done), by which time SAE is LOW.
// Solution: latch SA outputs while SAE is HIGH, feed latched values to FSM.
//
// d_cosim port mapping (MSB first for multi-bit):
//   Inputs  (8):  clk, rst_n, start, input_a, input_b, sa1_q, sa2_q, sa3_q
//   Outputs (17): ready, result_valid, xor_result,
//                 wl_en[3:0], phase, sae, sl_data_1[3:0], sl_data_2[3:0]

module xor_cosim_top (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       start,
    input  wire       input_a,
    input  wire       input_b,
    input  wire       sa1_q,
    input  wire       sa2_q,
    input  wire       sa3_q,

    output wire       ready,
    output wire       result_valid,
    output wire       xor_result,
    output wire [3:0] wl_en,
    output wire       phase,
    output wire       sae,
    output wire [3:0] sl_data_1,
    output wire [3:0] sl_data_2
);

    wire sae_trigger;
    wire sae_done;
    wire h1, h2;
    wire sae_int;

    // Latch SA outputs while SAE is active
    // At the clock edge where sae_control drops SAE (sae<=0, done<=1),
    // the pre-clock value of sae_int is still 1, so we capture the last
    // valid SA output before precharge begins.
    reg sa1_latched, sa2_latched, sa3_latched;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sa1_latched <= 1'b0;
            sa2_latched <= 1'b0;
            sa3_latched <= 1'b0;
        end else if (sae_int) begin
            sa1_latched <= sa1_q;
            sa2_latched <= sa2_q;
            sa3_latched <= sa3_q;
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
        .wl_en        (wl_en),
        .phase        (phase),
        .sae_trigger  (sae_trigger),
        .sae_done     (sae_done),
        .sa1_q        (sa1_latched),
        .sa2_q        (sa2_latched),
        .sa3_q        (sa3_latched),
        .h1_out       (h1),
        .h2_out       (h2)
    );

    input_encoder u_enc (
        .phase     (phase),
        .input_a   (input_a),
        .input_b   (input_b),
        .h1        (h1),
        .h2        (h2),
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
