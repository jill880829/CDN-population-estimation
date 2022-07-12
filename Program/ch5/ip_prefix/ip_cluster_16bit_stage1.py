from sys import argv
from pymongo import MongoClient
from pprint import pprint 
import numpy as np

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
ip_prefix_dict = {}
for ip in ip_list:
    prefix = find_prefix(ip)
    ip_prefix_dict[ip] = prefix

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
ip_subnet = []
for (ip, ch) in ip_and_ch:
    if ch == "0"*10:
        continue
    ip_ch_rec.append(ch)
    ip_subnet.append(ip_prefix_dict[ip])

with open('ch.txt', 'w') as f:
    for ch in ip_ch_rec:
        f.writelines(ch+'\n')

with open('cluster.txt', 'w') as f:
    for group in ip_subnet:
        f.writelines(group+'\n')
