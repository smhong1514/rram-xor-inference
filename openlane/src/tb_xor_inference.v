// Testbench for XOR Inference Controller
// Verifies 3-phase FSM timing and all 4 XOR input combinations

`timescale 1ns/1ps

module tb_xor_inference;

    reg        clk, rst_n;
    reg        start, input_a, input_b;
    wire       xor_result, result_valid, ready;
    wire [1:0] phase;
    wire       sae;

    // SA feedback: model ideal SA behavior
    // In real hardware, these come from analog SA macros
    reg        sa1_q, sa2_q;

    // DUT
    rram_ctrl_top dut (
        .clk          (clk),
        .rst_n        (rst_n),
        .rram_gnd     (),
        .start        (start),
        .input_a      (input_a),
        .input_b      (input_b),
        .xor_result   (xor_result),
        .result_valid (result_valid),
        .ready        (ready),
        .phase        (phase),
        .sae          (sae),
        .sa1_q        (sa1_q),
        .sa2_q        (sa2_q)
    );

    // Clock: 20MHz (50ns period)
    initial clk = 0;
    always #25 clk = ~clk;

    // XOR truth table for SA model
    // OR(A,B):   0,0→0  0,1→1  1,0→1  1,1→1
    // NAND(A,B): 0,0→1  0,1→1  1,0→1  1,1→0
    // AND(h1,h2): computed from h1,h2
    reg a_cap, b_cap;
    reg h1_model, h2_model;

    // Model SA: provide correct digital output based on phase
    // SA resolves during SAE=1 and output is latched after SAE falls
    always @(*) begin
        case (phase)
            2'd0: begin // OR phase → SA1
                sa1_q = a_cap | b_cap;
                sa2_q = 1'b0;
            end
            2'd1: begin // NAND phase → SA2
                sa1_q = 1'b0;
                sa2_q = ~(a_cap & b_cap);
            end
            2'd2: begin // AND phase → SA1
                sa1_q = h1_model & h2_model;
                sa2_q = 1'b0;
            end
            default: begin
                sa1_q = 1'b0;
                sa2_q = 1'b0;
            end
        endcase
    end

    // Track h1, h2 from controller's internal state
    always @(posedge clk) begin
        if (phase == 2'd0 && dut.u_ctrl.state == 4) // LATCH state
            h1_model <= a_cap | b_cap;
        if (phase == 2'd1 && dut.u_ctrl.state == 4)
            h2_model <= ~(a_cap & b_cap);
    end

    integer pass_cnt, fail_cnt;
    reg expected;

    task run_xor_test(input reg a, input reg b);
        begin
            @(posedge clk);
            a_cap   = a;
            b_cap   = b;
            input_a = a;
            input_b = b;
            start   = 1'b1;
            @(posedge clk);
            start = 1'b0;

            // Wait for result
            wait(result_valid);
            @(posedge clk);

            expected = a ^ b;
            if (xor_result == expected) begin
                $display("PASS: A=%b B=%b → XOR=%b (expected %b)", a, b, xor_result, expected);
                pass_cnt = pass_cnt + 1;
            end else begin
                $display("FAIL: A=%b B=%b → XOR=%b (expected %b)", a, b, xor_result, expected);
                fail_cnt = fail_cnt + 1;
            end

            // Wait for ready
            wait(ready);
            @(posedge clk);
        end
    endtask

    initial begin
        $dumpfile("/tmp/xor_inference.vcd");
        $dumpvars(0, tb_xor_inference);

        // Initialize
        rst_n   = 0;
        start   = 0;
        input_a = 0;
        input_b = 0;
        sa1_q   = 0;
        sa2_q   = 0;
        h1_model = 0;
        h2_model = 0;
        pass_cnt = 0;
        fail_cnt = 0;

        // Reset
        repeat(5) @(posedge clk);
        rst_n = 1;
        repeat(2) @(posedge clk);

        $display("");
        $display("========================================");
        $display("  XOR Inference Controller Test");
        $display("========================================");

        // Test all 4 combinations
        run_xor_test(0, 0);  // 0 XOR 0 = 0
        run_xor_test(0, 1);  // 0 XOR 1 = 1
        run_xor_test(1, 0);  // 1 XOR 0 = 1
        run_xor_test(1, 1);  // 1 XOR 1 = 0

        $display("");
        $display("========================================");
        $display("  Result: %0d PASS / %0d FAIL", pass_cnt, fail_cnt);
        $display("========================================");

        if (fail_cnt == 0)
            $display("  ALL TESTS PASSED!");
        else
            $display("  SOME TESTS FAILED!");

        $display("");
        #100;
        $finish;
    end

    // Timeout
    initial begin
        #100000;
        $display("TIMEOUT!");
        $finish;
    end

    // Monitor phase transitions
    always @(phase) begin
        case (phase)
            2'd0: $display("  [%0t] Phase 0: OR computation", $time);
            2'd1: $display("  [%0t] Phase 1: NAND computation", $time);
            2'd2: $display("  [%0t] Phase 2: AND computation", $time);
            2'd3: $display("  [%0t] Phase 3: Idle", $time);
        endcase
    end

endmodule
