from sys import argv
from pymongo import MongoClient
from pprint import pprint 
import csv
import numpy as np
import matplotlib.pyplot as plt

client = MongoClient('localhost:25555')
db = client.Twitch
serverStatusResult = db.command('serverStatus')
streams = db.United_States.find({ "start": { "$lt": "2021-05-17T00:00:00"}, "end": { "$gte": "2021-05-07T00:00:00"}})

def find_prefix(ip):
    cnt = 0
    subnet = ""
    for c in ip:
        if c == '.':
            if cnt == 1:
                return subnet
            else:
                cnt += 1
        subnet += c

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

# baseline for each group
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
subnet_baseline = np.array(subnet_baseline).T

# sampling for each group (including 1/2/3/4 samples in 5/13)
subnet_sample = []
new_subnet_sample_2 = []
new_subnet_sample_3 = []
new_subnet_sample_4 = []
for i, d in enumerate(date):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T01:00:00" }, "end": { "$gte": "2021-"+d+"T00:00:00" }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T00:00:00" and tm <= "2021-"+d+"T01:00:00":
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    cur_subnet_sample = [0] * len(ip_prefix_list)
    for ip in cur_ip_list:
        idx = ip_prefix_list.index(find_prefix(ip))
        cur_subnet_sample[idx] += 1
    subnet_sample.append(cur_subnet_sample)
    new_subnet_sample_2.append(cur_subnet_sample)
    new_subnet_sample_3.append(cur_subnet_sample)
    new_subnet_sample_4.append(cur_subnet_sample)
    if d == "05-13":
        streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T07:00:00" }, "end": { "$gte": "2021-"+d+"T06:00:00" }})
        cur_ip_list = list()
        for s in streams:
            for (tm, ip) in s["transactionList"].items():
                if tm >= "2021-"+d+"T08:00:00" and tm <= "2021-"+d+"T09:00:00":
                    if ip not in cur_ip_list:
                        cur_ip_list.append(ip)
        cur_subnet_sample = [0] * len(ip_prefix_list)
        for ip in cur_ip_list:
            idx = ip_prefix_list.index(find_prefix(ip))
            cur_subnet_sample[idx] += 1
        new_subnet_sample_4.append(cur_subnet_sample)
        streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T09:00:00" }, "end": { "$gte": "2021-"+d+"T08:00:00" }})
        cur_ip_list = list()
        for s in streams:
            for (tm, ip) in s["transactionList"].items():
                if tm >= "2021-"+d+"T08:00:00" and tm <= "2021-"+d+"T09:00:00":
                    if ip not in cur_ip_list:
                        cur_ip_list.append(ip)
        cur_subnet_sample = [0] * len(ip_prefix_list)
        for ip in cur_ip_list:
            idx = ip_prefix_list.index(find_prefix(ip))
            cur_subnet_sample[idx] += 1
        new_subnet_sample_3.append(cur_subnet_sample)
        streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T13:00:00" }, "end": { "$gte": "2021-"+d+"T12:00:00" }})
        cur_ip_list = list()
        for s in streams:
            for (tm, ip) in s["transactionList"].items():
                if tm >= "2021-"+d+"T12:00:00" and tm <= "2021-"+d+"T13:00:00":
                    if ip not in cur_ip_list:
                        cur_ip_list.append(ip)
        cur_subnet_sample = [0] * len(ip_prefix_list)
        for ip in cur_ip_list:
            idx = ip_prefix_list.index(find_prefix(ip))
            cur_subnet_sample[idx] += 1
        new_subnet_sample_2.append(cur_subnet_sample)
        new_subnet_sample_4.append(cur_subnet_sample)
        streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T17:00:00" }, "end": { "$gte": "2021-"+d+"T16:00:00" }})
        cur_ip_list = list()
        for s in streams:
            for (tm, ip) in s["transactionList"].items():
                if tm >= "2021-"+d+"T16:00:00" and tm <= "2021-"+d+"T17:00:00":
                    if ip not in cur_ip_list:
                        cur_ip_list.append(ip)
        cur_subnet_sample = [0] * len(ip_prefix_list)
        for ip in cur_ip_list:
            idx = ip_prefix_list.index(find_prefix(ip))
            cur_subnet_sample[idx] += 1
        new_subnet_sample_3.append(cur_subnet_sample)
        streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T19:00:00" }, "end": { "$gte": "2021-"+d+"T18:00:00" }})
        cur_ip_list = list()
        for s in streams:
            for (tm, ip) in s["transactionList"].items():
                if tm >= "2021-"+d+"T16:00:00" and tm <= "2021-"+d+"T17:00:00":
                    if ip not in cur_ip_list:
                        cur_ip_list.append(ip)
        cur_subnet_sample = [0] * len(ip_prefix_list)
        for ip in cur_ip_list:
            idx = ip_prefix_list.index(find_prefix(ip))
            cur_subnet_sample[idx] += 1
        new_subnet_sample_4.append(cur_subnet_sample)

subnet_sample = np.array(subnet_sample).T
new_subnet_sample_2 = np.array(new_subnet_sample_2).T
new_subnet_sample_3 = np.array(new_subnet_sample_3).T
new_subnet_sample_4 = np.array(new_subnet_sample_4).T

# reading capturing probability
prob = np.zeros((3, len(date)-1),)
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
            if s[1] == ip_prefix_list[0]:
                cp_before_sort[0].append([int(s[2]), float(s[4])])
            elif s[1] == ip_prefix_list[1]:
                cp_before_sort[1].append([int(s[2]), float(s[4])])
            elif s[1] == ip_prefix_list[2]:
                cp_before_sort[2].append([int(s[2]), float(s[4])])
for i in range(3):
    cp_before_sort[i].sort(key = lambda x: x[0])
    for j in range(len(date)-1):
        prob[i, j] = cp_before_sort[i][j][1]

new_prob = [np.zeros((len(date)),), np.zeros((len(date)+1),), np.zeros((len(date)+2),)]
for ite in range(3):
    cp_before_sort = [[], [], []]
    with open('out'+str(ite+2)+'.txt', 'r') as f:
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
                if s[1] == ip_prefix_list[0]:
                    cp_before_sort[0].append([int(s[2]), float(s[4])])
                elif s[1] == ip_prefix_list[1]:
                    cp_before_sort[1].append([int(s[2]), float(s[4])])
                elif s[1] == ip_prefix_list[2]:
                    cp_before_sort[2].append([int(s[2]), float(s[4])])
    for i in range(3):
        if ip_prefix_list[i] == "99.181":
            cp_before_sort[i].sort(key = lambda x: x[0])
            for j in range(len(date)+ite):
                new_prob[ite][j] = cp_before_sort[i][j][1]

server_estimation = np.zeros((prob.shape[1],))
new_server_estimation_2 = np.zeros((prob.shape[1],))
new_server_estimation_3 = np.zeros((prob.shape[1],))
new_server_estimation_4 = np.zeros((prob.shape[1],))
for i, prefix in enumerate(ip_prefix_list):
    print(prefix)
    num_estimation = subnet_sample[i, 1:]/prob[i]
    print("estimation")
    print(num_estimation)
    print("baseline")
    print(subnet_baseline[i])
    ERR = []
    for j, d in enumerate(num_estimation[1:-2]):
        if subnet_baseline[i, j+2] != 0:
            ERR.append(abs( d - subnet_baseline[i, j+2] ) / subnet_baseline[i, j+2])
    ERR = np.abs((num_estimation[1:-2]-subnet_baseline[i,2:-2])/subnet_baseline[i,2:-2])
    print("error")
    print(np.mean(ERR))
    print("std")
    print(np.std(ERR))
    server_estimation += num_estimation
    new_server_estimation_2 += num_estimation
    new_server_estimation_3 += num_estimation
    new_server_estimation_4 += num_estimation
    if prefix == "99.181":
        print("sampling twice")
        new_num_esti = new_subnet_sample_2[i, 1:]/new_prob[0]
        y_axis2 = np.zeros((len(num_estimation),))
        y_axis2[:5] = new_num_esti[:5]
        y_axis2[5:] = new_num_esti[6:]
        print("estimation")
        print(y_axis2)
        print("error")
        print(np.mean(np.abs( y_axis2[1:-2] - subnet_baseline[i, 2:-2] ) / subnet_baseline[i, 2:-2]))
        print("std")
        print(np.std(np.abs( y_axis2[1:-2] - subnet_baseline[i, 2:-2] ) / subnet_baseline[i, 2:-2]))
        new_server_estimation_2 -= num_estimation
        new_server_estimation_2 += y_axis2
        print("sampling three times")
        new_num_esti = new_subnet_sample_3[i, 1:]/new_prob[1]
        y_axis3 = np.zeros((len(num_estimation),))
        y_axis3[:5] = new_num_esti[:5]
        y_axis3[5] = np.mean(new_num_esti[6:8])
        y_axis3[6:] = new_num_esti[8:]
        print("estimation")
        print(y_axis3)
        print("error")
        print(np.mean(np.abs( y_axis3[1:-2] - subnet_baseline[i, 2:-2] ) / subnet_baseline[i, 2:-2]))
        print("std")
        print(np.std(np.abs( y_axis3[1:-2] - subnet_baseline[i, 2:-2] ) / subnet_baseline[i, 2:-2]))
        new_server_estimation_3 -= num_estimation
        new_server_estimation_3 += y_axis3
        print("sampling four times")
        new_num_esti = new_subnet_sample_4[i, 1:]/new_prob[2]
        y_axis4 = np.zeros((len(num_estimation),))
        y_axis4[:5] = new_num_esti[:5]
        y_axis4[5] = np.mean(new_num_esti[6:9])
        y_axis4[6:] = new_num_esti[9:]
        print("estimation")
        print(y_axis4)
        print("error")
        print(np.mean(np.abs( y_axis4[1:-2] - subnet_baseline[i, 2:-2] ) / subnet_baseline[i, 2:-2]))
        print("std")
        print(np.std(np.abs( y_axis4[1:-2] - subnet_baseline[i, 2:-2] ) / subnet_baseline[i, 2:-2]))
        new_server_estimation_4 -= num_estimation
        new_server_estimation_4 += y_axis4
        # plotting figure
        x_axis = date[1:-1]
        y_axis = subnet_baseline[i, 1:-1]
        y_axis1 = num_estimation[0:-1]
        fig, ax = plt.subplots(figsize=(20, 10))
        ax.set_xlabel("Day", fontsize=24)
        ax.set_ylabel("Number of Servers"+prefix, fontsize=24)
        plt.axis([None, None, 0, 140])
        color_idx = np.linspace(0, 1, 4)
        plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", label="baseline", alpha=0.7)
        plt.plot(x_axis, y_axis1, "o-", markersize=12, linewidth=3, color=plt.cm.winter(color_idx[0]), label="1 sample in 5/13", alpha=0.7)
        plt.plot(x_axis, y_axis2[:-1], "o-", markersize=12, linewidth=3, color=plt.cm.winter(color_idx[1]), label="2 samples in 5/13", alpha=0.7)
        plt.plot(x_axis, y_axis3[:-1], "o-", markersize=12, linewidth=3, color=plt.cm.winter(color_idx[2]), label="3 samples in 5/13", alpha=0.7)
        plt.plot(x_axis, y_axis4[:-1], "o-", markersize=12, linewidth=3, color=plt.cm.winter(color_idx[3]), label="4 samples in 5/13", alpha=0.7)
        ax.set_xticks(np.arange(0,10,1))
        ax.set_yticks(np.arange(0,140,20))
        ax.grid(which="both")
        leg = ax.legend(fontsize=20)
        ax.tick_params(axis="both", which='major', labelsize=20)
        plt.savefig(argv[1]+'16bit_Diff_Samples_in_group.png')

print("overall estimation")
print(server_estimation)
print("overall baseline")
print(server_num_each_day)
err = np.mean(np.abs( server_estimation[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2])
print("error")
print(err)
print("std")
print(np.std(np.abs( server_estimation[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))
print("sampling twice")
print("estimation")
print(new_server_estimation_2)
print("error")
print(np.mean(np.abs( new_server_estimation_2[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))
print("std")
print(np.std(np.abs( new_server_estimation_2[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))
print("sampling three times")
print("estimation")
print(new_server_estimation_3)
print("error")
print(np.mean(np.abs( new_server_estimation_3[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))
print("std")
print(np.std(np.abs( new_server_estimation_3[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))
print("sampling four times")
print("estimation")
print(new_server_estimation_4)
print("error")
print(np.mean(np.abs( new_server_estimation_4[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))
print("std")
print(np.std(np.abs( new_server_estimation_4[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))

x_axis = date[1:-1]
y_axis = server_num_each_day[1:-1]
y_axis1 = server_estimation[:-1]
y_axis2 = new_server_estimation_2[:-1]
y_axis3 = new_server_estimation_3[:-1]
y_axis4 = new_server_estimation_4[:-1]

fig, ax = plt.subplots(figsize=(20, 10))
ax.set_xlabel("Day", fontsize=24)
ax.set_ylabel("Number of Servers: ", fontsize=24)
plt.axis([None, None, 0, 600])
color_idx = np.linspace(0, 1, 4)
plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", label="baseline", alpha=0.7)
plt.plot(x_axis, y_axis1, "o-", markersize=12, linewidth=3, color=plt.cm.winter(color_idx[0]), label="1 sample in 5/13", alpha=0.7)
plt.plot(x_axis, y_axis2, "o-", markersize=12, linewidth=3, color=plt.cm.winter(color_idx[1]), label="2 samples in 5/13", alpha=0.7)
plt.plot(x_axis, y_axis3, "o-", markersize=12, linewidth=3, color=plt.cm.winter(color_idx[2]), label="3 samples in 5/13", alpha=0.7)
plt.plot(x_axis, y_axis4, "o-", markersize=12, linewidth=3, color=plt.cm.winter(color_idx[3]), label="4 samples in 5/13", alpha=0.7)
ax.set_xticks(np.arange(0,10,1))
ax.set_yticks(np.arange(0,600,50))
ax.grid(which="both")
leg = ax.legend(fontsize=20)
ax.tick_params(axis="both", which='major', labelsize=20)
plt.savefig(argv[1]+'16bit_overall_Diff_Samples.png')
