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

# MLE-CJS
print("MLE-CJS")

# samping
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
capturing_p = np.zeros((6,len(date)),)
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
    capturing_p[0,i-1] = cp_before_sort[-1][1]
    capturing_p[1,i-2] = cp_before_sort[-2][1]
    if i >= 4:
        capturing_p[2,i-3] = cp_before_sort[-3][1]
    if i >= 5:
        capturing_p[3,i-4] = cp_before_sort[-4][1]
    if i >= 6:
        capturing_p[4,i-5] = cp_before_sort[-5][1]
    if i >= 7:
        capturing_p[5,i-6] = cp_before_sort[-6][1]

err = []
# delay 0 day
whole_estimation = np.array(whole_sample[2:]) / capturing_p[0, 2:]
# print("delay 0 day")
# print(whole_estimation)
err.append(np.mean(np.abs( whole_estimation[:-1] - server_num_each_day[2:-1] ) / server_num_each_day[2:-1]))
# delay 1 day
whole_estimation = np.array(whole_sample[1:-1]) / capturing_p[1, 1:-1]
# print("delay 1 day")
# print(whole_estimation)
err.append(np.mean(np.abs( whole_estimation[1:-1] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))
# delay 2 days
whole_estimation = np.array(whole_sample[1:-2]) / capturing_p[2, 1:-2]
# print("delay 2 days")
# print(whole_estimation)
err.append(np.mean(np.abs( whole_estimation[1:] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2]))
# delay 3 days
whole_estimation = np.array(whole_sample[1:-3]) / capturing_p[3, 1:-3]
# print("delay 3 days")
# print(whole_estimation)
print(np.abs( whole_estimation[1:] - server_num_each_day[2:-3] ) / server_num_each_day[2:-3])
err.append(np.mean(np.abs( whole_estimation[1:] - server_num_each_day[2:-3] ) / server_num_each_day[2:-3]))
# delay 4 days
whole_estimation = np.array(whole_sample[1:-4]) / capturing_p[4, 1:-4]
# print("delay 4 days")
# print(whole_estimation)
err.append(np.mean(np.abs( whole_estimation[1:] - server_num_each_day[2:-4] ) / server_num_each_day[2:-4]))
# delay 5 days
whole_estimation = np.array(whole_sample[1:-5]) / capturing_p[5, 1:-5]
# print("delay 5 days")
# print(whole_estimation)
err.append(np.mean(np.abs( whole_estimation[1:] - server_num_each_day[2:-5] ) / server_num_each_day[2:-5]))
print("error")
print(err)

# traditional CJS
print("traditional CJS")

def get_server_ip_sampling(d, idx, loc, lang=None):
    streams = db.United_States.find({ "start": { "$lte": "2021-"+d+"T"+argv[2] }, "end": { "$gte": "2021-"+d+"T"+argv[1] }})
    cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T"+argv[1] and tm <= "2021-"+d+"T"+argv[2]:
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

# real time estimation
traditional_err = []
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
    if i >= 2:
        LM = np.polyfit(n_t[:-1], R_t[:-1], 1)
        LMF = np.poly1d(LM)
        R_t[-1] = LMF(n_t[-1])

    for d in range(len(date1)):
        Z_t[d] = np.sum(last_capture_table[(d+1):len(date1), :d])
    if i >= 2:
        LM = np.polyfit(n_t[:-1], Z_t[:-1], 1)
        LMF = np.poly1d(LM)
        Z_t[-1] = LMF(n_t[-1])

    alpha_t = (m_t+1)/(n_t+1)
    M_t = ((n_t+1)*Z_t/(R_t+1))+m_t
    N_t = M_t/alpha_t
    estimate_N_24hr_us.append(N_t[-1])

traditional_err.append(np.mean(np.abs(estimate_N_24hr_us[2:-1] - server_num_each_day[2:-1]) / server_num_each_day[2:-1]))

# delayed estimaiton
date1 = []
estimate_N_24hr_us = [[], [], [], [], []]
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
        estimate_N_24hr_us[0].append(N_t[-2])
    if i > 1:
        estimate_N_24hr_us[1].append(N_t[-3])
    if i > 2:
        estimate_N_24hr_us[2].append(N_t[-4])
    if i > 3:
        estimate_N_24hr_us[3].append(N_t[-5])
    if i > 4:
        estimate_N_24hr_us[4].append(N_t[-6])

traditional_err.append(np.mean(np.abs(estimate_N_24hr_us[0][2:-1] - server_num_each_day[2:-2]) / server_num_each_day[2:-2]))
traditional_err.append(np.mean(np.abs(estimate_N_24hr_us[1][2:] - server_num_each_day[2:-2]) / server_num_each_day[2:-2]))
traditional_err.append(np.mean(np.abs(estimate_N_24hr_us[2][2:] - server_num_each_day[2:-3]) / server_num_each_day[2:-3]))
traditional_err.append(np.mean(np.abs(estimate_N_24hr_us[3][2:] - server_num_each_day[2:-4]) / server_num_each_day[2:-4]))
traditional_err.append(np.mean(np.abs(estimate_N_24hr_us[4][2:] - server_num_each_day[2:-5]) / server_num_each_day[2:-5]))
print("error")
print(traditional_err)

# plotting figure
import matplotlib.pyplot as plt
x_axis = [0, 1, 2, 3, 4, 5]
y_axis = traditional_err
y_axis1 = err
x = np.arange(len(x_axis))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, y_axis, width, label='Traditional')
rects2 = ax.bar(x + width/2, y_axis1, width, label='MLE')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_xlabel('Length of Delay')
ax.set_ylabel('Error Rates')
# ax.set_title('Average Estimation Error Rates with Delays')
ax.set_xticks(x)
ax.set_xticklabels(x_axis)
ax.legend()

fig.tight_layout()
plt.savefig(argv[3])