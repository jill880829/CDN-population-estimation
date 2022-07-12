from sys import argv
from pymongo import MongoClient
from pprint import pprint 
import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


client = MongoClient('localhost:25555')
db = client.Twitch
serverStatusResult = db.command('serverStatus')
streams = db.United_States.find({ "start": { "$lt": "2021-05-17T00:00:00"}, "end": { "$gte": "2021-05-07T00:00:00"}})

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

# plotting clustering results
x_axis = scores_pca[:,0]
y_axis = scores_pca[:,1]
plt.figure(figsize=(10, 8))
sns.scatterplot(x = x_axis, y = y_axis, hue = kmeans_pca.labels_, palette = ['c', 'm', 'y'])
plt.title('Clusters by PCA Components')
plt.savefig(argv[3]+'5gp_estimation_cluster.png')

# def ip_prefix(ip):
#     idx = 0
#     for i, c in enumerate(ip):
#         if c == '.':
#             if idx == 2:
#                 return ip[:i]
#             else:
#                 idx += 1

# first_group_cluster = [[],[],[]]
# first_group_ip_prefix = [[],[],[]]
for i, ip in enumerate(first_group_ip):
    if kmeans_pca.labels_[i] == 0:
        ip_group_dict[ip] = "class_4"
    elif kmeans_pca.labels_[i] == 1:
        ip_group_dict[ip] = "class_5"
    elif kmeans_pca.labels_[i] == 2:
        ip_group_dict[ip] = "class_6"
    # first_group_cluster[kmeans_pca.labels_[i]].append([ip, first_group_tran[i]])
    # first_group_ip_prefix[kmeans_pca.labels_[i]].append(ip_prefix(ip))

# sampling and transforming input data format
ip_dict = dict.fromkeys(ip_list, "")
for d in date:
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T"+argv[2] }, "end": { "$gte": "2021-"+d+"T"+argv[1] }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T"+argv[1] and tm <= "2021-"+d+"T"+argv[2]:
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    for ip in ip_list:
        if ip in cur_ip_list:
            ip_dict[ip] += "1"
        else:
            ip_dict[ip] += "0"

ip_and_ch = ip_dict.items()
ip_ch_rec = []
ip_group = []
for (ip, ch) in ip_and_ch:
    if ch == "0"*10:
        continue
    ip_ch_rec.append(ch)
    ip_group.append(ip_group_dict[ip])

with open('ch.txt', 'w') as f:
    for ch in ip_ch_rec:
        f.writelines(ch+'\n')

with open('cluster.txt', 'w') as f:
    for group in ip_group:
        f.writelines(group+'\n')