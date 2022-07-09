python3 MLE_CJS_stage1.py $1 $2
for i in {3..10}
do
    Rscript ../CJS_without_heterogeneity.R tmp"$i".txt > out"$i".txt
done
python3 converge_period.py $1 $2 $4 > $3
rm tmp*.txt out*.txt