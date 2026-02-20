// Test module with async reset (like our controller)
module test_asyncrst (
    input wire clk,
    input wire rst_n,
    input wire start,
    output reg [3:0] count,
    output reg active
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 0;
            active <= 0;
        end else begin
            if (start) begin
                active <= 1;
                count <= count + 1;
            end else begin
                active <= 0;
            end
        end
    end
endmodule
