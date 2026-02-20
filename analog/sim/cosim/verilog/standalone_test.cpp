// Standalone test of Verilator-compiled controller
#include "verilated.h"
#include "Vlng.h"
#include <cstdio>

int main(int argc, char **argv) {
    VerilatedContext *ctx = new VerilatedContext;
    Vlng *top = new Vlng(ctx);

    printf("=== Standalone Verilator test ===\n");

    // Apply reset
    top->clk = 0; top->rst_n = 0;
    top->cmd_valid = 0; top->cmd_write = 0;
    top->cmd_row = 0; top->cmd_col = 0;
    top->cmd_data = 0; top->bl_sense = 5; // 0101
    top->eval();
    printf("After reset assert:   cmd_ready=%d state(internal)=?\n", top->cmd_ready);

    // Clock cycle with reset active
    top->clk = 1; top->eval();
    printf("posedge clk (rst=0): cmd_ready=%d\n", top->cmd_ready);
    top->clk = 0; top->eval();

    // Release reset
    top->rst_n = 1; top->eval();
    printf("rst_n deassert:      cmd_ready=%d\n", top->cmd_ready);

    // Clock with rst=1, no cmd_valid
    top->clk = 1; top->eval();
    printf("posedge clk (idle):  cmd_ready=%d resp_valid=%d\n",
           top->cmd_ready, top->resp_valid);
    top->clk = 0; top->eval();

    // Another idle cycle
    top->clk = 1; top->eval();
    printf("posedge clk (idle2): cmd_ready=%d\n", top->cmd_ready);
    top->clk = 0; top->eval();

    // Set cmd_valid=1, cmd_write=0 (READ), cmd_row=1, cmd_col=2
    top->cmd_valid = 1;
    top->cmd_write = 0;
    top->cmd_row = 1;
    top->cmd_col = 2;
    printf("Set cmd_valid=1 (read, row=1, col=2)\n");

    // Clock edge - should go IDLE→DECODE
    top->clk = 1; top->eval();
    printf("posedge (expect DECODE): cmd_ready=%d wl_sel=%d read_en=%d\n",
           top->cmd_ready, top->wl_sel, top->read_en);
    top->clk = 0; top->eval();

    // Clock edge - should go DECODE→READ_SENSE
    top->clk = 1; top->eval();
    printf("posedge (expect READ_SENSE): cmd_ready=%d wl_sel=%d read_en=%d\n",
           top->cmd_ready, top->wl_sel, top->read_en);
    top->clk = 0; top->eval();

    // More clock cycles for READ
    for (int i = 0; i < 5; i++) {
        top->clk = 1; top->eval();
        printf("posedge READ[%d]: resp_valid=%d resp_data=%d read_en=%d wl_sel=%d\n",
               i, top->resp_valid, top->resp_data, top->read_en, top->wl_sel);
        top->clk = 0; top->eval();
    }

    printf("=== Test complete ===\n");
    delete top;
    delete ctx;
    return 0;
}
