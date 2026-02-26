# ReLU Analog Macro (v3)

5T OTA comparator + CMOS inverter buffer. Implements analog ReLU activation between RRAM Array 1 BL and Array 2 SL.

## Circuit

```
VBL → M2 (nfet, signal)
VREF → M1 (nfet, reference)
M3/M4: PMOS current mirror
M5: tail current source (gate=VBIAS)
+ CMOS inverter output buffer (NFET W=10, PMOS W=4)
```

## Behavior

| VBL condition | OUT (→SL2) |
|---------------|------------|
| VBL < VREF (neuron active) | HIGH |
| VBL > VREF (neuron inactive) | LOW |

## Key Parameters

- VREF = 1.25V (shared with SA)
- VBIAS = 0.6V
- Size: ~3.04 x 10.86 um

## Files

| File | Description |
|------|-------------|
| relu.mag | Magic layout |
| relu.gds | GDS (for OpenLane) |
| relu.lef | LEF (for OpenLane placement) |
| relu.lib | Liberty file (blackbox timing) |
| relu.spice | Extracted netlist |
| relu_flat.spice | Flat extracted netlist (LVS) |
| relu_schematic.spice | Schematic SPICE |
| relu_lvs_result.txt | LVS result (0 errors) |

## LVS Status: PASS (0 errors)
