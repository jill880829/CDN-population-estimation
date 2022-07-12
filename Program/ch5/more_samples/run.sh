python3 ip_cluster_16bit_stage1.py
Rscript CJS_diff_interval.R ch.txt cluster.txt 1 > out.txt
Rscript CJS_diff_interval.R ch2.txt cluster2.txt 2 > out2.txt
Rscript CJS_diff_interval.R ch3.txt cluster3.txt 3 > out3.txt
Rscript CJS_diff_interval.R ch4.txt cluster4.txt 4 > out4.txt
python3 ip_cluster_16bit_stage2.py $2 > $1
rm ch*.txt cluster*.txt out*.txt