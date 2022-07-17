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
print(server_num_each_day)
print(np.std(server_num_each_day))

x_axis = date
y_axis = server_num_each_day
fig, ax = plt.subplots(figsize=(20, 10))
ax.set_xlabel("Day", fontsize=24)
ax.set_ylabel("Number of Servers", fontsize=24)
plt.axis([None, None, 0, 600])
plt.plot(x_axis, y_axis, "o-", markersize=12, linewidth=3, color="k", alpha=0.7)
ax.set_xticks(np.arange(0,10,1))
ax.set_yticks(np.arange(0,600,50))
ax.grid(which="both")
ax.tick_params(axis="both", which='major', labelsize=20)
plt.savefig(argv[1]+'daily_count.png')