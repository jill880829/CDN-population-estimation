from sys import argv
from pymongo import MongoClient
from pprint import pprint 
import csv
import numpy as np
import matplotlib.pyplot as plt

client = MongoClient('localhost:25555')
db = client.Twitch
serverStatusResult = db.command('serverStatus')

print("sampling time: "+argv[1]+"-"+argv[2])

streams = db.United_States.find({ "start": { "$lt": "2021-05-17T00:00:00"}, "end": { "$gte": "2021-05-07T00:00:00"}})
ip_list = list()
for s in streams:
    for ip in s["addrPool"]:
        if ip not in ip_list:
            ip_list.append(ip)
            
# transforming input data format for clustering
date = ["05-07", "05-08", "05-09", "05-10", "05-11", "05-12", "05-13", "05-14", "05-15", "05-16"]
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

# server clustering based on frequency of occurrence
ip_and_ch = ip_dict.items()
ip_ch_rec = []
ip_freq_table = {}
for (ip, ch) in ip_and_ch:
    if ch == "0"*10:
        continue
    ip_ch_rec.append(ch)
    cnt = 0
    for c in ch:
        if c == "1":
            cnt += 1
    if cnt >= 5:
        ip_freq_table[ip] = "high"
    elif cnt >= 2:
        ip_freq_table[ip] = "mid"
    else:
        ip_freq_table[ip] = "low"

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
print("overall baseline")
print(server_num_each_day)

# baseline for each cluster
server_group = ["high", "mid", "low"]
cluster_baseline = [[0] * len(date), [0] * len(date), [0] * len(date)]
for i, d in enumerate(date):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T23:59:59" }, "end": { "$gte": "2021-"+d+"T00:00:00" }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T00:00:00" and tm <= "2021-"+d+"T23:59:59":
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    for ip in cur_ip_list:
        if ip not in ip_freq_table:
            cluster_baseline[2][i] += 1
        elif ip_freq_table[ip] == "high":
            cluster_baseline[0][i] += 1
        elif ip_freq_table[ip] == "mid":
            cluster_baseline[1][i] += 1
        else:
            cluster_baseline[2][i] += 1
print("baseline for each cluster")
print(server_group)
print(cluster_baseline)
cluster_baseline = np.array(cluster_baseline)

# sampling for each cluster
cluster_sample = [[0] * len(date), [0] * len(date), [0] * len(date)]
for i, d in enumerate(date):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T"+argv[2] }, "end": { "$gte": "2021-"+d+"T"+argv[1] }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T"+argv[1] and tm <= "2021-"+d+"T"+argv[2]:
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    for ip in cur_ip_list:
        if ip_freq_table[ip] == "high":
            cluster_sample[0][i] += 1
        elif ip_freq_table[ip] == "mid":
            cluster_sample[1][i] += 1
        else:
            cluster_sample[2][i] += 1
cluster_sample = np.array(cluster_sample)

# reading capturing probability
capturing_p = np.zeros((3, len(date)-1),)
cp_before_sort = [[], [], []]
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
            if s[1] == "high":
                cp_before_sort[0].append([int(s[2]), float(s[4])])
            elif s[1] == "mid":
                cp_before_sort[1].append([int(s[2]), float(s[4])])
            elif s[1] == "low":
                cp_before_sort[2].append([int(s[2]), float(s[4])])
for i in range(3):
    cp_before_sort[i].sort(key = lambda x: x[0])
    for j in range(len(date)-1):
        capturing_p[i, j] = cp_before_sort[i][j][1]

# server population estimation for each cluster
server_estimation = np.zeros((len(date)-1,))
for i in range(3):
    print(server_group[i])
    num_estimation = cluster_sample[i, 1:] / capturing_p[i]
    err = np.mean(np.abs( num_estimation[1:-2] - cluster_baseline[i,2:-2] ) / cluster_baseline[i,2:-2])
    print("estimation")
    print(num_estimation)
    print("error")
    print(err)
    print("std")
    print(np.std(np.abs( num_estimation[1:-2] - cluster_baseline[i,2:-2] ) / cluster_baseline[i,2:-2]))
    server_estimation += num_estimation
    x_axis = date[1:-1]
    y_axis = cluster_baseline[i, 1:-1]
    y_axis1 = num_estimation[0:-1]
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.set_xlabel("Day", fontsize=24)
    if i == 0:
        plt.axis([None, None, 0, 600])
        ax.set_ylabel("Number of Servers: High Freq", fontsize=24)
    elif i == 1:
        plt.axis([None, None, 0, 40])
        ax.set_ylabel("Number of Servers: Mid Freq", fontsize=24)
    else:
        plt.axis([None, None, 0, 3000])
        ax.set_ylabel("Number of Servers: Low Freq", fontsize=24)
    color_idx = np.linspace(0, 1, 4)
    plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", label="baseline", alpha=0.7)
    plt.plot(x_axis, y_axis1, "o-", markersize=12, linewidth=3, color="r", label="estimation", alpha=0.7)
    ax.set_xticks(np.arange(0,10,1))
    if i == 0:
        ax.set_yticks(np.arange(0,600,100))
    elif i == 1:
        ax.set_yticks(np.arange(0,40,5))
    else:
        ax.set_yticks(np.arange(0,3000,500))
    ax.grid(which="both")
    leg = ax.legend(fontsize=20)
    ax.tick_params(axis="both", which='major', labelsize=20)
    plt.savefig(argv[3]+'freq_cluster'+str(i)+'.png')

print("overall")
print("estimation")
print(server_estimation)
err = np.mean(np.abs( server_estimation[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2])
print("error")
print(err)
print("std")
print(np.std(np.abs( server_estimation[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))
x_axis = date[1:-1]
y_axis = server_num_each_day[1:-1]
y_axis1 = server_estimation[0:-1]
fig, ax = plt.subplots(figsize=(20, 10))
ax.set_xlabel("Day", fontsize=24)
ax.set_ylabel("Number of Servers", fontsize=24)
plt.axis([None, None, 0, 3500])
color_idx = np.linspace(0, 1, 4)
plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", label="baseline", alpha=0.7)
plt.plot(x_axis, y_axis1, "o-", markersize=12, linewidth=3, color="r", label="estimation", alpha=0.7)
ax.set_xticks(np.arange(0,10,1))
ax.set_yticks(np.arange(0,3500,500))
ax.grid(which="both")
leg = ax.legend(fontsize=20)
ax.tick_params(axis="both", which='major', labelsize=20)
plt.savefig(argv[3]+'freq_cluster_overall.png')
