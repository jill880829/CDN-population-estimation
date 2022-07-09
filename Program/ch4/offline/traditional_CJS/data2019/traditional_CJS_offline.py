from sys import argv
from pprint import pprint 
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

print("sampling time: "+argv[1]+"-"+argv[2])

date = ["10-28", "10-29", "10-30", "10-31", "11-01", "11-02", "11-03", "11-04", "11-05", "11-06", "11-07", "11-08", "11-09", "11-10"]
server_num_each_day = []
for d in date:
    st = f'2019-{d}T00:00:00Z' 
    et = f'2019-{d}T23:59:59Z'
    q = build_query(st, et, loc='west-us', lang=None)
    result = client.query(q)
    server_set, _ = get_edge_num(result)
    cur_ip_list = list(server_set)
    server_num_each_day.append(len(cur_ip_list))
server_num_each_day = np.array(server_num_each_day)
print("baseline")
print(server_num_each_day)

def get_server_ip_sampling(d, idx, loc, lang=None):
    st = f'2019-{d}T{argv[1]}Z' 
    et = f'2019-{d}T{argv[2]}Z'
    q = build_query(st, et, loc='west-us', lang=None)
    result = client.query(q)
    server_set, _ = get_edge_num(result)
    cur_ip_list = list(server_set)
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

record_server_table = []
last_capture_table = np.zeros((len(date), len(date)), dtype = int)
m_t, u_t, n_t = np.zeros((len(date),), dtype = int), np.zeros((len(date),), dtype = int), np.zeros((len(date),), dtype = int)
record_server_table = []
for j, d in enumerate(date):
    get_server_ip_sampling(d, j, 'west-us')

R_t, Z_t = np.zeros((len(date),), dtype = int), np.zeros((len(date),), dtype = int)    
for d, _ in enumerate(date):
    R_t[d] = np.sum(last_capture_table[(d+1):len(date), d])

for d in range(len(date)):
    Z_t[d] = np.sum(last_capture_table[(d+1):len(date), :d])

alpha_t = (m_t+1)/(n_t+1)
M_t = ((n_t+1)*Z_t/(R_t+1))+m_t
N_t = M_t/alpha_t
estimate_N_24hr_us = N_t
print("estimation")
print(estimate_N_24hr_us)
print("error")
print(np.mean(np.abs(estimate_N_24hr_us[2:-2] - server_num_each_day[2:-2]) / server_num_each_day[2:-2]))