from sys import argv
from pymongo import MongoClient
from pprint import pprint 
import csv
import numpy as np

client = MongoClient('localhost:25555')
db = client.Twitch
serverStatusResult = db.command('serverStatus')

print("sampling time: "+argv[1]+"-"+argv[2])

# baseline
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
print("baseline")
print(server_num_each_day)

# MLE-CJS
print("MLE-CJS")

# sampling
whole_sample = []
for i, d in enumerate(date):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T"+argv[2] }, "end": { "$gte": "2021-"+d+"T"+argv[1] }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T"+argv[1] and tm <= "2021-"+d+"T"+argv[2]:
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    whole_sample.append(len(cur_ip_list))

# reading capturing probability
capturing_p = np.zeros((len(date)),)
for i in range(3, 11):
    cp_before_sort = []
    with open('out'+str(i)+'.txt', 'r') as f:
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
                cp_before_sort.append([int(s[1]), float(s[3])])
    cp_before_sort.sort(key = lambda x: x[0])
    capturing_p[i-2] = cp_before_sort[-2][1]

whole_estimation = np.array(whole_sample[1:-1]) / capturing_p[1:-1]
print("estimation")
print(whole_estimation)
err = np.mean(np.abs( whole_estimation[1:-1] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2])
print("error")
print(err)

# traditional CJS
print("traditional CJS")

def get_server_ip_sampling(d, idx, loc, lang=None):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T01:00:00" }, "end": { "$gte": "2021-"+d+"T00:00:00" }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T00:00:00" and tm <= "2021-"+d+"T01:00:00":
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
    last_rec = np.zeros((idx,), dtype = int)
    marked_sum = 0
    if idx > 0:
        for server in cur_ip_list:
            for d, server_cluster in enumerate(record_server_table[::-1]):
                if server in server_cluster:
                    last_rec[d] += 1
                    marked_sum += 1
                    break
        last_capture_table[idx, :idx] = last_rec[::-1]  
    m_t[idx] = marked_sum
    u_t[idx] = len(cur_ip_list)-marked_sum
    n_t[idx] = len(cur_ip_list)
    record_server_table.append(cur_ip_list)

date1 = []
estimate_N_24hr_us = []
for i, D in enumerate(date):
    date1.append(D)
    record_server_table = []
    last_capture_table = np.zeros((len(date1), len(date1)), dtype = int)
    m_t, u_t, n_t = np.zeros((len(date1),), dtype = int), np.zeros((len(date1),), dtype = int), np.zeros((len(date1),), dtype = int)
    record_server_table = []
    for j, d in enumerate(date1):
        get_server_ip_sampling(d, j, 'west-us')

    R_t, Z_t = np.zeros((len(date1),), dtype = int), np.zeros((len(date1),), dtype = int)    
    for d, _ in enumerate(date1):
        R_t[d] = np.sum(last_capture_table[(d+1):len(date1), d])

    for d in range(len(date1)):
        Z_t[d] = np.sum(last_capture_table[(d+1):len(date1), :d])

    alpha_t = (m_t+1)/(n_t+1)
    M_t = ((n_t+1)*Z_t/(R_t+1))+m_t
    N_t = M_t/alpha_t
    if i > 0:
        estimate_N_24hr_us.append(N_t[-2])

print("estimation")
print(estimate_N_24hr_us)
print("error")
print(np.mean(np.abs(estimate_N_24hr_us[2:-1] - server_num_each_day[2:-2]) / server_num_each_day[2:-2]))

# plotting figure
import matplotlib.pyplot as plt
x_axis = date[2:-1]
y_axis = server_num_each_day[2:-1]
y_axis1 = whole_estimation[1:]
y_axis2 = estimate_N_24hr_us[1:-1]
fig, ax = plt.subplots(figsize=(20, 10))
ax.set_xlabel("Day", fontsize=24)
ax.set_ylabel("Number of Servers", fontsize=24)
plt.axis([None, None, 0, 600])
plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", label="baseline", alpha=0.7)
plt.plot(x_axis, y_axis1, "o-", markersize=12, linewidth=3, color="b", label="MLE-CJS", alpha=0.7)
plt.plot(x_axis, y_axis2, "o-", markersize=12, linewidth=3, color="g", label="Traditioinal-CJS", alpha=0.7)
ax.set_xticks(np.arange(0,10,1))
ax.set_yticks(np.arange(0,600,50))
ax.grid(which="both")
leg = ax.legend(fontsize=20)
ax.tick_params(axis="both", which='major', labelsize=20)
plt.savefig(argv[3]+'delay_one_day.png')