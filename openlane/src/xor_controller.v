// XOR Inference Controller v3 (ReLU Activation)
// 2-Layer XOR via RRAM 3x5 + 5x2 arrays
// Layer 1→2: Analog ReLU activation (no digital latching)
//
// XOR(x1,x2) = AND( OR(x1,x2), NAND(x1,x2) )
//
// Phase 0: Array 1 WLs ON, SL1 driven → BL1 develops → ReLU outputs settle
// Phase 1: Array 2 WLs ON (Array 1 stays ON) → BL2 develops → SA latch
//
// SA2_0(Q) → z[0] = XOR
// SA2_1(Q) → z[1] = XOR (redundant, must match z[0])

module xor_controller (
    input  wire        clk,
    input  wire        rst_n,

    // Inference interface
    input  wire        start,
    input  wire        input_a,       // x1
    input  wire        input_b,       // x2
    output reg         xor_result,
    output reg         result_valid,
    output wire        ready,

    // WL driver control
    output reg  [4:0]  wl_en_1,       // Array 1 WL enables (5 columns)
    output reg  [1:0]  wl_en_2,       // Array 2 WL enables (2 columns)

    // Phase control
    output reg         phase,         // 0=Layer1 settling, 1=Layer2 settling

    // SAE handshake (Layer 2 only)
    output reg         sae_trigger,
    input  wire        sae_done,

    // SA feedback - Layer 2 only (2 SAs)
    input  wire [1:0]  sa2_q          // SA Q outputs (Array 2)
);

    // FSM states
    localparam IDLE         = 3'd0;
    localparam PHASE0_WL    = 3'd1;   // Array 1 WL settling
    localparam PHASE0_RELU  = 3'd2;   // BL1 + ReLU output settling
    localparam PHASE1_WL    = 3'd3;   // Array 2 WL settling
    localparam PHASE1_BL    = 3'd4;   // BL2 settling
    localparam SAE_WAIT     = 3'd5;   // Wait for SAE done
    localparam LATCH        = 3'd6;   // Capture SA2 output
    localparam DONE         = 3'd7;

    reg [2:0] state;
    reg [3:0] wait_cnt;
    reg       a_reg, b_reg;

    // Timing parameters (clock cycles)
    localparam WL_SETTLE_CNT   = 4'd2;   // WL driver settle time
    localparam RELU_SETTLE_CNT = 4'd6;   // BL1 develop + ReLU propagation (~4ns OTA)
    localparam BL2_SETTLE_CNT  = 4'd4;   // Array 2 BL develop time

    assign ready = (state == IDLE);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= IDLE;
            wait_cnt     <= 4'd0;
            phase        <= 1'b0;
            a_reg        <= 1'b0;
            b_reg        <= 1'b0;
            xor_result   <= 1'b0;
            result_valid <= 1'b0;
            wl_en_1      <= 5'b00000;
            wl_en_2      <= 2'b00;
            sae_trigger  <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    result_valid <= 1'b0;
                    sae_trigger  <= 1'b0;
                    wl_en_1      <= 5'b00000;
                    wl_en_2      <= 2'b00;
                    phase        <= 1'b0;
                    if (start) begin
                        a_reg    <= input_a;
                        b_reg    <= input_b;
                        // Phase 0: Turn on Array 1 WLs only
                        phase    <= 1'b0;
                        wl_en_1  <= 5'b11111;
                        wl_en_2  <= 2'b00;
                        wait_cnt <= 4'd0;
                        state    <= PHASE0_WL;
                    end
                end

                PHASE0_WL: begin
                    // Wait for Array 1 WL drivers to settle
                    if (wait_cnt >= WL_SETTLE_CNT) begin
                        wait_cnt <= 4'd0;
                        state    <= PHASE0_RELU;
                    end else begin
                        wait_cnt <= wait_cnt + 4'd1;
                    end
                end

                PHASE0_RELU: begin
                    // Wait for BL1 to develop + ReLU to propagate
                    if (wait_cnt >= RELU_SETTLE_CNT) begin
                        // Phase 1: Add Array 2 WLs (keep Array 1 on)
                        phase    <= 1'b1;
                        wl_en_2  <= 2'b11;
                        wait_cnt <= 4'd0;
                        state    <= PHASE1_WL;
                    end else begin
                        wait_cnt <= wait_cnt + 4'd1;
                    end
                end

                PHASE1_WL: begin
                    // Wait for Array 2 WL drivers to settle
                    if (wait_cnt >= WL_SETTLE_CNT) begin
                        wait_cnt <= 4'd0;
                        state    <= PHASE1_BL;
                    end else begin
                        wait_cnt <= wait_cnt + 4'd1;
                    end
                end

                PHASE1_BL: begin
                    // Wait for Array 2 BL to develop
                    if (wait_cnt >= BL2_SETTLE_CNT) begin
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
                    // Capture Layer 2 output
                    // z[0] and z[1] should match (redundant columns)
                    xor_result <= sa2_q[0] & sa2_q[1];
                    state      <= DONE;
                end

                DONE: begin
                    result_valid <= 1'b1;
                    wl_en_1      <= 5'b00000;
                    wl_en_2      <= 2'b00;
                    phase        <= 1'b0;
                    state        <= IDLE;
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
