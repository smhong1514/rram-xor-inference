tech load $env(PDK_ROOT)/sky130B/libs.tech/magic/sky130B.tech
drc style drc(full)
drc off
snap internal
cellname delete sense_amp
edit

# === NWELL ===
box -3 670 360 1054
paint nwell

# === MN3 (ndiff W=2.0) ===
box 15 128 84 328
paint ndiff
box 42 115 57 341
paint poly
box 19 147 36 164
paint ndiffc
box 19 183 36 200
paint ndiffc
box 19 219 36 236
paint ndiffc
box 19 255 36 272
paint ndiffc
box 19 291 36 308
paint ndiffc
box 63 147 80 164
paint ndiffc
box 63 183 80 200
paint ndiffc
box 63 219 80 236
paint ndiffc
box 63 255 80 272
paint ndiffc
box 63 291 80 308
paint ndiffc
box 19 139 36 316
paint locali
box 63 139 80 316
paint locali

# === MN0 (ndiff W=2.0) ===
box 144 128 213 328
paint ndiff
box 171 115 186 341
paint poly
box 148 147 165 164
paint ndiffc
box 148 183 165 200
paint ndiffc
box 148 219 165 236
paint ndiffc
box 148 255 165 272
paint ndiffc
box 148 291 165 308
paint ndiffc
box 192 147 209 164
paint ndiffc
box 192 183 209 200
paint ndiffc
box 192 219 209 236
paint ndiffc
box 192 255 209 272
paint ndiffc
box 192 291 209 308
paint ndiffc
box 148 139 165 316
paint locali
box 192 139 209 316
paint locali

# === MN4 (ndiff W=2.0) ===
box 273 128 342 328
paint ndiff
box 300 115 315 341
paint poly
box 277 147 294 164
paint ndiffc
box 277 183 294 200
paint ndiffc
box 277 219 294 236
paint ndiffc
box 277 255 294 272
paint ndiffc
box 277 291 294 308
paint ndiffc
box 321 147 338 164
paint ndiffc
box 321 183 338 200
paint ndiffc
box 321 219 338 236
paint ndiffc
box 321 255 338 272
paint ndiffc
box 321 291 338 308
paint ndiffc
box 277 139 294 316
paint locali
box 321 139 338 316
paint locali

# === MN1 (ndiff W=1.0) ===
box 15 458 84 558
paint ndiff
box 42 445 57 571
paint poly
box 19 481 36 498
paint ndiffc
box 19 517 36 534
paint ndiffc
box 63 481 80 498
paint ndiffc
box 63 517 80 534
paint ndiffc
box 19 473 36 542
paint locali
box 63 473 80 542
paint locali

# === MN2 (ndiff W=1.0) ===
box 273 458 342 558
paint ndiff
box 300 445 315 571
paint poly
box 277 481 294 498
paint ndiffc
box 277 517 294 534
paint ndiffc
box 321 481 338 498
paint ndiffc
box 321 517 338 534
paint ndiffc
box 277 473 294 542
paint locali
box 321 473 338 542
paint locali

# === MP1 (pdiff W=1.0) ===
box 15 688 84 788
paint pdiff
box 42 675 57 801
paint poly
box 19 711 36 728
paint pdiffc
box 19 747 36 764
paint pdiffc
box 63 711 80 728
paint pdiffc
box 63 747 80 764
paint pdiffc
box 19 703 36 772
paint locali
box 63 703 80 772
paint locali

# === MP2 (pdiff W=1.0) ===
box 273 688 342 788
paint pdiff
box 300 675 315 801
paint poly
box 277 711 294 728
paint pdiffc
box 277 747 294 764
paint pdiffc
box 321 711 338 728
paint pdiffc
box 321 747 338 764
paint pdiffc
box 277 703 294 772
paint locali
box 321 703 338 772
paint locali

# === MP3 (pdiff W=0.5) ===
box 15 918 84 968
paint pdiff
box 42 905 57 981
paint poly
box 19 934 36 951
paint pdiffc
box 63 934 80 951
paint pdiffc
box 19 926 36 959
paint locali
box 63 926 80 959
paint locali

# === MP5 (pdiff W=0.5) ===
box 144 918 213 968
paint pdiff
box 171 905 186 981
paint poly
box 148 934 165 951
paint pdiffc
box 192 934 209 951
paint pdiffc
box 148 926 165 959
paint locali
box 192 926 209 959
paint locali

# === MP4 (pdiff W=0.5) ===
box 273 918 342 968
paint pdiff
box 300 905 315 981
paint poly
box 277 934 294 951
paint pdiffc
box 321 934 338 951
paint pdiffc
box 277 926 294 959
paint locali
box 321 926 338 959
paint locali

# === CONTINUOUS GATE POLY (MN1-MP1, MN2-MP2) ===
box 42 571 57 675
paint poly
box 300 571 315 675
paint poly

# === TAPS ===
box 19 72 36 89
paint ptapc
box 63 72 80 89
paint ptapc
box 15 60 84 101
paint ptap
box 19 64 80 97
paint locali
box 19 1007 36 1024
paint ntapc
box 63 1007 80 1024
paint ntapc
box 15 995 84 1036
paint ntap
box 19 999 80 1032
paint locali
box 148 72 165 89
paint ptapc
box 192 72 209 89
paint ptapc
box 144 60 213 101
paint ptap
box 148 64 209 97
paint locali
box 148 1007 165 1024
paint ntapc
box 192 1007 209 1024
paint ntapc
box 144 995 213 1036
paint ntap
box 148 999 209 1032
paint locali
box 277 72 294 89
paint ptapc
box 321 72 338 89
paint ptapc
box 273 60 342 101
paint ptap
box 277 64 338 97
paint locali
box 277 1007 294 1024
paint ntapc
box 321 1007 338 1024
paint ntapc
box 273 995 342 1036
paint ntap
box 277 999 338 1032
paint locali

# === POWER RAILS ===
box 0 0 357 48
paint metal1
box 0 1048 357 1096
paint metal1

# === VSS ===
box 148 147 165 164
paint viali
box 148 183 165 200
paint viali
box 148 219 165 236
paint viali
box 148 255 165 272
paint viali
box 148 291 165 308
paint viali
box 143 141 170 314
paint metal1
box 143 48 166 141
paint metal1
box 19 72 36 89
paint viali
box 14 48 41 95
paint metal1
box 63 72 80 89
paint viali
box 58 48 85 95
paint metal1
box 148 72 165 89
paint viali
box 143 48 170 95
paint metal1
box 192 72 209 89
paint viali
box 187 48 214 95
paint metal1
box 277 72 294 89
paint viali
box 272 48 299 95
paint metal1
box 321 72 338 89
paint viali
box 316 48 343 95
paint metal1

# === VDD ===
box 19 1007 36 1024
paint viali
box 14 1001 41 1048
paint metal1
box 63 1007 80 1024
paint viali
box 58 1001 85 1048
paint metal1
box 148 1007 165 1024
paint viali
box 143 1001 170 1048
paint metal1
box 192 1007 209 1024
paint viali
box 187 1001 214 1048
paint metal1
box 277 1007 294 1024
paint viali
box 272 1001 299 1048
paint metal1
box 321 1007 338 1024
paint viali
box 316 1001 343 1048
paint metal1
box 19 934 36 951
paint viali
box 14 927 41 958
paint metal1
box 14 958 41 1048
paint metal1
box 277 934 294 951
paint viali
box 272 927 299 958
paint metal1
box 272 958 299 1048
paint metal1
box 19 711 36 728
paint viali
box 19 747 36 764
paint viali
box 14 705 41 770
paint metal1
box 14 770 41 811
paint metal1
box 0 797 41 811
paint metal1
box 0 797 14 866
paint metal1
box 0 866 41 880
paint metal1
box 14 866 41 1048
paint metal1
box 277 711 294 728
paint viali
box 277 747 294 764
paint viali
box 272 705 299 770
paint metal1
box 272 770 299 811
paint metal1
box 272 797 357 811
paint metal1
box 343 797 357 866
paint metal1
box 272 866 357 880
paint metal1
box 272 866 299 1048
paint metal1

# === FN1 (met2 true L-shape) ===
box 63 147 80 164
paint viali
box 63 183 80 200
paint viali
box 63 219 80 236
paint viali
box 63 255 80 272
paint viali
box 63 291 80 308
paint viali
box 58 141 85 314
paint metal1
box 19 481 36 498
paint viali
box 19 517 36 534
paint viali
box 14 475 41 540
paint metal1
box 57 287 83 313
paint via1
box 57 284 83 316
paint metal1
box 57 284 83 316
paint metal2
box 13 475 39 501
paint via1
box 13 472 39 504
paint metal1
box 13 472 39 504
paint metal2
box 13 287 84 314
paint metal2
box 13 287 40 502
paint metal2

# === FN2 (met2 true L-shape) ===
box 321 147 338 164
paint viali
box 321 183 338 200
paint viali
box 321 219 338 236
paint viali
box 321 255 338 272
paint viali
box 321 291 338 308
paint viali
box 316 141 343 314
paint metal1
box 277 481 294 498
paint viali
box 277 517 294 534
paint viali
box 272 475 299 540
paint metal1
box 315 287 341 313
paint via1
box 315 284 341 316
paint metal1
box 315 284 341 316
paint metal2
box 271 475 297 501
paint via1
box 271 472 297 504
paint metal1
box 271 472 297 504
paint metal2
box 271 287 342 314
paint metal2
box 271 287 298 502
paint metal2

# === TAIL ===
box 19 147 36 164
paint viali
box 19 183 36 200
paint viali
box 19 219 36 236
paint viali
box 19 255 36 272
paint viali
box 19 291 36 308
paint viali
box 192 147 209 164
paint viali
box 192 183 209 200
paint viali
box 192 219 209 236
paint viali
box 192 255 209 272
paint viali
box 192 291 209 308
paint viali
box 277 147 294 164
paint viali
box 277 183 294 200
paint viali
box 277 219 294 236
paint viali
box 277 255 294 272
paint viali
box 277 291 294 308
paint viali
box 14 141 41 314
paint metal1
box 187 141 214 314
paint metal1
box 272 141 299 314
paint metal1
box 13 141 39 167
paint via1
box 13 138 39 170
paint metal1
box 13 138 39 170
paint metal2
box 186 141 212 167
paint via1
box 186 138 212 170
paint metal1
box 186 138 212 170
paint metal2
box 271 141 297 167
paint via1
box 271 138 297 170
paint metal1
box 271 138 297 170
paint metal2
box 13 141 298 168
paint metal2

# === Q NET ===
box 63 481 80 498
paint viali
box 63 517 80 534
paint viali
box 58 475 85 540
paint metal1
box 63 711 80 728
paint viali
box 63 747 80 764
paint viali
box 58 705 85 770
paint metal1
box 63 934 80 951
paint viali
box 58 927 85 958
paint metal1
box 148 934 165 951
paint viali
box 143 927 170 958
paint metal1
box 58 475 85 540
paint metal1
box 57 475 83 501
paint via1
box 57 472 83 504
paint metal1
box 57 472 83 504
paint metal2
box 58 705 85 770
paint metal1
box 57 705 83 731
paint via1
box 57 702 83 734
paint metal1
box 57 702 83 734
paint metal2
box 58 927 85 958
paint metal1
box 57 927 83 953
paint via1
box 57 924 83 956
paint metal1
box 57 924 83 956
paint metal2
box 143 927 170 958
paint metal1
box 142 927 168 953
paint via1
box 142 924 168 956
paint metal1
box 142 924 168 956
paint metal2
box 57 475 84 954
paint metal2
box 57 927 169 954
paint metal2

# === QB NET ===
box 321 481 338 498
paint viali
box 321 517 338 534
paint viali
box 316 475 343 540
paint metal1
box 321 711 338 728
paint viali
box 321 747 338 764
paint viali
box 316 705 343 770
paint metal1
box 321 934 338 951
paint viali
box 316 927 343 958
paint metal1
box 192 934 209 951
paint viali
box 187 927 214 958
paint metal1
box 316 475 343 540
paint metal1
box 315 475 341 501
paint via1
box 315 472 341 504
paint metal1
box 315 472 341 504
paint metal2
box 316 705 343 770
paint metal1
box 315 705 341 731
paint via1
box 315 702 341 734
paint metal1
box 315 702 341 734
paint metal2
box 316 927 343 958
paint metal1
box 315 927 341 953
paint via1
box 315 924 341 956
paint metal1
box 315 924 341 956
paint metal2
box 187 927 214 958
paint metal1
box 186 927 212 953
paint via1
box 186 924 212 956
paint metal1
box 186 924 212 956
paint metal2
box 315 475 342 954
paint metal2
box 186 927 342 954
paint metal2

# === CROSS-COUPLING ===
box 42 445 57 442
paint poly
box 33 409 66 442
paint poly
box 41 417 58 434
paint polycont
box 33 417 66 434
paint locali
box 41 417 58 434
paint viali
box 300 445 315 442
paint poly
box 291 409 324 442
paint poly
box 299 417 316 434
paint polycont
box 291 417 324 434
paint locali
box 299 417 316 434
paint viali
box 42 574 57 801
paint poly
box 33 574 66 607
paint poly
box 41 582 58 599
paint polycont
box 33 582 66 599
paint locali
box 41 582 58 599
paint viali
box 300 574 315 801
paint poly
box 291 574 324 607
paint poly
box 299 582 316 599
paint polycont
box 291 582 324 599
paint locali
box 299 582 316 599
paint viali
# Q cross-coupling: met2 stub + met1 horizontal in Gap0 upper
box 94 412 120 438
paint via1
box 94 409 120 441
paint metal1
box 94 409 120 441
paint metal2
box 57 409 121 441
paint metal2
box 57 409 84 954
paint metal2
box 294 410 321 441
paint metal1
box 94 410 321 441
paint metal1
# QB cross-coupling: met2 stub + met1 horizontal in Gap1 lower
box 252 577 278 603
paint via1
box 252 574 278 606
paint metal1
box 252 574 278 606
paint metal2
box 252 574 342 606
paint metal2
box 315 574 342 954
paint metal2
box 36 575 63 606
paint metal1
box 36 575 279 606
paint metal1
box 36 410 63 441
paint metal1
box 294 575 321 606
paint metal1

# === SAE ===
box 42 822 57 981
paint poly
box 33 822 66 855
paint poly
box 41 830 58 847
paint polycont
box 33 830 66 847
paint locali
box 41 830 58 847
paint viali
box 171 822 186 981
paint poly
box 162 822 195 855
paint poly
box 170 830 187 847
paint polycont
box 162 830 195 847
paint locali
box 170 830 187 847
paint viali
box 300 822 315 981
paint poly
box 291 822 324 855
paint poly
box 299 830 316 847
paint polycont
box 291 830 324 847
paint locali
box 299 830 316 847
paint viali
box 35 825 322 852
paint metal1
box 171 115 186 377
paint poly
box 162 344 195 377
paint poly
box 170 352 187 369
paint polycont
box 162 352 195 369
paint locali
box 170 352 187 369
paint viali
box 165 345 192 376
paint metal1
box 164 825 190 851
paint via1
box 164 822 190 854
paint metal1
box 164 822 190 854
paint metal2
box 164 349 190 375
paint via1
box 164 346 190 378
paint metal1
box 164 346 190 378
paint metal2
box 164 349 191 852
paint metal2

# === INP ===
box 42 115 57 377
paint poly
box 33 344 66 377
paint poly
box 41 352 58 369
paint polycont
box 33 352 66 369
paint locali
box 41 352 58 369
paint viali
box 35 346 64 375
paint metal1

# === INN ===
box 300 115 315 377
paint poly
box 291 344 324 377
paint poly
box 299 352 316 369
paint polycont
box 291 352 324 369
paint locali
box 299 352 316 369
paint viali
box 293 346 322 375
paint metal1

# === LABELS & PORTS ===
box 35 825 322 852
label SAE s metal1
port make 1
box 35 346 64 375
label INP s metal1
port make 2
box 293 346 322 375
label INN s metal1
port make 3
box 57 475 84 954
label Q s metal2
port make 4
box 315 475 342 954
label QB s metal2
port make 5
box 0 1048 357 1096
label VDD s metal1
port make 6
box 0 0 357 48
label VSS s metal1
port make 7

# === SAVE + DRC + EXTRACT ===
save sense_amp
drc on
drc check
drc catchup
select top cell
drc why
drc count
extract all
ext2spice lvs
ext2spice
gds write sense_amp.gds
quit -noprompt