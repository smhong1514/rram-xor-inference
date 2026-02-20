// d_cosim wrapper for RRAM controller
// Reorders ports: all inputs first, all outputs second
// This is required for ngspice d_cosim digital co-simulation

module controller_cosim (
    // --- Inputs (13 bits total) ---
    input wire        clk,
    input wire        rst_n,
    input wire        cmd_valid,
    input wire        cmd_write,
    input wire [1:0]  cmd_row,
    input wire [1:0]  cmd_col,
    input wire        cmd_data,
    input wire [3:0]  bl_sense,
    // --- Outputs (21 bits total) ---
    output wire        cmd_ready,
    output wire        resp_valid,
    output wire        resp_data,
    output wire [3:0]  wl_sel,
    output wire [3:0]  sl_sel,
    output wire [3:0]  bl_en,
    output wire [3:0]  bl_data,
    output wire        write_en,
    output wire        read_en
);

    controller u_ctrl (
        .clk        (clk),
        .rst_n      (rst_n),
        .cmd_valid  (cmd_valid),
        .cmd_write  (cmd_write),
        .cmd_row    (cmd_row),
        .cmd_col    (cmd_col),
        .cmd_data   (cmd_data),
        .cmd_ready  (cmd_ready),
        .resp_valid (resp_valid),
        .resp_data  (resp_data),
        .wl_sel     (wl_sel),
        .sl_sel     (sl_sel),
        .bl_en      (bl_en),
        .bl_data    (bl_data),
        .bl_sense   (bl_sense),
        .write_en   (write_en),
        .read_en    (read_en)
    );

endmodule
