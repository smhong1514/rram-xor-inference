// Test with same port count as controller (13 in bits, 21 out bits)
module test_manyports (
    input wire        clk,
    input wire        rst_n,
    input wire        cmd_valid,
    input wire        cmd_write,
    input wire [1:0]  cmd_row,
    input wire [1:0]  cmd_col,
    input wire        cmd_data,
    input wire [3:0]  bl_sense,
    output reg        cmd_ready,
    output reg        resp_valid,
    output reg        resp_data,
    output reg [3:0]  wl_sel,
    output reg [3:0]  sl_sel,
    output reg [3:0]  bl_en,
    output reg [3:0]  bl_data,
    output reg        write_en,
    output reg        read_en
);
    reg [2:0] state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state      <= 0;
            cmd_ready  <= 1;
            resp_valid <= 0;
            resp_data  <= 0;
            wl_sel     <= 0;
            sl_sel     <= 0;
            bl_en      <= 0;
            bl_data    <= 0;
            write_en   <= 0;
            read_en    <= 0;
        end else begin
            case (state)
                3'd0: begin // IDLE
                    cmd_ready  <= 1;
                    resp_valid <= 0;
                    wl_sel     <= 0;
                    sl_sel     <= 0;
                    bl_en      <= 0;
                    write_en   <= 0;
                    read_en    <= 0;
                    if (cmd_valid && cmd_ready) begin
                        state   <= 3'd1;
                    end
                end
                3'd1: begin // DECODE
                    cmd_ready <= 0;
                    wl_sel    <= (4'b0001 << cmd_row);
                    sl_sel    <= (4'b0001 << cmd_row);
                    if (cmd_write)
                        state <= 3'd2; // WRITE
                    else
                        state <= 3'd3; // READ
                end
                3'd2: begin // WRITE
                    write_en <= 1;
                    bl_en    <= (4'b0001 << cmd_col);
                    bl_data  <= cmd_data ? (4'b0001 << cmd_col) : 4'b0000;
                    resp_valid <= 1;
                    resp_data  <= 1;
                    state <= 3'd0;
                end
                3'd3: begin // READ
                    read_en <= 1;
                    resp_valid <= 1;
                    resp_data  <= bl_sense[cmd_col];
                    state <= 3'd0;
                end
                default: state <= 3'd0;
            endcase
        end
    end
endmodule
