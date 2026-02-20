// RRAM XOR Inference Top Module (2-Array Architecture)
// Integrates: XOR controller + input encoder + SAE control
//           + 8x WL driver + 3x Sense Amp + 8x BL Write Driver
//           + 2x RRAM 4x4 array
//
// 2-Layer XOR: XOR(A,B) = AND( OR(A,B), NAND(A,B) )
// Array 1 (Layer 1): OR + NAND (simultaneous, independent weights)
// Array 2 (Layer 2): AND (independent weights)
// 2-phase time-multiplexed inference

module rram_ctrl_top (
`ifdef USE_POWER_PINS
    inout  wire        vccd1,
    inout  wire        vssd1,
`endif
    input  wire        clk,
    input  wire        rst_n,

    // RRAM array ground
    inout  wire        rram_gnd,

    // XOR inference interface
    input  wire        start,
    input  wire        input_a,
    input  wire        input_b,
    output wire        xor_result,
    output wire        result_valid,
    output wire        ready,

    // Analog block control
    output wire        phase,       // 0=Layer1, 1=Layer2
    output wire        sae          // SAE output (debug observability)
);

    // Internal signals
    wire [3:0] wl_en;       // Controller → WL drivers (shared for both arrays)
    wire [3:0] wl_out_1;    // WL drivers → Array 1 WL
    wire [3:0] wl_out_2;    // WL drivers → Array 2 WL
    wire [3:0] sl_data_1;   // Encoder → Array 1 SL
    wire [3:0] sl_data_2;   // Encoder → Array 2 SL
    wire [3:0] bl_bus_1;    // Array 1 BL ↔ SA1/SA2 ↔ BL Write Driver 1
    wire [3:0] bl_bus_2;    // Array 2 BL ↔ SA3 ↔ BL Write Driver 2
    wire       sae_trigger, sae_done;
    wire       h1, h2;
    wire       sa1_q, sa1_qb;
    wire       sa2_q, sa2_qb;
    wire       sa3_q, sa3_qb;

    // =========================================================
    // Digital Logic
    // =========================================================

    // XOR Controller FSM
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
        .sa1_q        (sa1_q),
        .sa2_q        (sa2_q),
        .sa3_q        (sa3_q),
        .h1_out       (h1),
        .h2_out       (h2)
    );

    // Input Encoder: phase + inputs → SL data for each array
    input_encoder u_enc (
        .phase     (phase),
        .input_a   (input_a),
        .input_b   (input_b),
        .h1        (h1),
        .h2        (h2),
        .sl_data_1 (sl_data_1),
        .sl_data_2 (sl_data_2)
    );

    // SAE Timing Controller
    sae_control u_sae (
        .clk      (clk),
        .rst_n    (rst_n),
        .trigger  (sae_trigger),
        .sae      (sae),
        .done     (sae_done)
    );

    // =========================================================
    // Analog Macros — Array 1 (Layer 1: OR + NAND)
    // =========================================================

    // WL Drivers for Array 1
    wl_driver u_wl_drv_1_0 (.IN(wl_en[0]), .OUT(wl_out_1[0]));
    wl_driver u_wl_drv_1_1 (.IN(wl_en[1]), .OUT(wl_out_1[1]));
    wl_driver u_wl_drv_1_2 (.IN(wl_en[2]), .OUT(wl_out_1[2]));
    wl_driver u_wl_drv_1_3 (.IN(wl_en[3]), .OUT(wl_out_1[3]));

    // SA1: Array 1 BL[0] vs BL[1] → OR result
    sense_amp u_sa1 (
        .SAE (sae),
        .INP (bl_bus_1[0]),
        .INN (bl_bus_1[1]),
        .Q   (sa1_q),
        .QB  (sa1_qb)
    );

    // SA2: Array 1 BL[2] vs BL[3] → NAND result
    sense_amp u_sa2 (
        .SAE (sae),
        .INP (bl_bus_1[2]),
        .INN (bl_bus_1[3]),
        .Q   (sa2_q),
        .QB  (sa2_qb)
    );

    // BL Write Drivers for Array 1 (disabled during inference)
    bl_write_driver u_bl_wd_1_0 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_1[0]));
    bl_write_driver u_bl_wd_1_1 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_1[1]));
    bl_write_driver u_bl_wd_1_2 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_1[2]));
    bl_write_driver u_bl_wd_1_3 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_1[3]));

    // RRAM 4x4 Array 1
    rram_4x4_array u_rram_array_1 (
        .GND (rram_gnd),
        .WL  (wl_out_1),
        .BL  (bl_bus_1),
        .SL  (sl_data_1)
    );

    // =========================================================
    // Analog Macros — Array 2 (Layer 2: AND)
    // =========================================================

    // WL Drivers for Array 2
    wl_driver u_wl_drv_2_0 (.IN(wl_en[0]), .OUT(wl_out_2[0]));
    wl_driver u_wl_drv_2_1 (.IN(wl_en[1]), .OUT(wl_out_2[1]));
    wl_driver u_wl_drv_2_2 (.IN(wl_en[2]), .OUT(wl_out_2[2]));
    wl_driver u_wl_drv_2_3 (.IN(wl_en[3]), .OUT(wl_out_2[3]));

    // SA3: Array 2 BL[0] vs BL[1] → AND result
    sense_amp u_sa3 (
        .SAE (sae),
        .INP (bl_bus_2[0]),
        .INN (bl_bus_2[1]),
        .Q   (sa3_q),
        .QB  (sa3_qb)
    );

    // BL Write Drivers for Array 2 (disabled during inference)
    bl_write_driver u_bl_wd_2_0 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_2[0]));
    bl_write_driver u_bl_wd_2_1 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_2[1]));
    bl_write_driver u_bl_wd_2_2 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_2[2]));
    bl_write_driver u_bl_wd_2_3 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_2[3]));

    // RRAM 4x4 Array 2
    rram_4x4_array u_rram_array_2 (
        .GND (rram_gnd),
        .WL  (wl_out_2),
        .BL  (bl_bus_2),
        .SL  (sl_data_2)
    );

endmodule
