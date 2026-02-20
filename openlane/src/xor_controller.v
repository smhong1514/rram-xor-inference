// XOR Inference Controller (2-Array Architecture)
// 2-Layer XOR via two RRAM 4x4 arrays, 2-phase time-multiplexed
// XOR(A,B) = AND( OR(A,B), NAND(A,B) )
//
// Phase 0 (Layer 1): SL1=[A, B, bias, bias]
//   SA1(Array1 BL0 vs BL1) → h1 (OR)
//   SA2(Array1 BL2 vs BL3) → h2 (NAND)
// Phase 1 (Layer 2): SL2=[h1, h2, bias, bias]
//   SA3(Array2 BL0 vs BL1) → xor_result (AND)

module xor_controller (
    input  wire        clk,
    input  wire        rst_n,

    // Inference interface
    input  wire        start,
    input  wire        input_a,
    input  wire        input_b,
    output reg         xor_result,
    output reg         result_valid,
    output wire        ready,

    // RRAM array control
    output reg  [3:0]  wl_en,       // WL driver enable (all ON during inference)

    // Phase control
    output reg         phase,       // 0=Layer1, 1=Layer2

    // SAE handshake
    output reg         sae_trigger, // Pulse to start SAE sequence
    input  wire        sae_done,    // SAE sequence complete

    // SA feedback
    input  wire        sa1_q,       // SA1: OR result (Array 1, BL[0] vs BL[1])
    input  wire        sa2_q,       // SA2: NAND result (Array 1, BL[2] vs BL[3])
    input  wire        sa3_q,       // SA3: AND result (Array 2, BL[0] vs BL[1])

    // Intermediate results (for input_encoder)
    output wire        h1_out,
    output wire        h2_out
);

    // FSM states
    localparam IDLE      = 3'd0;
    localparam WL_ON     = 3'd1;  // Enable WL drivers, wait to settle
    localparam SL_SETTLE = 3'd2;  // SL data applied, wait for BL current to settle
    localparam SAE_WAIT  = 3'd3;  // SAE pulse in progress (via sae_control)
    localparam LATCH     = 3'd4;  // Capture SA output
    localparam DONE      = 3'd5;  // Output result

    reg [2:0] state;
    reg [3:0] wait_cnt;
    reg       a_reg, b_reg;
    reg       h1_reg, h2_reg;

    // Timing parameters (clock cycles)
    localparam WL_SETTLE_CNT = 4'd2;  // WL driver stabilization
    localparam SL_SETTLE_CNT = 4'd4;  // Array current settling

    assign ready  = (state == IDLE);
    assign h1_out = h1_reg;
    assign h2_out = h2_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= IDLE;
            wait_cnt     <= 4'd0;
            phase        <= 1'b0;
            a_reg        <= 1'b0;
            b_reg        <= 1'b0;
            h1_reg       <= 1'b0;
            h2_reg       <= 1'b0;
            xor_result   <= 1'b0;
            result_valid <= 1'b0;
            wl_en        <= 4'b0000;
            sae_trigger  <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    result_valid <= 1'b0;
                    sae_trigger  <= 1'b0;
                    wl_en        <= 4'b0000;
                    phase        <= 1'b0;
                    if (start) begin
                        a_reg    <= input_a;
                        b_reg    <= input_b;
                        phase    <= 1'b0;        // Start with Layer 1
                        wl_en    <= 4'b1111;     // All WLs ON
                        wait_cnt <= 4'd0;
                        state    <= WL_ON;
                    end
                end

                WL_ON: begin
                    if (wait_cnt >= WL_SETTLE_CNT) begin
                        wait_cnt <= 4'd0;
                        state    <= SL_SETTLE;
                    end else begin
                        wait_cnt <= wait_cnt + 4'd1;
                    end
                end

                SL_SETTLE: begin
                    // input_encoder drives sl_data_1/sl_data_2 based on current phase
                    if (wait_cnt >= SL_SETTLE_CNT) begin
                        sae_trigger <= 1'b1;
                        state       <= SAE_WAIT;
                    end else begin
                        wait_cnt <= wait_cnt + 4'd1;
                    end
                end

                SAE_WAIT: begin
                    sae_trigger <= 1'b0;
                    if (sae_done) begin
                        state <= LATCH;
                    end
                end

                LATCH: begin
                    if (phase == 1'b0) begin
                        // Layer 1: capture OR and NAND simultaneously
                        h1_reg   <= sa1_q;     // OR  → SA1 (Array 1)
                        h2_reg   <= sa2_q;     // NAND → SA2 (Array 1)
                        phase    <= 1'b1;      // Switch to Layer 2
                        wait_cnt <= 4'd0;
                        state    <= SL_SETTLE; // WL already ON, skip WL_ON
                    end else begin
                        // Layer 2: capture AND result
                        xor_result <= sa3_q;   // AND  → SA3 (Array 2)
                        state      <= DONE;
                    end
                end

                DONE: begin
                    result_valid <= 1'b1;
                    wl_en        <= 4'b0000;
                    phase        <= 1'b0;
                    state        <= IDLE;
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
