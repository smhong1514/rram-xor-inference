// SAE (Sense Amplifier Enable) Timing Controller
// Generates SAE pulse with proper timing:
//   trigger → [SAE_WIDTH cycles of SAE=1] → done
//
// SAE=0: SA precharge (Q=QB=VDD)
// SAE=1: SA evaluate (differential amplify → full-swing output)

module sae_control (
    input  wire clk,
    input  wire rst_n,
    input  wire trigger,    // Start SAE pulse (one-cycle pulse)
    output reg  sae,        // SAE output to Sense Amplifier
    output reg  done        // Pulse when SAE sequence completes
);

    // SAE pulse width (clock cycles)
    // At 20MHz (50ns period): 3 cycles = 150ns >> SA resolution time (~230ps)
    localparam SAE_WIDTH = 3'd3;

    reg [2:0] cnt;
    reg       active;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sae    <= 1'b0;
            done   <= 1'b0;
            cnt    <= 3'd0;
            active <= 1'b0;
        end else begin
            done <= 1'b0;  // Default: done is pulse

            if (trigger && !active) begin
                // Start SAE sequence
                active <= 1'b1;
                sae    <= 1'b1;
                cnt    <= 3'd0;
            end else if (active) begin
                if (cnt >= SAE_WIDTH - 1) begin
                    // SAE pulse complete
                    sae    <= 1'b0;
                    done   <= 1'b1;
                    active <= 1'b0;
                    cnt    <= 3'd0;
                end else begin
                    cnt <= cnt + 3'd1;
                end
            end
        end
    end

endmodule
