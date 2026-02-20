// RRAM Controller FSM
// Controls read/write operations for 4x4 RRAM array

module controller (
    input  wire        clk,
    input  wire        rst_n,

    // Command interface
    input  wire        cmd_valid,
    input  wire        cmd_write,    // 1=write, 0=read
    input  wire [1:0]  cmd_row,
    input  wire [1:0]  cmd_col,
    input  wire        cmd_data,     // Data to write
    output reg         cmd_ready,

    // Response interface
    output reg         resp_valid,
    output reg         resp_data,

    // Array control
    output reg  [3:0]  wl_sel,       // Wordline select (active high)
    output reg  [3:0]  sl_sel,       // Sourceline select
    output reg  [3:0]  bl_en,        // Bitline driver enable
    output reg  [3:0]  bl_data,      // Data to write on bitlines
    input  wire [3:0]  bl_sense,     // Sensed data from bitlines

    // Control signals
    output reg         write_en,
    output reg         read_en
);

    // FSM states
    localparam IDLE       = 3'd0;
    localparam DECODE     = 3'd1;
    localparam READ_SENSE = 3'd2;
    localparam READ_DONE  = 3'd3;
    localparam WRITE_PROG = 3'd4;
    localparam WRITE_DONE = 3'd5;

    reg [2:0] state, next_state;
    reg [1:0] row_reg, col_reg;
    reg       data_reg, write_reg;
    reg [13:0] cycle_cnt;

    // State register
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    // Next state logic
    always @(*) begin
        next_state = state;
        case (state)
            IDLE: begin
                if (cmd_valid && cmd_ready)
                    next_state = DECODE;
            end
            DECODE: begin
                if (write_reg)
                    next_state = WRITE_PROG;
                else
                    next_state = READ_SENSE;
            end
            READ_SENSE: begin
                if (cycle_cnt >= 14'd5)
                    next_state = READ_DONE;
            end
            READ_DONE: begin
                next_state = IDLE;
            end
            WRITE_PROG: begin
                if (cycle_cnt >= 14'd4999)
                    next_state = WRITE_DONE;
            end
            WRITE_DONE: begin
                next_state = IDLE;
            end
            default: next_state = IDLE;
        endcase
    end

    // Cycle counter
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            cycle_cnt <= 14'd0;
        else if (state == IDLE || state == DECODE)
            cycle_cnt <= 14'd0;
        else
            cycle_cnt <= cycle_cnt + 1'b1;
    end

    // Capture command
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            row_reg   <= 2'd0;
            col_reg   <= 2'd0;
            data_reg  <= 1'b0;
            write_reg <= 1'b0;
        end else if (state == IDLE && cmd_valid && cmd_ready) begin
            row_reg   <= cmd_row;
            col_reg   <= cmd_col;
            data_reg  <= cmd_data;
            write_reg <= cmd_write;
        end
    end

    // Output logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cmd_ready  <= 1'b1;
            resp_valid <= 1'b0;
            resp_data  <= 1'b0;
            wl_sel     <= 4'b0000;
            sl_sel     <= 4'b0000;
            bl_en      <= 4'b0000;
            bl_data    <= 4'b0000;
            write_en   <= 1'b0;
            read_en    <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    cmd_ready  <= 1'b1;
                    resp_valid <= 1'b0;
                    wl_sel     <= 4'b0000;
                    sl_sel     <= 4'b0000;
                    bl_en      <= 4'b0000;
                    write_en   <= 1'b0;
                    read_en    <= 1'b0;
                end
                DECODE: begin
                    cmd_ready <= 1'b0;
                    wl_sel    <= (4'b0001 << row_reg);  // Row select for WL (gate)
                    sl_sel    <= (4'b0001 << row_reg);  // Row select for SL (current return path)
                end
                READ_SENSE: begin
                    read_en <= (cycle_cnt >= 14'd3) ? 1'b1 : 1'b0;  // Delay SA: 20ns BL settling
                    bl_en   <= 4'b0000;  // Don't drive BL during read
                end
                READ_DONE: begin
                    resp_valid <= 1'b1;
                    resp_data  <= bl_sense[col_reg];
                    read_en    <= 1'b0;
                end
                WRITE_PROG: begin
                    write_en <= 1'b1;
                    bl_en    <= (4'b0001 << col_reg);
                    bl_data  <= data_reg ? (4'b0001 << col_reg) : 4'b0000;
                end
                WRITE_DONE: begin
                    sl_sel     <= 4'b0000;  // Cut SL ground path to preserve filament
                    resp_valid <= 1'b1;
                    resp_data  <= 1'b1;  // Write success
                    write_en   <= 1'b0;
                    bl_en      <= 4'b0000;
                end
            endcase
        end
    end

endmodule
