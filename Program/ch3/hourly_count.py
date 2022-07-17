from sys import argv
from pymongo import MongoClient
from pprint import pprint 
import csv
import numpy as np
import matplotlib.pyplot as plt

client = MongoClient('localhost:25555')
db = client.Twitch
serverStatusResult = db.command('serverStatus')

date = ["05-07", "05-08", "05-09", "05-10", "05-11", "05-12", "05-13", "05-14", "05-15"]
time1 = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
time2 = ["01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00", "23:59"]

server_num_each_hour = []
transaction_each_hour = []
for d in date:
    server_num_in_one_day = []
    cur_transaction = [0]*24
    for i, (t1, t2) in enumerate(zip(time1, time2)):
        streams = db.United_States.find({ "start": { "$lt": "2021-"+d+"T"+t2 }, "end": { "$gte": "2021-"+d+"T"+t1 }})
        cur_ip_list = list()
        for s in streams:
            for (tm, ip) in s["transactionList"].items():
                if tm >= "2021-"+d+"T"+t1+":00" and tm <= "2021-"+d+"T"+t2+":00":
                    cur_transaction[i] += 1
                    if ip not in cur_ip_list:
                        cur_ip_list.append(ip)
        server_num_in_one_day.append(len(cur_ip_list))
    server_num_each_hour.append(server_num_in_one_day)
    transaction_each_hour.append(cur_transaction)
print(server_num_each_hour)
print(transaction_each_hour)

server_num_each_hour = np.array(server_num_each_hour)
server_num_each_hour_avg = np.mean(server_num_each_hour, axis=0)
server_num_each_hour_std = np.std(server_num_each_hour, axis=0)

x_axis = np.linspace(0, 23, 24)
y_axis = server_num_each_hour_avg
error = server_num_each_hour_std
fig, ax = plt.subplots(figsize=(20, 10))
ax.set_xlabel("Time of Day", fontsize=24)
ax.set_ylabel("Number of Servers", fontsize=24)
plt.axis([None, None, 0, 600])
plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", alpha=0.7)
plt.fill_between(x_axis, y_axis-error, y_axis+error, alpha=0.3)
ax.set_xticks(np.arange(0,24,1))
ax.set_yticks(np.arange(0,600,50))
ax.grid(which="both")
ax.tick_params(axis="both", which='major', labelsize=20)
plt.savefig(argv[1]+'hourly_count.png')