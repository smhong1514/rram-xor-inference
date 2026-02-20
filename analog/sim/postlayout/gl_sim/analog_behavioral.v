// Behavioral models for analog macros (gate-level simulation)
// Models functional behavior for post-layout digital verification.
// Actual analog performance verified separately in SPICE.

`timescale 1ns / 1ps

// ============================================================
// RRAM 4x4 Array — Behavioral CIM Model
// ============================================================
// MODE=0 (Array 1): OR on BL[0:1], NAND on BL[2:3]
// MODE=1 (Array 2): AND on BL[0:1], BL[2:3] unused
//
// Inputs: SL[0]=input_x, SL[1]=input_y, SL[2:3]=bias(1)
// BL driven when any WL is active. Hi-Z when WL all off.
// Use defparam to set MODE per instance in testbench.

module rram_4x4_array (
    inout  wire       GND,
    input  wire [3:0] WL,
    inout  wire [3:0] BL,
    inout  wire [3:0] SL
);
    parameter MODE = 0;  // 0=OR+NAND (Layer1), 1=AND (Layer2)

    wire active = |WL;   // Any WL active
    wire x = SL[0];      // First input
    wire y = SL[1];      // Second input

    reg [3:0] bl_drive;

    always @(*) begin
        if (MODE == 0) begin
            // Layer 1: OR + NAND
            bl_drive[0] = x | y;        // OR positive
            bl_drive[1] = ~(x | y);     // OR reference
            bl_drive[2] = ~(x & y);     // NAND positive
            bl_drive[3] = x & y;        // NAND reference
        end else begin
            // Layer 2: AND
            bl_drive[0] = x & y;        // AND positive
            bl_drive[1] = ~(x & y);     // AND reference
            bl_drive[2] = 1'b0;
            bl_drive[3] = 1'b0;
        end
    end

    // Drive BL with ~2ns delay (models RRAM current settling)
    // Hi-Z when WL inactive (BL Write Driver or precharge controls BL)
    assign #2 BL[0] = active ? bl_drive[0] : 1'bz;
    assign #2 BL[1] = active ? bl_drive[1] : 1'bz;
    assign #2 BL[2] = active ? bl_drive[2] : 1'bz;
    assign #2 BL[3] = active ? bl_drive[3] : 1'bz;

endmodule

// ============================================================
// WL Driver — Behavioral Model
// ============================================================
// Level shifter: 1.8V digital IN → VWL high-voltage OUT
// Functionally: non-inverting buffer

module wl_driver (
    input  wire IN,
    output wire OUT
);
    assign #0.5 OUT = IN;
endmodule

// ============================================================
// Sense Amplifier — Behavioral Model (Latch-type)
// ============================================================
// StrongARM latch: cross-coupled inverters HOLD result after SAE falls.
// SAE rising edge: evaluate (compare INP vs INN)
// SAE=0: latch holds previous result (real SA retains state)

module sense_amp (
    input  wire SAE,
    input  wire INP,
    input  wire INN,
    output wire Q,
    output wire QB
);
    reg q_latch;

    // Latch comparison result on SAE rising edge, hold until next SAE pulse
    always @(posedge SAE) begin
        if (INP === 1'bz || INN === 1'bz)
            q_latch <= 1'b0;
        else if (INP > INN)
            q_latch <= 1'b1;
        else
            q_latch <= 1'b0;
    end

    initial q_latch = 1'b0;

    assign #0.3 Q  = q_latch;
    assign #0.3 QB = ~q_latch;
endmodule

// ============================================================
// BL Write Driver — Behavioral Model
// ============================================================
// Tri-state buffer: EN=1 → BL=DATA, EN=0 → Hi-Z

module bl_write_driver (
    input  wire EN,
    input  wire DATA,
    output wire BL
);
    assign #0.5 BL = EN ? DATA : 1'bz;
endmodule

// Note: sky130_ef_sc_hd__decap_12 is already in sky130_fd_sc_hd.v
