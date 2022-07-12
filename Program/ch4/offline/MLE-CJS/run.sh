#!/bin/bash

python3 $1/MLE_CJS_offline_stage1.py $2 $3
Rscript ../../CJS_without_heterogeneity.R tmp.txt > out.txt
python3 $1/MLE_CJS_offline_stage2.py $2 $3 > $4
rm tmp.txt out.txt