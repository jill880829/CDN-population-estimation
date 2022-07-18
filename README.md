# Estimation on Server Population with MLE-based CMR

## Abstract
The quality and continuity of the video services such as Twitch depend on the scale and well-being of their content distribution networks (CDNs). Due to the growing demand for video services, server numbers in the CDNs have rapidly increased to feed videos to the clients. Given the widespread use of Twitch, we find continuous survey of its CDN an important subject of study. Inspired by Capture-Mark-Recapture(CMR), a methodology widely used to estimate animal population, we developed a system to continuously observe its CDN size (i.e., the number of servers) with lightweight probing. According to our previous research in AINTEC, the Cormack-Jolly-Seber (CJS) model can estimate the CDN size at each sample time with relatively low errors.

Nevertheless, the assumptions of the traditional CJS model are still restrictive. Due to its long converging period, the model can only estimate server population offline. Besides, it assumes that all servers share the same capturing and survival rates, which does not meet the server patterns in Twitch's CDN. Therefore, we introduce the Maximum-Likelihood-Estimation-based (MLE) CJS model with heterogeneity to address these two issues. It not only allows different parameters for each server but also co-estimates all parameters in the CJS probability model. The resulting MLE model is too complicated, and thus we try server clustering to reduce the parameter space. Using a data set collected in May 2021, we find the MLE-based CJS indeed performs better in online estimation. Heterogeneity and server clustering, on the other hand, do not improve the estimation accuracy. For these worse results, we identify the detailed reasons with the estimation results in each group.

This README aims to guide users to set up the environment and run the programs and the scripts. Further information for this study can be found in the Thesis directory.

## Environment Setup
1. Connect to the server with IP "140.112.42.161" through SSH since the 2021 data set is only opened to this server in NSLab.
2. Clone the github repo.
    ```shell=
    git clone https://github.com/jill880829/CDN-population-estimation.git
    ```
3. Build up an virtual environment.
    ```shell=
    cd CDN-population-estimation
    sudo apt install python3-virtualenv
    virtualenv <env_name>
    ```
4. Activate the virtual environment and install required python packages.
    ```shell=
    source <env_name>/bin/activate
    pip install -r requirements.txt
    ```
5. Install Rscript.
    ```shell=
    sudo apt install r-base-core
    ```
6. Install several dependencies first before installing the R package "marked".
    Run these bash command
    ```shell=
    sudo apt install libxml2-dev libcurl4-openssl-dev r-base libssl-dev libfontconfig1-dev
    ```
    and these R commands.
    ```r=
    > packageurl<-"https://cran.r-project.org/src/contrib/Archive/nloptr/nloptr_1.2.1.tar.gz"
    > install.packages(packageurl, repos=NULL, type="source")
    > install.packages("bit64")
    > install.packages("tidyselect")
    ```
7. Install the R package "marked".
    ```r=
    > install.packages("marked")
    ```
   Since the dependencies are installed in the last step, we will get the following result.![](https://i.imgur.com/JdXFilI.png) Now, "marked" has been successfully installed.
8. Install the R package "readr" by running the R command.
    ```r=
    > install.packages("readr")
    ```
    "readr" has been successfully installed.
    ![](https://i.imgur.com/YvOKo29.png)

## Generate Plots in Chapter 3
Note: assume we are in the directory "
CDN-population-estimation" cloned from Github.
### Daily Server Count
```python=
python3 Program/ch3/daily_count.py <dir_path>
```
The plot for daily server count will be stored under the <dir_path>.

### Hourly Server Count
```python=
python3 Program/ch3/hourly_count.py <dir_path>
```
The plot for daily server count will be stored under the <dir_path>.

## Generate Results and Plots in Chapter 4
Note: assume we are in the directory "
CDN-population-estimation" cloned from Github.
### Offline Estimation
Since data sets in 2019 and 2021 are stored in different databases, the programs for accessing these two data sets are different as well. We need to specify the directory path of the program here.

#### Traditional CJS

##### 2019 Data Set
```shell=
cd Program/ch4/offline/traditional_CJS
sudo chmod 774 run.sh
./run.sh data2019 <strat_time> <end_time> <output_file>
```
The estimation results will be stored in <output_file>.
##### 2021 Data Set
```shell=
cd Program/ch4/offline/traditional_CJS
sudo chmod 774 run.sh
./run.sh data2021 <strat_time> <end_time> <output_file>
```
The estimation results will be stored in <output_file>.
#### MLE-based CJS

##### 2019 Data Set
```shell=
cd Program/ch4/offline/MLE-CJS
sudo chmod 774 run.sh
./run.sh data2019 <strat_time> <end_time> <output_file>
```
The estimation results will be stored in <output_file>.
##### 2021 Data Set
```shell=
cd Program/ch4/offline/MLE-CJS
sudo chmod 774 run.sh
./run.sh data2019 <strat_time> <end_time> <output_file>
```
The estimation results will be stored in <output_file>.

With the estimation results in 0-1am, 6-7am, 0-1pm, and 6-7pm, we are able to generate the plots in Result/ch4/offline.
### Real-Time Estimation
```shell=
cd Program/ch4/real_time
sudo chmod 774 run.sh
./run.sh <strat_time> <end_time> <output_file> <fig_dir>
```
The estimation results will be stored in <output_file> and the figure "real_time.png" will be stored in <fig_dir>.
### Delay-One-Day Estimation
```shell=
cd Program/ch4/delay_one_day
sudo chmod 774 run.sh
./run.sh <strat_time> <end_time> <output_file> <fig_dir>
```
The estimation results will be stored in <output_file> and the figure "delay_one_day.png" will be stored in <fig_dir>.
### Converge Period
```shell=
cd Program/ch4/converge_period
sudo chmod 774 run.sh
./run.sh <strat_time> <end_time> <output_file> <fig_dir>
```
The estimation results will be stored in <output_file> and the figure "converge_period.png" will be stored in <fig_dir>.

## Generate Results and Plots in Chapter 5
Note: assume we are in the directory "
CDN-population-estimation" cloned from Github.
### Clustering by Frequency of Occurrence
```shell=
cd Program/ch5/freq
sudo chmod 774 run.sh
./run.sh <strat_time> <end_time> <output_file> <fig_dir>
```
The estimation results will be stored in <output_file> and the figure "converge_period.png" will be stored in <fig_dir>.
### Clustering by IP Prefix
We try 16-bit and 24-bit IP prefixes for clustering in this study. Here, we need to specify the length of IP prefix we use for clustering.
#### 16-bit IP Prefix
```shell=
cd Program/ch5/ip_prefix
sudo chmod 774 run.sh
./run.sh 16bit <strat_time> <end_time> <output_file> <fig_dir>
```
The estimation results will be stored in <output_file> and the figures with prefix "16bit" will be stored in <fig_dir>.
#### 24-bit IP Prefix
```shell=
cd Program/ch5/ip_prefix
sudo chmod 774 run.sh
./run.sh 24bit <strat_time> <end_time> <output_file> <fig_dir>
```
The estimation results will be stored in <output_file> and the figures with prefix "24bit" will be stored in <fig_dir>.

### K-means Clustering
In this study, we try 2 stages of Kmeans clustering. In the first stage, servers are clustered into three groups by transaction numbers in 3 different time periods. In the second stage, one of the server group in the first stage is furthered clustered into 3 subgroups by transaction numbers in different days. Hence, there are 5 server groups in the second stage. Here, we also need to specify which stage of K-means clustering is used for server estimation.
#### Stage 1 (3 Groups)
```shell=
cd Program/ch5/kmeans
sudo chmod 774 run.sh
./run.sh 3gp <strat_time> <end_time> <output_file> <fig_dir>
```
The estimation results will be stored in <output_file> and the figures with prefix "3gp" will be stored in <fig_dir>.
#### Stage 2 (5 Groups)
```shell=
cd Program/ch5/kmeans
sudo chmod 774 run.sh
./run.sh 5gp <strat_time> <end_time> <output_file> <fig_dir>
```
The estimation results will be stored in <output_file> and the figures with prefix "5gp" will be stored in <fig_dir>.

### More Samplings for Estimations with 16-bit IP Prefix Clustering
In this section, the default sampling time is 0-1 am and we try to do more samplings in 5/13. Currently, the sampling time is specified in the python program. Thus, we don't need to specify the sampling time here.
To run the codes:
```shell=
cd Program/ch5/more_samples
sudo chmod 774 run.sh
./run.sh <output_file> <fig_dir>
```
### Computational Overhead of MLE-based CJS Model
The parameter numbers of the MLE-based CJS models and the computation time of "marked" are printed in stderr and stdout respectively. Since the R script is not the last part of the estimation process, we need to run the commands line by line in the run.sh files to acquire these information.
Take the estimation without heterogeneity as an example.
```shell=
cd Program/ch4/offline/MLE-CJS
python3 data2021/MLE_CJS_offline_stage1.py 00:00:00 01:00:00
Rscript ../../CJS_without_heterogeneity.R tmp.txt > out.txt 2> err.txt
```
The parameter numbers of the model is printed in err.txt.
![](https://i.imgur.com/3pIQUTH.png)
The computation time is printed in out.txt.
![](https://i.imgur.com/kAIan7P.png)

Similar operations can be done in the clustering-based estimation with a variety numbers of server groups. With these information, we are able to generate the figure "computation_time" in Result/ch5/discussion.