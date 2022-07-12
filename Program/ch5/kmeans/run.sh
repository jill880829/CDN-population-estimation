python3 kmeans_$1_stage1.py $2 $3 $5
Rscript ../CJS_with_heterogeneity.R ch.txt cluster.txt > out.txt
python3 kmeans_$1_stage2.py $2 $3 $5 > $4
rm ch.txt cluster.txt out.txt