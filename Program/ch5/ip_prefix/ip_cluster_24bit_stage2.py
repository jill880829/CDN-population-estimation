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

def find_prefix(ip):
    cnt = 0
    subnet = ""
    for c in ip:
        if c == '.':
            if cnt == 2:
                return subnet
            else:
                cnt += 1
        subnet += c

streams = db.United_States.find({ "start": { "$lt": "2021-05-17T00:00:00"}, "end": { "$gte": "2021-05-07T00:00:00"}})
ip_list = list()
for s in streams:
    for ip in s["addrPool"]:
        if ip not in ip_list:
            ip_list.append(ip)

# server clustering
ip_prefix_list = []
ip_prefix_dict = {}
ip_prefix_total = {}
for ip in ip_list:
    prefix = find_prefix(ip)
    ip_prefix_dict[ip] = prefix
    if prefix not in ip_prefix_list:
        ip_prefix_list.append(prefix)
        ip_prefix_total[prefix] = [ip]
    else:
        ip_prefix_total[prefix].append(ip)

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
subnet_baseline = []
for i, d in enumerate(date):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T23:59:59" }, "end": { "$gte": "2021-"+d+"T00:00:00" }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T00:00:00" and tm <= "2021-"+d+"T23:59:59":
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    cur_subnet_baseline = [0] * len(ip_prefix_list)
    for ip in cur_ip_list:
        idx = ip_prefix_list.index(find_prefix(ip))
        cur_subnet_baseline[idx] += 1
    subnet_baseline.append(cur_subnet_baseline)
print("baseline for each cluster")
print(ip_prefix_list)
print(subnet_baseline)
subnet_baseline = np.array(subnet_baseline).T

# sampling for each cluster
subnet_sample = []
for i, d in enumerate(date):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T"+argv[2] }, "end": { "$gte": "2021-"+d+"T"+argv[1] }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T"+argv[1] and tm <= "2021-"+d+"T"+argv[2]:
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    cur_subnet_sample = [0] * len(ip_prefix_list)
    for ip in cur_ip_list:
        idx = ip_prefix_list.index(find_prefix(ip))
        cur_subnet_sample[idx] += 1
    subnet_sample.append(cur_subnet_sample)
subnet_sample = np.array(subnet_sample).T

# reading capturing probability
capturing_p = np.zeros((len(ip_prefix_list), len(date)-1),)
cp_before_sort = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
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
            for i in range(len(ip_prefix_list)):
                if s[1] == ip_prefix_list[i]:
                    cp_before_sort[i].append([int(s[2]), float(s[4])])

for i, prefix in enumerate(ip_prefix_list):
    if prefix == "99.181.65" or prefix == "52.223.247" or prefix == "52.223.248":
        continue
    cp_before_sort[i].sort(key = lambda x: x[0])
    for j in range(len(date)-1):
        capturing_p[i, j] = cp_before_sort[i][j][1]

server_estimation = np.zeros((len(date)-1,))
for i, prefix in enumerate(ip_prefix_list):
    print(prefix)
    if prefix == "99.181.65" or prefix == "52.223.247" or prefix == "52.223.248":
        print("not in sample")
    else:
        num_estimation = subnet_sample[i, 1:] / capturing_p[i]
        print("estimation")
        print(num_estimation)
        print("baseline")
        print(subnet_baseline[i])
        ERR = []
        for j, d in enumerate(num_estimation[1:-2]):
            if subnet_baseline[i, j+2] != 0:
                ERR.append(abs( d - subnet_baseline[i, j+2] ) / subnet_baseline[i, j+2])
        ERR = np.array(ERR)
        print("error")
        print(np.mean(ERR))
        print("std")
        print(np.std(ERR))
        server_estimation += num_estimation

print("overall")
print("estimation")
print(server_estimation)
print("overall baseline")
print(server_num_each_day)
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
plt.axis([None, None, 0, 600])
color_idx = np.linspace(0, 1, 4)
plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", label="baseline", alpha=0.7)
plt.plot(x_axis, y_axis1, "o-", markersize=12, linewidth=3, color="r", label="estimation", alpha=0.7)
ax.set_xticks(np.arange(0,10,1))
ax.set_yticks(np.arange(0,600,50))
ax.grid(which="both")
leg = ax.legend(fontsize=20)
ax.tick_params(axis="both", which='major', labelsize=20)
plt.savefig(argv[3]+'24bit_cluster_overall.png')
