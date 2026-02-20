// Minimal test module for d_cosim debugging
module test_simple (
    input wire clk,
    input wire start,
    output reg [3:0] count,
    output reg active
);
    initial begin
        count = 0;
        active = 0;
    end

    always @(posedge clk) begin
        if (start) begin
            active <= 1;
            count <= count + 1;
        end else begin
            active <= 0;
        end
    end
endmodule
