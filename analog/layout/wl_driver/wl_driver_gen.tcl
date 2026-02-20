tech load $env(PDK_ROOT)/sky130B/libs.tech/magic/sky130B.tech
drc style drc(full)
drc off
snap internal
cellname delete wl_driver
edit

# === NWELL ===
box -3 620 102 1134
paint nwell
box 311 605 801 1149
paint nwell

# === Col0 devices ===
box 15 213 84 263
paint ndiff
box 42 213 57 263
paint nmos
box 15 788 84 888
paint pdiff
box 42 788 57 888
paint pmos
box 42 200 57 901
paint poly
box 12 471 45 504
paint poly
box 12 471 57 504
paint poly
box 20 479 37 496
paint polycont
box 12 479 45 496
paint locali
box 19 229 36 246
paint ndiffc
box 63 229 80 246
paint ndiffc
box 19 811 36 828
paint pdiffc
box 19 847 36 864
paint pdiffc
box 63 811 80 828
paint pdiffc
box 63 847 80 864
paint pdiffc
box 19 221 36 254
paint locali
box 63 221 80 254
paint locali
box 19 803 36 872
paint locali
box 63 803 80 872
paint locali

# === Col1 devices ===
box 344 138 452 338
paint mvndiff
box 373 138 423 338
paint mvnmos
box 344 788 452 888
paint mvpdiff
box 373 788 423 888
paint mvpmos
box 373 119 423 387
paint poly
box 373 589 423 907
paint poly
box 342 354 375 387
paint poly
box 342 354 423 387
paint poly
box 350 362 367 379
paint polycont
box 342 362 375 379
paint locali
box 342 589 375 622
paint poly
box 342 589 423 622
paint poly
box 350 597 367 614
paint polycont
box 342 597 375 614
paint locali
box 348 157 365 174
paint mvndiffc
box 348 193 365 210
paint mvndiffc
box 348 229 365 246
paint mvndiffc
box 348 265 365 282
paint mvndiffc
box 348 301 365 318
paint mvndiffc
box 429 157 446 174
paint mvndiffc
box 429 193 446 210
paint mvndiffc
box 429 229 446 246
paint mvndiffc
box 429 265 446 282
paint mvndiffc
box 429 301 446 318
paint mvndiffc
box 348 811 365 828
paint mvpdiffc
box 348 847 365 864
paint mvpdiffc
box 429 811 446 828
paint mvpdiffc
box 429 847 446 864
paint mvpdiffc
box 348 149 365 326
paint locali
box 429 149 446 326
paint locali
box 348 803 365 872
paint locali
box 429 803 446 872
paint locali

# === Col2 devices ===
box 502 138 610 338
paint mvndiff
box 531 138 581 338
paint mvnmos
box 502 788 610 888
paint mvpdiff
box 531 788 581 888
paint mvpmos
box 531 119 581 387
paint poly
box 531 589 581 907
paint poly
box 500 354 533 387
paint poly
box 500 354 581 387
paint poly
box 508 362 525 379
paint polycont
box 500 362 533 379
paint locali
box 500 589 533 622
paint poly
box 500 589 581 622
paint poly
box 508 597 525 614
paint polycont
box 500 597 533 614
paint locali
box 506 157 523 174
paint mvndiffc
box 506 193 523 210
paint mvndiffc
box 506 229 523 246
paint mvndiffc
box 506 265 523 282
paint mvndiffc
box 506 301 523 318
paint mvndiffc
box 587 157 604 174
paint mvndiffc
box 587 193 604 210
paint mvndiffc
box 587 229 604 246
paint mvndiffc
box 587 265 604 282
paint mvndiffc
box 587 301 604 318
paint mvndiffc
box 506 811 523 828
paint mvpdiffc
box 506 847 523 864
paint mvpdiffc
box 587 811 604 828
paint mvpdiffc
box 587 847 604 864
paint mvpdiffc
box 506 149 523 326
paint locali
box 587 149 604 326
paint locali
box 506 803 523 872
paint locali
box 587 803 604 872
paint locali

# === Col3 devices ===
box 660 138 768 338
paint mvndiff
box 689 138 739 338
paint mvnmos
box 660 638 768 1038
paint mvpdiff
box 689 638 739 1038
paint mvpmos
box 689 119 739 1057
paint poly
box 658 471 691 504
paint poly
box 658 471 739 504
paint poly
box 666 479 683 496
paint polycont
box 658 479 691 496
paint locali
box 664 157 681 174
paint mvndiffc
box 664 193 681 210
paint mvndiffc
box 664 229 681 246
paint mvndiffc
box 664 265 681 282
paint mvndiffc
box 664 301 681 318
paint mvndiffc
box 745 157 762 174
paint mvndiffc
box 745 193 762 210
paint mvndiffc
box 745 229 762 246
paint mvndiffc
box 745 265 762 282
paint mvndiffc
box 745 301 762 318
paint mvndiffc
box 664 649 681 666
paint mvpdiffc
box 664 685 681 702
paint mvpdiffc
box 664 721 681 738
paint mvpdiffc
box 664 757 681 774
paint mvpdiffc
box 664 793 681 810
paint mvpdiffc
box 664 829 681 846
paint mvpdiffc
box 664 865 681 882
paint mvpdiffc
box 664 901 681 918
paint mvpdiffc
box 664 937 681 954
paint mvpdiffc
box 664 973 681 990
paint mvpdiffc
box 664 1009 681 1026
paint mvpdiffc
box 745 649 762 666
paint mvpdiffc
box 745 685 762 702
paint mvpdiffc
box 745 721 762 738
paint mvpdiffc
box 745 757 762 774
paint mvpdiffc
box 745 793 762 810
paint mvpdiffc
box 745 829 762 846
paint mvpdiffc
box 745 865 762 882
paint mvpdiffc
box 745 901 762 918
paint mvpdiffc
box 745 937 762 954
paint mvpdiffc
box 745 973 762 990
paint mvpdiffc
box 745 1009 762 1026
paint mvpdiffc
box 664 149 681 326
paint locali
box 745 149 762 326
paint locali
box 664 641 681 1034
paint locali
box 745 641 762 1034
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
box 19 1087 36 1104
paint ntapc
box 63 1087 80 1104
paint ntapc
box 15 1075 84 1116
paint ntap
box 19 1079 80 1112
paint locali
box 348 72 365 89
paint mvptapc
box 431 72 448 89
paint mvptapc
box 344 60 452 101
paint mvptap
box 348 64 448 97
paint locali
box 348 1087 365 1104
paint mvntapc
box 431 1087 448 1104
paint mvntapc
box 344 1075 452 1116
paint mvntap
box 348 1079 448 1112
paint locali
box 506 72 523 89
paint mvptapc
box 589 72 606 89
paint mvptapc
box 502 60 610 101
paint mvptap
box 506 64 606 97
paint locali
box 506 1087 523 1104
paint mvntapc
box 589 1087 606 1104
paint mvntapc
box 502 1075 610 1116
paint mvntap
box 506 1079 606 1112
paint locali
box 664 72 681 89
paint mvptapc
box 747 72 764 89
paint mvptapc
box 660 60 768 101
paint mvptap
box 664 64 764 97
paint locali
box 664 1087 681 1104
paint mvntapc
box 747 1087 764 1104
paint mvntapc
box 660 1075 768 1116
paint mvntap
box 664 1079 764 1112
paint locali

# === POWER ===
box 0 0 783 48
paint metal1
box 329 1128 783 1176
paint metal1
box 0 1188 99 1236
paint metal1

# === SRC -> VSS ===
box 19 229 36 246
paint viali
box 14 48 41 252
paint metal1
box 19 72 36 89
paint viali
box 14 48 41 95
paint metal1
box 63 72 80 89
paint viali
box 58 48 85 95
paint metal1
box 348 157 365 174
paint viali
box 348 193 365 210
paint viali
box 348 229 365 246
paint viali
box 348 265 365 282
paint viali
box 348 301 365 318
paint viali
box 343 48 370 324
paint metal1
box 348 72 365 89
paint viali
box 343 48 370 95
paint metal1
box 431 72 448 89
paint viali
box 426 48 453 95
paint metal1
box 506 157 523 174
paint viali
box 506 193 523 210
paint viali
box 506 229 523 246
paint viali
box 506 265 523 282
paint viali
box 506 301 523 318
paint viali
box 501 48 528 324
paint metal1
box 506 72 523 89
paint viali
box 501 48 528 95
paint metal1
box 589 72 606 89
paint viali
box 584 48 611 95
paint metal1
box 664 157 681 174
paint viali
box 664 193 681 210
paint viali
box 664 229 681 246
paint viali
box 664 265 681 282
paint viali
box 664 301 681 318
paint viali
box 659 48 686 324
paint metal1
box 664 72 681 89
paint viali
box 659 48 686 95
paint metal1
box 747 72 764 89
paint viali
box 742 48 769 95
paint metal1

# === SRC -> VDD/VWL ===
box 19 811 36 828
paint viali
box 19 847 36 864
paint viali
box 14 805 41 1188
paint metal1
box 19 1087 36 1104
paint viali
box 14 1081 41 1188
paint metal1
box 63 1087 80 1104
paint viali
box 58 1081 85 1188
paint metal1
box 348 811 365 828
paint viali
box 348 847 365 864
paint viali
box 343 805 370 1128
paint metal1
box 348 1087 365 1104
paint viali
box 343 1081 370 1128
paint metal1
box 431 1087 448 1104
paint viali
box 426 1081 453 1128
paint metal1
box 506 811 523 828
paint viali
box 506 847 523 864
paint viali
box 501 805 528 1128
paint metal1
box 506 1087 523 1104
paint viali
box 501 1081 528 1128
paint metal1
box 589 1087 606 1104
paint viali
box 584 1081 611 1128
paint metal1
box 664 649 681 666
paint viali
box 664 685 681 702
paint viali
box 664 721 681 738
paint viali
box 664 757 681 774
paint viali
box 664 793 681 810
paint viali
box 664 829 681 846
paint viali
box 664 865 681 882
paint viali
box 664 901 681 918
paint viali
box 664 937 681 954
paint viali
box 664 973 681 990
paint viali
box 664 1009 681 1026
paint viali
box 659 643 686 1128
paint metal1
box 664 1087 681 1104
paint viali
box 659 1081 686 1128
paint metal1
box 747 1087 764 1104
paint viali
box 742 1081 769 1128
paint metal1

# === DRAIN MET1 BUSES ===
# Col0 drain met1 bus
box 63 229 80 246
paint viali
box 63 811 80 828
paint viali
box 63 847 80 864
paint viali
box 58 222 85 253
paint metal1
box 58 805 85 870
paint metal1
box 58 222 85 870
paint metal1
# Col1 drain met1 bus
box 429 157 446 174
paint viali
box 429 193 446 210
paint viali
box 429 229 446 246
paint viali
box 429 265 446 282
paint viali
box 429 301 446 318
paint viali
box 429 811 446 828
paint viali
box 429 847 446 864
paint viali
box 424 151 451 324
paint metal1
box 424 805 451 870
paint metal1
box 424 151 451 870
paint metal1
# Col2 drain met1 bus
box 587 157 604 174
paint viali
box 587 193 604 210
paint viali
box 587 229 604 246
paint viali
box 587 265 604 282
paint viali
box 587 301 604 318
paint viali
box 587 811 604 828
paint viali
box 587 847 604 864
paint viali
box 582 151 609 324
paint metal1
box 582 805 609 870
paint metal1
box 582 151 609 870
paint metal1
# Col3 drain met1 bus
box 745 157 762 174
paint viali
box 745 193 762 210
paint viali
box 745 229 762 246
paint viali
box 745 265 762 282
paint viali
box 745 301 762 318
paint viali
box 745 649 762 666
paint viali
box 745 685 762 702
paint viali
box 745 721 762 738
paint viali
box 745 757 762 774
paint viali
box 745 793 762 810
paint viali
box 745 829 762 846
paint viali
box 745 865 762 882
paint viali
box 745 901 762 918
paint viali
box 745 937 762 954
paint viali
box 745 973 762 990
paint viali
box 745 1009 762 1026
paint viali
box 740 151 767 324
paint metal1
box 740 643 767 1032
paint metal1
box 740 151 767 1032
paint metal1

# === GATE MET1 PADS ===
box 20 479 37 496
paint viali
box 14 473 43 502
paint metal1
box 350 362 367 379
paint viali
box 344 356 373 385
paint metal1
box 350 597 367 614
paint viali
box 344 591 373 620
paint metal1
box 508 362 525 379
paint viali
box 502 356 531 385
paint metal1
box 508 597 525 614
paint viali
box 502 591 531 620
paint metal1
box 666 479 683 496
paint viali
box 660 473 689 502
paint metal1

# === GATE ROUTING (met2) ===
# Track Y1: INB
# INB src Col0-drain: via1 on Col0 drain
box 58 417 84 443
paint via1
box 58 414 87 446
paint metal1
box 58 414 87 446
paint metal2
box 58 222 87 870
paint metal1
# INB dst Col2-N: via1 on (2, 'n')
box 502 417 528 443
paint via1
box 502 414 531 446
paint metal1
box 502 414 531 446
paint metal2
box 502 356 531 446
paint metal1
box 52 408 537 452
paint metal2
# Track Y2: IN + Q
# IN src Col0: via1 on (0, 'u')
box 14 475 40 501
paint via1
box 14 472 43 504
paint metal1
box 14 472 43 504
paint metal2
box 14 472 43 504
paint metal1
# IN dst Col1-N: via1 on (1, 'n')
box 344 475 370 501
paint via1
box 344 472 373 504
paint metal1
box 344 472 373 504
paint metal2
box 344 356 373 504
paint metal1
box 8 466 379 510
paint metal2
# Q src Col1-drain: via1 on Col1 drain
box 424 475 450 501
paint via1
box 424 472 453 504
paint metal1
box 424 472 453 504
paint metal2
box 424 151 453 870
paint metal1
# Q mid Col2-P: via1 on (2, 'p')
box 502 475 528 501
paint via1
box 502 472 531 504
paint metal1
box 502 472 531 504
paint metal2
box 502 472 531 620
paint metal1
# Q dst Col3: via1 on (3, 'u')
box 660 475 686 501
paint via1
box 660 472 689 504
paint metal1
box 660 472 689 504
paint metal2
box 660 472 689 504
paint metal1
box 418 466 695 510
paint metal2
# Track Y3: QB
# QB src Col2-drain: via1 on Col2 drain
box 582 533 608 559
paint via1
box 582 530 611 562
paint metal1
box 582 530 611 562
paint metal2
box 582 151 611 870
paint metal1
# QB dst Col1-P: via1 on (1, 'p')
box 344 533 370 559
paint via1
box 344 530 373 562
paint metal1
box 344 530 373 562
paint metal2
box 344 530 373 620
paint metal1
box 338 524 617 568
paint metal2

# === LABELS ===
box 14 473 43 502
label IN s metal1
port make 1
box 740 151 767 1032
label OUT s metal1
port make 2
box 0 1188 99 1236
label VDD s metal1
port make 3
box 329 1128 783 1176
label VWL s metal1
port make 4
box 0 0 783 48
label VSS s metal1
port make 5

# === SAVE ===
save wl_driver
drc on
select top cell
drc check
drc catchup
box 0 0 783 1236
drc count total
flatten wl_driver_flat
load wl_driver_flat
select top cell
extract all
ext2spice lvs
ext2spice
load wl_driver
gds write wl_driver.gds
quit -noprompt