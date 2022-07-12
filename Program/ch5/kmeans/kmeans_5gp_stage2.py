from sys import argv
from pymongo import MongoClient
from pprint import pprint 
import csv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

client = MongoClient('localhost:25555')
db = client.Twitch
serverStatusResult = db.command('serverStatus')
streams = db.United_States.find({ "start": { "$lt": "2021-05-17T00:00:00"}, "end": { "$gte": "2021-05-07T00:00:00"}})

print("sampling time: "+argv[1]+"-"+argv[2])

ip_list = list()
for s in streams:
    for ip in s["addrPool"]:
        if ip not in ip_list:
            ip_list.append(ip)

# reading server clustering results
ip_group_dict = {}
first_group = []
with open('cluster_result.csv', newline='') as csvfile:
    rows = csv.reader(csvfile)
    for row in rows:
        if row[2] not in ip_list:
            continue
        ip_group_dict[row[2]] = row[1]
        if row[1] == "class_1":
            first_group.append(row[2])

# collecting transaction numbers in each day
date = ["05-07", "05-08", "05-09", "05-10", "05-11", "05-12", "05-13", "05-14", "05-15", "05-16"]
tran_num = {}
for ip in first_group:
    tran_num[ip] = np.zeros((len(date)), dtype=int)

for i, d in enumerate(date):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T23:59:59" }, "end": { "$gte": "2021-"+d+"T00:00:00" }})
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T00:00:00" and tm <= "2021-"+d+"T23:59:59":
                if ip in tran_num:
                    tran_num[ip][i] += 1
first_group_ip = list(tran_num.keys())
first_group_tran = list(tran_num.values())
first_group_tran = np.array(first_group_tran)

scaler = StandardScaler()
segmentation_std = scaler.fit_transform(first_group_tran)
pca = PCA()
pca.fit(segmentation_std)

pca = PCA(n_components = 3)
pca.fit(segmentation_std)
scores_pca = pca.transform(segmentation_std)

kmeans_pca = KMeans(n_clusters = 3, init = 'k-means++', random_state = 42)
kmeans_pca.fit(scores_pca)

for i, ip in enumerate(first_group_ip):
    if kmeans_pca.labels_[i] == 0:
        ip_group_dict[ip] = "class_4"
    elif kmeans_pca.labels_[i] == 1:
        ip_group_dict[ip] = "class_5"
    elif kmeans_pca.labels_[i] == 2:
        ip_group_dict[ip] = "class_6"

# overall baseline
date = ["05-07", "05-08", "05-09", "05-10", "05-11", "05-12", "05-13", "05-14", "05-15", "05-16"]
server_num_each_day = []
for d in date:
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T23:59:59" }, "end": { "$gte": "2021-"+d+"T00:00:00" }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T00:00:00" and tm <= "2021-"+d+"T23:59:59":
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    server_num_each_day.append(len(cur_ip_list))
server_num_each_day = np.array(server_num_each_day)

# baseline for each cluster
baseline_with_cluster = [[], [], [], [], []]
for i, d in enumerate(date):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T23:59:59" }, "end": { "$gte": "2021-"+d+"T00:00:00" }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T00:00:00" and tm <= "2021-"+d+"T23:59:59":
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    c5 = 0
    for ip in cur_ip_list:
        if ip_group_dict[ip] == "class_2":
            c1 += 1
        elif ip_group_dict[ip] == "class_3":
            c2 += 1
        elif ip_group_dict[ip] == "class_4":
            c3 += 1
        elif ip_group_dict[ip] == "class_5":
            c4 += 1
        elif ip_group_dict[ip] == "class_6":
            c5 += 1
    baseline_with_cluster[0].append(c1)
    baseline_with_cluster[1].append(c2)
    baseline_with_cluster[2].append(c3)
    baseline_with_cluster[3].append(c4)
    baseline_with_cluster[4].append(c5)

# sampling for each cluster
sample_with_cluster = [[], [], [], [], []]
for i, d in enumerate(date):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T"+argv[2] }, "end": { "$gte": "2021-"+d+"T"+argv[1] }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T"+argv[1] and tm <= "2021-"+d+"T"+argv[2]:
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    c5 = 0
    for ip in cur_ip_list:
        if ip_group_dict[ip] == "class_2":
            c1 += 1
        elif ip_group_dict[ip] == "class_3":
            c2 += 1
        elif ip_group_dict[ip] == "class_4":
            c3 += 1
        elif ip_group_dict[ip] == "class_5":
            c4 += 1
        elif ip_group_dict[ip] == "class_6":
            c5 += 1
    sample_with_cluster[0].append(c1)
    sample_with_cluster[1].append(c2)
    sample_with_cluster[2].append(c3)
    sample_with_cluster[3].append(c4)
    sample_with_cluster[4].append(c5)

# reading capturing probability
capturing_p = np.zeros((5, len(date)-1),)
cp_before_sort = [[], [], [], [], []]
with open('out.txt', 'r') as f:
    check = 0
    for line in f:
        if check == 0 and line == "$p\n":
            check = 1
        elif check == 1:
            check = 2
        elif check == 2:
            if line == "\n":
                break
            s = line.split()
            if s[1] == 'class_2':
                cp_before_sort[0].append([int(s[2]), float(s[4])])
            elif s[1] == 'class_3':
                cp_before_sort[1].append([int(s[2]), float(s[4])])
            elif s[1] == 'class_4':
                cp_before_sort[2].append([int(s[2]), float(s[4])])
            elif s[1] == 'class_5':
                cp_before_sort[3].append([int(s[2]), float(s[4])])
            elif s[1] == 'class_6':
                cp_before_sort[4].append([int(s[2]), float(s[4])])
for i in range(5):
    cp_before_sort[i].sort(key = lambda x: x[0])
    for j in range(len(date)-1):
        capturing_p[i, j] = cp_before_sort[i][j][1]

# plotting figures
baseline_with_cluster = np.array(baseline_with_cluster)
sample_with_cluster = np.array(sample_with_cluster)
estimation_with_cluster = sample_with_cluster[:, 1:] / capturing_p
print("estimation for each cluster")
print(estimation_with_cluster)
print("baseline for each cluster")
print(baseline_with_cluster)
err = np.abs(estimation_with_cluster[:,1:-2]-baseline_with_cluster[:,2:-2]) / baseline_with_cluster[:,2:-2]
print("error for each cluster")
print(np.mean(err, axis=1))
print("std for each cluster")
print(np.std(err, axis=1))
print("overall estimation")
estimation_sum = np.sum(estimation_with_cluster, axis=0)
print(estimation_sum)
print("overall baseline")
print(server_num_each_day)
print("error")
print(np.mean(np.abs( estimation_sum[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))
print("std")
print(np.std(np.abs( estimation_sum[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))

x_axis = date[1:-1]
y_axis = server_num_each_day[1:-1]
y_axis1 = estimation_sum[:-1]
fig, ax = plt.subplots(figsize=(20, 10))
ax.set_xlabel("Day", fontsize=24)
ax.set_ylabel("Number of Servers", fontsize=24)
plt.axis([None, None, 0, 600])
plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", label="baseline", alpha=0.7)
plt.plot(x_axis, y_axis1, "o-", markersize=12, linewidth=3, color="r", label="MLE-CJS", alpha=0.7)
ax.set_xticks(np.arange(0,10,1))
ax.set_yticks(np.arange(0,600,50))
ax.grid(which="both")
leg = ax.legend(fontsize=20)
ax.tick_params(axis="both", which='major', labelsize=20)
plt.savefig(argv[3]+'5gp_estimation.png')

x_axis = date[1:-1]
y_axis = baseline_with_cluster[2, 1:-1]
y_axis1 = estimation_with_cluster[2, 0:-1]
fig, ax = plt.subplots(figsize=(20, 10))
ax.set_xlabel("Day", fontsize=24)
ax.set_ylabel("Number of Servers: Cyan", fontsize=24)
plt.axis([None, None, 0, 50])
color_idx = np.linspace(0, 1, 4)
plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", label="baseline", alpha=0.7)
plt.plot(x_axis, y_axis1, "o-", markersize=12, linewidth=3, color="c", label="estimation", alpha=0.7)
ax.set_xticks(np.arange(0,10,1))
ax.set_yticks(np.arange(0,50,10))
ax.grid(which="both")
leg = ax.legend(fontsize=20)
ax.tick_params(axis="both", which='major', labelsize=20)
plt.savefig(argv[3]+'5gp_estimation_cyan.png')
x_axis = date[1:-1]
y_axis = baseline_with_cluster[3, 1:-1]
y_axis1 = estimation_with_cluster[3, 0:-1]
fig, ax = plt.subplots(figsize=(20, 10))
ax.set_xlabel("Day", fontsize=24)
ax.set_ylabel("Number of Servers: Magenta", fontsize=24)
plt.axis([None, None, 0, 450])
color_idx = np.linspace(0, 1, 4)
plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", label="baseline", alpha=0.7)
plt.plot(x_axis, y_axis1, "o-", markersize=12, linewidth=3, color="m", label="estimation", alpha=0.7)
ax.set_xticks(np.arange(0,10,1))
ax.set_yticks(np.arange(0,450,50))
ax.grid(which="both")
leg = ax.legend(fontsize=20)
ax.tick_params(axis="both", which='major', labelsize=20)
plt.savefig(argv[3]+'5gp_estimation_magenta.png')
x_axis = date[1:-1]
y_axis = baseline_with_cluster[4, 1:-1]
y_axis1 = estimation_with_cluster[4, 0:-1]
fig, ax = plt.subplots(figsize=(20, 10))
ax.set_xlabel("Day", fontsize=24)
ax.set_ylabel("Number of Servers: Yellow", fontsize=24)
plt.axis([None, None, 0, 80])
color_idx = np.linspace(0, 1, 4)
plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", label="baseline", alpha=0.7)
plt.plot(x_axis, y_axis1, "o-", markersize=12, linewidth=3, color="y", label="estimation", alpha=0.7)
ax.set_xticks(np.arange(0,10,1))
ax.set_yticks(np.arange(0,80,10))
ax.grid(which="both")
leg = ax.legend(fontsize=20)
ax.tick_params(axis="both", which='major', labelsize=20)
plt.savefig(argv[3]+'5gp_estimation_yellow.png')
err = np.abs(estimation_with_cluster[:,1:-2]-baseline_with_cluster[:,2:-2]) / baseline_with_cluster[:,2:-2]
