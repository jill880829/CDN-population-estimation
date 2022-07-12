python3 freq_stage1.py $1 $2
Rscript ../CJS_with_heterogeneity.R ch.txt cluster.txt > out.txt
python3 freq_stage2.py $1 $2 $4 > $3
rm ch.txt cluster.txt out.txt