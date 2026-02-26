// RRAM XOR Inference Top Module v3 (ReLU Activation)
// Integrates: XOR controller + input encoder + SAE control
//           + 7x WL driver + 5x ReLU + 2x Sense Amp + 7x BL Write Driver
//           + RRAM 3x5 array + RRAM 5x2 array
//
// Total: 23 analog macros
//   Array 1 (Layer 1): 1x RRAM 3x5 + 5x WL + 5x BL_WD
//   Layer 1→2:         5x ReLU (analog activation)
//   Array 2 (Layer 2): 1x RRAM 5x2 + 2x WL + 2x SA + 2x BL_WD
//
// v2→v3 changes:
//   - 5x Layer 1 SAs removed (replaced by 5x ReLU)
//   - BL1[i] → ReLU[i] → SL2[i] (direct analog path)
//   - No digital hidden layer (h_reg removed)
//   - Single inference pass (no 2-phase digital latching)

module rram_ctrl_top (
`ifdef USE_POWER_PINS
    inout  wire        vccd1,
    inout  wire        vssd1,
`endif
    input  wire        clk,
    input  wire        rst_n,

    // RRAM array ground
    inout  wire        rram_gnd,

    // VREF for Sense Amplifiers and ReLU
    inout  wire        vref,

    // VBIAS for ReLU tail current
    inout  wire        vbias,

    // XOR inference interface
    input  wire        start,
    input  wire        input_a,      // x1
    input  wire        input_b,      // x2
    output wire        xor_result,
    output wire        result_valid,
    output wire        ready,

    // Analog block control
    output wire        phase,        // 0=Layer1 settling, 1=Layer2 settling
    output wire        sae           // SAE output (debug observability)
);

    // =========================================================
    // Internal Signals
    // =========================================================

    // Controller <-> WL drivers
    wire [4:0] wl_en_1;        // Array 1 WL enables
    wire [1:0] wl_en_2;        // Array 2 WL enables
    wire [4:0] wl_out_1;       // WL driver outputs → Array 1
    wire [1:0] wl_out_2;       // WL driver outputs → Array 2

    // Encoder → Array 1 SL
    wire [2:0] sl_data_1;

    // Array BL buses
    wire [4:0] bl_bus_1;       // Array 1 BL (5 columns)
    wire [1:0] bl_bus_2;       // Array 2 BL (2 columns)

    // ReLU outputs → Array 2 SL
    wire [4:0] relu_out;       // ReLU analog outputs

    // SAE handshake
    wire sae_trigger, sae_done;

    // SA outputs — Layer 2 only (2 SAs)
    wire [1:0] sa2_q, sa2_qb;

    // =========================================================
    // Digital Logic
    // =========================================================

    // XOR Controller FSM (v3: single-pass, no digital hidden layer)
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
        .sa2_q        (sa2_q)
    );

    // Input Encoder: inputs → SL1 (Array 1 only)
    input_encoder u_enc (
        .input_a   (input_a),
        .input_b   (input_b),
        .sl_data_1 (sl_data_1)
    );

    // SAE Timing Controller (Layer 2 SAs only)
    sae_control u_sae (
        .clk      (clk),
        .rst_n    (rst_n),
        .trigger  (sae_trigger),
        .sae      (sae),
        .done     (sae_done)
    );

    // =========================================================
    // Analog Macros — Array 1 (Layer 1: 3x5)
    // =========================================================

    // WL Drivers for Array 1 (5 columns)
    wl_driver u_wl_drv_1_0 (.IN(wl_en_1[0]), .OUT(wl_out_1[0]));
    wl_driver u_wl_drv_1_1 (.IN(wl_en_1[1]), .OUT(wl_out_1[1]));
    wl_driver u_wl_drv_1_2 (.IN(wl_en_1[2]), .OUT(wl_out_1[2]));
    wl_driver u_wl_drv_1_3 (.IN(wl_en_1[3]), .OUT(wl_out_1[3]));
    wl_driver u_wl_drv_1_4 (.IN(wl_en_1[4]), .OUT(wl_out_1[4]));

    // BL Write Drivers for Array 1 (disabled during inference)
    bl_write_driver u_bl_wd_1_0 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_1[0]));
    bl_write_driver u_bl_wd_1_1 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_1[1]));
    bl_write_driver u_bl_wd_1_2 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_1[2]));
    bl_write_driver u_bl_wd_1_3 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_1[3]));
    bl_write_driver u_bl_wd_1_4 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_1[4]));

    // RRAM 3x5 Array 1
    rram_array_3x5_260222 u_rram_array_1 (
        .GND (rram_gnd),
        .WL  (wl_out_1),
        .BL  (bl_bus_1),
        .SL  (sl_data_1)
    );

    // =========================================================
    // ReLU Activation (Layer 1 → Layer 2)
    // BL1[i] → ReLU[i] → SL2[i]
    // =========================================================

    relu u_relu_0 (.VBL(bl_bus_1[0]), .VREF(vref), .OUT(relu_out[0]), .VBIAS(vbias));
    relu u_relu_1 (.VBL(bl_bus_1[1]), .VREF(vref), .OUT(relu_out[1]), .VBIAS(vbias));
    relu u_relu_2 (.VBL(bl_bus_1[2]), .VREF(vref), .OUT(relu_out[2]), .VBIAS(vbias));
    relu u_relu_3 (.VBL(bl_bus_1[3]), .VREF(vref), .OUT(relu_out[3]), .VBIAS(vbias));
    relu u_relu_4 (.VBL(bl_bus_1[4]), .VREF(vref), .OUT(relu_out[4]), .VBIAS(vbias));

    // =========================================================
    // Analog Macros — Array 2 (Layer 2: 5x2, AND → XOR)
    // =========================================================

    // WL Drivers for Array 2 (2 columns)
    wl_driver u_wl_drv_2_0 (.IN(wl_en_2[0]), .OUT(wl_out_2[0]));
    wl_driver u_wl_drv_2_1 (.IN(wl_en_2[1]), .OUT(wl_out_2[1]));

    // Sense Amplifiers for Array 2 (2 BLs, each vs VREF)
    sense_amp u_sa_2_0 (
        .SAE (sae),
        .INP (bl_bus_2[0]),
        .INN (vref),
        .Q   (sa2_q[0]),
        .QB  (sa2_qb[0])
    );
    sense_amp u_sa_2_1 (
        .SAE (sae),
        .INP (bl_bus_2[1]),
        .INN (vref),
        .Q   (sa2_q[1]),
        .QB  (sa2_qb[1])
    );

    // BL Write Drivers for Array 2 (disabled during inference)
    bl_write_driver u_bl_wd_2_0 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_2[0]));
    bl_write_driver u_bl_wd_2_1 (.EN(1'b0), .DATA(1'b0), .BL(bl_bus_2[1]));

    // RRAM 5x2 Array 2 (SL driven by ReLU outputs)
    rram_array_5x2_260222 u_rram_array_2 (
        .GND (rram_gnd),
        .WL  (wl_out_2),
        .BL  (bl_bus_2),
        .SL  (relu_out)
    );

endmodule
