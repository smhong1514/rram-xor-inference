// Gate-Level Testbench for rram_ctrl_top (XOR Inference)
// Tests the final synthesized netlist with SDF timing back-annotation.
// Analog macros use behavioral models.
//
// Test: All 4 XOR input combinations → verify correct output.

`timescale 1ns / 1ps

module tb_gl_xor;

    // DUT signals
    reg  clk, rst_n, start, input_a, input_b;
    wire xor_result, result_valid, ready, phase, sae;
    wire rram_gnd;

    // Power pins
    wire vccd1, vssd1;
    assign vccd1 = 1'b1;
    assign vssd1 = 1'b0;

    // RRAM ground
    assign rram_gnd = 1'b0;

    // Instantiate DUT (gate-level netlist)
    rram_ctrl_top dut (
        .vccd1       (vccd1),
        .vssd1       (vssd1),
        .clk         (clk),
        .rst_n       (rst_n),
        .rram_gnd    (rram_gnd),
        .start       (start),
        .input_a     (input_a),
        .input_b     (input_b),
        .xor_result  (xor_result),
        .result_valid(result_valid),
        .ready       (ready),
        .phase       (phase),
        .sae         (sae)
    );

    // Configure RRAM array instances (weight programming)
    defparam dut.u_rram_array_1.MODE = 0;  // Array 1: OR + NAND
    defparam dut.u_rram_array_2.MODE = 1;  // Array 2: AND

    // Clock: 20MHz (50ns period)
    initial clk = 0;
    always #25 clk = ~clk;

    // Test variables
    integer pass_count = 0;
    integer fail_count = 0;
    integer test_num = 0;
    reg [0:0] expected;

    // VCD dump for waveform viewing
    initial begin
        $dumpfile("gl_xor_sim.vcd");
        $dumpvars(0, tb_gl_xor);
    end

    // Main test sequence
    initial begin
        $display("");
        $display("============================================================");
        $display("Gate-Level XOR Inference Test (Post-Layout Netlist + SDF)");
        $display("============================================================");
        $display("Clock: 20MHz (50ns), XOR(A,B) = AND(OR(A,B), NAND(A,B))");
        $display("");

        // Reset
        rst_n   = 0;
        start   = 0;
        input_a = 0;
        input_b = 0;
        #200;  // 4 clock cycles reset
        rst_n = 1;
        #100;  // Wait for ready

        // Test all 4 XOR combinations
        run_xor_test(0, 0, 0);  // XOR(0,0) = 0
        run_xor_test(0, 1, 1);  // XOR(0,1) = 1
        run_xor_test(1, 0, 1);  // XOR(1,0) = 1
        run_xor_test(1, 1, 0);  // XOR(1,1) = 0

        // Summary
        $display("");
        $display("============================================================");
        $display("RESULT: %0d/%0d PASS", pass_count, pass_count + fail_count);
        if (fail_count == 0)
            $display("*** ALL TESTS PASSED ***");
        else
            $display("*** %0d TESTS FAILED ***", fail_count);
        $display("============================================================");

        #100;
        $finish;
    end

    // Task: run one XOR test
    task run_xor_test;
        input a_val, b_val, exp_val;
        begin
            test_num = test_num + 1;

            // Wait for ready
            wait(ready == 1'b1);
            @(posedge clk);
            #1;

            // Apply inputs and start
            input_a = a_val;
            input_b = b_val;
            start   = 1;
            @(posedge clk);
            #1;
            start = 0;

            // Wait for result_valid
            wait(result_valid == 1'b1);
            @(posedge clk);
            #1;

            // Check result
            if (xor_result === exp_val) begin
                $display("  [PASS] Test %0d: XOR(%0b, %0b) = %0b (expected %0b)",
                         test_num, a_val, b_val, xor_result, exp_val);
                pass_count = pass_count + 1;
            end else begin
                $display("  [FAIL] Test %0d: XOR(%0b, %0b) = %0b (expected %0b)",
                         test_num, a_val, b_val, xor_result, exp_val);
                fail_count = fail_count + 1;
            end

            // Wait a few cycles before next test
            repeat(3) @(posedge clk);
        end
    endtask

    // Timeout watchdog
    initial begin
        #100000;  // 100us
        $display("[TIMEOUT] Simulation exceeded 100us");
        $finish;
    end

    // Monitor key signals
    initial begin
        $monitor("  t=%0t clk=%b rst_n=%b start=%b A=%b B=%b | phase=%b sae=%b | result=%b valid=%b ready=%b",
                 $time, clk, rst_n, start, input_a, input_b,
                 phase, sae, xor_result, result_valid, ready);
    end

endmodule
