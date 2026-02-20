tech load $env(PDK_ROOT)/sky130B/libs.tech/magic/sky130B.tech
drc style drc(full)
drc off
snap internal
cellname delete bl_write_driver
edit

# === NWELL ===
box -3 640 489 1144
paint nwell

# === Col0 (W_n=0.5, W_p=0.5) ===
box 15 128 84 178
paint ndiff
box 15 658 84 708
paint pdiff
box 42 115 57 721
paint poly
box 33 544 66 577
paint poly
box 41 552 58 569
paint polycont
box 33 552 66 569
paint locali
# S/D contacts
box 19 144 36 161
paint ndiffc
box 63 144 80 161
paint ndiffc
box 19 674 36 691
paint pdiffc
box 63 674 80 691
paint pdiffc
# li1 strips (y-direction enclosure)
box 19 136 36 169
paint locali
box 63 136 80 169
paint locali
box 19 666 36 699
paint locali
box 63 666 80 699
paint locali

# === Col1 (W_n=4.0, W_p=4.0) ===
box 144 128 213 528
paint ndiff
box 144 658 213 1058
paint pdiff
box 171 115 186 577
paint poly
box 162 544 195 577
paint poly
box 170 552 187 569
paint polycont
box 162 552 195 569
paint locali
box 171 609 186 1071
paint poly
box 162 609 195 642
paint poly
box 170 617 187 634
paint polycont
box 162 617 195 634
paint locali
# S/D contacts
box 148 139 165 156
paint ndiffc
box 148 175 165 192
paint ndiffc
box 148 211 165 228
paint ndiffc
box 148 247 165 264
paint ndiffc
box 148 283 165 300
paint ndiffc
box 148 319 165 336
paint ndiffc
box 148 355 165 372
paint ndiffc
box 148 391 165 408
paint ndiffc
box 148 427 165 444
paint ndiffc
box 148 463 165 480
paint ndiffc
box 148 499 165 516
paint ndiffc
box 192 139 209 156
paint ndiffc
box 192 175 209 192
paint ndiffc
box 192 211 209 228
paint ndiffc
box 192 247 209 264
paint ndiffc
box 192 283 209 300
paint ndiffc
box 192 319 209 336
paint ndiffc
box 192 355 209 372
paint ndiffc
box 192 391 209 408
paint ndiffc
box 192 427 209 444
paint ndiffc
box 192 463 209 480
paint ndiffc
box 192 499 209 516
paint ndiffc
box 148 669 165 686
paint pdiffc
box 148 705 165 722
paint pdiffc
box 148 741 165 758
paint pdiffc
box 148 777 165 794
paint pdiffc
box 148 813 165 830
paint pdiffc
box 148 849 165 866
paint pdiffc
box 148 885 165 902
paint pdiffc
box 148 921 165 938
paint pdiffc
box 148 957 165 974
paint pdiffc
box 148 993 165 1010
paint pdiffc
box 148 1029 165 1046
paint pdiffc
box 192 669 209 686
paint pdiffc
box 192 705 209 722
paint pdiffc
box 192 741 209 758
paint pdiffc
box 192 777 209 794
paint pdiffc
box 192 813 209 830
paint pdiffc
box 192 849 209 866
paint pdiffc
box 192 885 209 902
paint pdiffc
box 192 921 209 938
paint pdiffc
box 192 957 209 974
paint pdiffc
box 192 993 209 1010
paint pdiffc
box 192 1029 209 1046
paint pdiffc
# li1 strips (y-direction enclosure)
box 148 131 165 524
paint locali
box 192 131 209 524
paint locali
box 148 661 165 1054
paint locali
box 192 661 209 1054
paint locali

# === Col2 (W_n=4.0, W_p=4.0) ===
box 273 128 342 528
paint ndiff
box 273 658 342 1058
paint pdiff
box 300 115 315 1071
paint poly
box 291 609 324 642
paint poly
box 299 617 316 634
paint polycont
box 291 617 324 634
paint locali
# S/D contacts
box 277 139 294 156
paint ndiffc
box 277 175 294 192
paint ndiffc
box 277 211 294 228
paint ndiffc
box 277 247 294 264
paint ndiffc
box 277 283 294 300
paint ndiffc
box 277 319 294 336
paint ndiffc
box 277 355 294 372
paint ndiffc
box 277 391 294 408
paint ndiffc
box 277 427 294 444
paint ndiffc
box 277 463 294 480
paint ndiffc
box 277 499 294 516
paint ndiffc
box 321 139 338 156
paint ndiffc
box 321 175 338 192
paint ndiffc
box 321 211 338 228
paint ndiffc
box 321 247 338 264
paint ndiffc
box 321 283 338 300
paint ndiffc
box 321 319 338 336
paint ndiffc
box 321 355 338 372
paint ndiffc
box 321 391 338 408
paint ndiffc
box 321 427 338 444
paint ndiffc
box 321 463 338 480
paint ndiffc
box 321 499 338 516
paint ndiffc
box 277 669 294 686
paint pdiffc
box 277 705 294 722
paint pdiffc
box 277 741 294 758
paint pdiffc
box 277 777 294 794
paint pdiffc
box 277 813 294 830
paint pdiffc
box 277 849 294 866
paint pdiffc
box 277 885 294 902
paint pdiffc
box 277 921 294 938
paint pdiffc
box 277 957 294 974
paint pdiffc
box 277 993 294 1010
paint pdiffc
box 277 1029 294 1046
paint pdiffc
box 321 669 338 686
paint pdiffc
box 321 705 338 722
paint pdiffc
box 321 741 338 758
paint pdiffc
box 321 777 338 794
paint pdiffc
box 321 813 338 830
paint pdiffc
box 321 849 338 866
paint pdiffc
box 321 885 338 902
paint pdiffc
box 321 921 338 938
paint pdiffc
box 321 957 338 974
paint pdiffc
box 321 993 338 1010
paint pdiffc
box 321 1029 338 1046
paint pdiffc
# li1 strips (y-direction enclosure)
box 277 131 294 524
paint locali
box 321 131 338 524
paint locali
box 277 661 294 1054
paint locali
box 321 661 338 1054
paint locali

# === Col3 (W_n=0.5, W_p=0.5) ===
box 402 128 471 178
paint ndiff
box 402 658 471 708
paint pdiff
box 429 115 444 721
paint poly
box 420 544 453 577
paint poly
box 428 552 445 569
paint polycont
box 420 552 453 569
paint locali
# S/D contacts
box 406 144 423 161
paint ndiffc
box 450 144 467 161
paint ndiffc
box 406 674 423 691
paint pdiffc
box 450 674 467 691
paint pdiffc
# li1 strips (y-direction enclosure)
box 406 136 423 169
paint locali
box 450 136 467 169
paint locali
box 406 666 423 699
paint locali
box 450 666 467 699
paint locali

# === TAPS ===
box 19 72 36 89
paint ptapc
box 63 72 80 89
paint ptapc
box 15 60 84 101
paint ptap
box 19 64 80 97
paint locali
box 19 1097 36 1114
paint ntapc
box 63 1097 80 1114
paint ntapc
box 15 1085 84 1126
paint ntap
box 19 1089 80 1122
paint locali
box 148 72 165 89
paint ptapc
box 192 72 209 89
paint ptapc
box 144 60 213 101
paint ptap
box 148 64 209 97
paint locali
box 148 1097 165 1114
paint ntapc
box 192 1097 209 1114
paint ntapc
box 144 1085 213 1126
paint ntap
box 148 1089 209 1122
paint locali
box 277 72 294 89
paint ptapc
box 321 72 338 89
paint ptapc
box 273 60 342 101
paint ptap
box 277 64 338 97
paint locali
box 277 1097 294 1114
paint ntapc
box 321 1097 338 1114
paint ntapc
box 273 1085 342 1126
paint ntap
box 277 1089 338 1122
paint locali
box 406 72 423 89
paint ptapc
box 450 72 467 89
paint ptapc
box 402 60 471 101
paint ptap
box 406 64 467 97
paint locali
box 406 1097 423 1114
paint ntapc
box 450 1097 467 1114
paint ntapc
box 402 1085 471 1126
paint ntap
box 406 1089 467 1122
paint locali

# === POWER RAILS ===
box 0 0 486 48
paint metal1
box 0 1138 486 1186
paint metal1
# Col0 NFET src→VSS
box 19 144 36 161
paint viali
box 14 48 41 167
paint metal1
box 19 72 36 89
paint viali
box 14 48 41 95
paint metal1
box 63 72 80 89
paint viali
box 58 48 85 95
paint metal1
# Col0 PFET src→VDD
box 19 674 36 691
paint viali
box 14 668 41 1138
paint metal1
box 19 1097 36 1114
paint viali
box 14 1091 41 1138
paint metal1
box 63 1097 80 1114
paint viali
box 58 1091 85 1138
paint metal1
# Col1 NFET src→VSS
box 148 139 165 156
paint viali
box 148 175 165 192
paint viali
box 148 211 165 228
paint viali
box 148 247 165 264
paint viali
box 148 283 165 300
paint viali
box 148 319 165 336
paint viali
box 148 355 165 372
paint viali
box 148 391 165 408
paint viali
box 148 427 165 444
paint viali
box 148 463 165 480
paint viali
box 148 499 165 516
paint viali
box 143 48 170 522
paint metal1
box 148 72 165 89
paint viali
box 143 48 170 95
paint metal1
box 192 72 209 89
paint viali
box 187 48 214 95
paint metal1
# Col1 PFET src→VDD
box 148 669 165 686
paint viali
box 148 705 165 722
paint viali
box 148 741 165 758
paint viali
box 148 777 165 794
paint viali
box 148 813 165 830
paint viali
box 148 849 165 866
paint viali
box 148 885 165 902
paint viali
box 148 921 165 938
paint viali
box 148 957 165 974
paint viali
box 148 993 165 1010
paint viali
box 148 1029 165 1046
paint viali
box 143 663 170 1138
paint metal1
box 148 1097 165 1114
paint viali
box 143 1091 170 1138
paint metal1
box 192 1097 209 1114
paint viali
box 187 1091 214 1138
paint metal1
# Col3 NFET src→VSS
box 406 144 423 161
paint viali
box 401 48 428 167
paint metal1
box 406 72 423 89
paint viali
box 401 48 428 95
paint metal1
box 450 72 467 89
paint viali
box 445 48 472 95
paint metal1
# Col3 PFET src→VDD
box 406 674 423 691
paint viali
box 401 668 428 1138
paint metal1
box 406 1097 423 1114
paint viali
box 401 1091 428 1138
paint metal1
box 450 1097 467 1114
paint viali
box 445 1091 472 1138
paint metal1

# === DRAIN CONNECTIONS ===
# Col0 drain (NFET↔PFET via met2)
box 63 144 80 161
paint viali
box 63 674 80 691
paint viali
box 58 137 85 168
paint metal1
box 58 667 85 698
paint metal1
box 57 141 83 167
paint via1
box 57 138 86 170
paint metal1
box 57 138 86 170
paint metal2
box 57 667 83 693
paint via1
box 57 664 86 696
paint metal1
box 57 664 86 696
paint metal2
box 57 141 84 694
paint metal2
# Col3 drain (NFET↔PFET via met2)
box 450 144 467 161
paint viali
box 450 674 467 691
paint viali
box 445 137 472 168
paint metal1
box 445 667 472 698
paint metal1
box 444 141 470 167
paint via1
box 444 138 473 170
paint metal1
box 444 138 473 170
paint metal2
box 444 667 470 693
paint via1
box 444 664 473 696
paint metal1
box 444 664 473 696
paint metal2
box 444 141 471 694
paint metal2
# NET_P: Col1 PFET drain → Col2 PFET source
box 192 669 209 686
paint viali
box 192 705 209 722
paint viali
box 192 741 209 758
paint viali
box 192 777 209 794
paint viali
box 192 813 209 830
paint viali
box 192 849 209 866
paint viali
box 192 885 209 902
paint viali
box 192 921 209 938
paint viali
box 192 957 209 974
paint viali
box 192 993 209 1010
paint viali
box 192 1029 209 1046
paint viali
box 277 669 294 686
paint viali
box 277 705 294 722
paint viali
box 277 741 294 758
paint viali
box 277 777 294 794
paint viali
box 277 813 294 830
paint viali
box 277 849 294 866
paint viali
box 277 885 294 902
paint viali
box 277 921 294 938
paint viali
box 277 957 294 974
paint viali
box 277 993 294 1010
paint viali
box 277 1029 294 1046
paint viali
box 187 663 214 1052
paint metal1
box 272 663 299 1052
paint metal1
box 187 843 299 872
paint metal1
# NET_N: Col1 NFET drain → Col2 NFET source
box 192 139 209 156
paint viali
box 192 175 209 192
paint viali
box 192 211 209 228
paint viali
box 192 247 209 264
paint viali
box 192 283 209 300
paint viali
box 192 319 209 336
paint viali
box 192 355 209 372
paint viali
box 192 391 209 408
paint viali
box 192 427 209 444
paint viali
box 192 463 209 480
paint viali
box 192 499 209 516
paint viali
box 277 139 294 156
paint viali
box 277 175 294 192
paint viali
box 277 211 294 228
paint viali
box 277 247 294 264
paint viali
box 277 283 294 300
paint viali
box 277 319 294 336
paint viali
box 277 355 294 372
paint viali
box 277 391 294 408
paint viali
box 277 427 294 444
paint viali
box 277 463 294 480
paint viali
box 277 499 294 516
paint viali
box 187 133 214 522
paint metal1
box 272 133 299 522
paint metal1
box 187 313 299 342
paint metal1
# BL: Col2 drain NFET↔PFET via met2
box 321 139 338 156
paint viali
box 321 175 338 192
paint viali
box 321 211 338 228
paint viali
box 321 247 338 264
paint viali
box 321 283 338 300
paint viali
box 321 319 338 336
paint viali
box 321 355 338 372
paint viali
box 321 391 338 408
paint viali
box 321 427 338 444
paint viali
box 321 463 338 480
paint viali
box 321 499 338 516
paint viali
box 321 669 338 686
paint viali
box 321 705 338 722
paint viali
box 321 741 338 758
paint viali
box 321 777 338 794
paint viali
box 321 813 338 830
paint viali
box 321 849 338 866
paint viali
box 321 885 338 902
paint viali
box 321 921 338 938
paint viali
box 321 957 338 974
paint viali
box 321 993 338 1010
paint viali
box 321 1029 338 1046
paint viali
box 316 133 343 522
paint metal1
box 316 663 343 1052
paint metal1
box 315 495 341 521
paint via1
box 315 492 344 524
paint metal1
box 315 492 344 524
paint metal2
box 315 663 341 689
paint via1
box 315 660 344 692
paint metal1
box 315 660 344 692
paint metal2
box 315 495 342 690
paint metal2

# === GATE ROUTING ===
# EN: Col0 gate → Col1 NFET gate (lower track met1)
box 41 552 58 569
paint viali
box 170 552 187 569
paint viali
box 35 547 193 574
paint metal1
# EN_B: Col0 drain → Col1 PFET gate (upper track met1)
box 57 611 83 637
paint via1
box 57 608 86 640
paint metal1
box 57 608 86 640
paint metal2
box 170 617 187 634
paint viali
box 57 612 193 639
paint metal1
# DATA_B: Col3 drain → Col2 gate (upper track met1)
box 444 611 470 637
paint via1
box 444 608 473 640
paint metal1
box 444 608 473 640
paint metal2
box 299 617 316 634
paint viali
box 293 612 471 639
paint metal1

# === SIGNAL PINS ===
# DATA pin met1
box 428 552 445 569
paint viali
box 422 546 451 575
paint metal1

# === LABELS & PORTS ===
box 35 547 193 574
label EN s metal1
port make 1
box 422 546 451 575
label DATA s metal1
port make 2
box 316 133 343 522
label BL s metal1
port make 3
box 0 1138 486 1186
label VDD s metal1
port make 4
box 0 0 486 48
label VSS s metal1
port make 5

# === SAVE + DRC + EXTRACT ===
save bl_write_driver
drc on
drc check
drc catchup
select top cell
drc why
drc count
extract all
ext2spice lvs
ext2spice
gds write bl_write_driver.gds
quit -noprompt