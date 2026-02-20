// WL Driver Blackbox
// Level shifter: 1.8V digital → VWL high-voltage output
// 8 transistors (2x 1.8V + 6x 5V HV)
// Power pins (VDD, VWL, VSS) handled by PDN, not in Verilog

(* blackbox *)
module wl_driver (
    input  wire IN,      // Digital input (1.8V)
    output wire OUT      // High-voltage output (VWL level)
);
endmodule
