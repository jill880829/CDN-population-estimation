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

print("sampling time: "+argv[2]+"-"+argv[3])

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

# sampling
whole_sample = []
for i, d in enumerate(date):
    st = f'2019-{d}T{argv[1]}Z' 
    et = f'2019-{d}T{argv[2]}Z'
    q = build_query(st, et, loc='west-us', lang=None)
    result = client.query(q)
    server_set, _ = get_edge_num(result)
    cur_ip_list = list(server_set)
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
