from sys import argv
from pymongo import MongoClient
from pprint import pprint 
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
# print(whole_sample)

# reading capturing probability
capturing_p = np.zeros((len(date)-1),)
cp_before_sort = []
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
            cp_before_sort.append([int(s[1]), float(s[3])])

cp_before_sort.sort(key = lambda x: x[0])
for i in range(len(date)-1):
    capturing_p[i] = cp_before_sort[i][1]
# print(capturing_p)
whole_estimation = np.array(whole_sample[1:]) / capturing_p
print("estimation")
print(whole_estimation)
err = np.mean(np.abs( whole_estimation[1:-2] - server_num_each_day[2:-2] ) / server_num_each_day[2:-2])
print("error")
print(err)
