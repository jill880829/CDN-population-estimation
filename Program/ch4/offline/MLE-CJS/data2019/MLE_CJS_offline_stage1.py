from sys import argv
from pprint import pprint 
import datetime
import numpy as np
from influxdb import InfluxDBClient

client = InfluxDBClient(host='140.112.42.161', port=23234, database='test_2')

CODE_TO_COUNTRY = {              # country language code to full language name  
        'zh-tw': 'Taiwan',
        'west-eu': 'Europe',
        'west-us': 'West US',
    }

def build_query(t_s, t_e, channel=None, lang=None, loc=None):
    """
    gets all data from month/date to month/(date+1)
    t_s: time start
    t_e: time end 
    lang: stream language
    loc: client location 
    """
    channel = '/.*/' if channel is None else channel
    q = f"SELECT viewer, client_location, ip_list, fq_count, num_edge FROM {channel} WHERE time >= '{t_s}' AND time < '{t_e}'"
    if lang:
        q = f"{q} AND stream_language = '{lang}'"
    if loc:
        q = f"{q} AND client_location = '{loc}'"
    return q

def get_edge_num(result):
    tmp = list()
    transactions = 0
    for (stream, _), points in result.items():
        for point in points:
            edges = point['ip_list'].split(',')
            transactions += sum([int(fq) for fq in point['fq_count'].split(',')])
            for edge in edges:
                if edge not in tmp:
                    tmp.append(edge)
    return set(tmp), transactions

def get_edge_list(result):
    record = list()
    for (stream, _), points in result.items():
        for point in points:
            edges = point['ip_list'].split(',')
            record.append(edges)
    return record

st = f'2019-10-28T00:00:00Z' 
et = f'2019-11-10T23:59:59Z'
q = build_query(st, et, loc='west-us', lang=None)
result = client.query(q)
server_set, _ = get_edge_num(result)
ip_list = list(server_set)

date = ["10-28", "10-29", "10-30", "10-31", "11-01", "11-02", "11-03", "11-04", "11-05", "11-06", "11-07", "11-08", "11-09", "11-10"]

# sampling and transforming input data format
ip_dict = dict.fromkeys(ip_list, "")
for d in date:
    st = f'2019-{d}T{argv[1]}Z' 
    et = f'2019-{d}T{argv[2]}Z'
    q = build_query(st, et, loc='west-us', lang=None)
    result = client.query(q)
    server_set, _ = get_edge_num(result)
    cur_ip_list = list(server_set)
    for ip in ip_list:
        if ip in cur_ip_list:
            ip_dict[ip] += "1"
        else:
            ip_dict[ip] += "0"

ip_and_ch = ip_dict.items()
ip_ch_rec = []
for (ip, ch) in ip_and_ch:
    if ch == "0"*len(date):
        continue
    ip_ch_rec.append(ch)

with open('tmp.txt', 'w') as f:
    for ch in ip_ch_rec:
        f.writelines(ch+'\n')
