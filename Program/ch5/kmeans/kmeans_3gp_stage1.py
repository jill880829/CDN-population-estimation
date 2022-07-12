from sys import argv
from pymongo import MongoClient
from pprint import pprint 
import csv
import numpy as np

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
with open('cluster_result.csv', newline='') as csvfile:
    rows = csv.reader(csvfile)
    for row in rows:
        if row[2] not in ip_list:
            continue
        ip_group_dict[row[2]] = row[1]

# sampling and transforming input data format
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