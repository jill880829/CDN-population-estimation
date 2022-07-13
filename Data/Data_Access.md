# Data Access

In this study, US data sets in 2019 and 2021 are used for server population in Twitch's CDN. Both data sets are collected by Caleb Wang (graduated in 2021).

These two data sets are stored in the NSLab servers. This readme will introduce the steps to access these two data sets with Python scripts.

## 2019 Data Set

1. Import the package and connect to the DB.
```python=
from influxdb import InfluxDBClient
client = InfluxDBClient(host='140.112.42.161', port=23234, database='test_2')

```
2. Set up the country code.
```python=
CODE_TO_COUNTRY = { 
        'zh-tw': 'Taiwan',
        'west-eu': 'Europe',
        'west-us': 'West US',
    }
```
3. Define a function for building query statement.
```python=
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
```
4. Define a function to extract information of server and transaction numbers.
```python=
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

```
5. A simple example to access the data set.
```python=
# start time
st = f'2019-10-28T00:00:00Z'
# end time
et = f'2019-11-10T23:59:59Z'
# build query statement
q = build_query(st, et, loc='west-us', lang=None)
# receive the result from the DB
result = client.query(q)
# extract info from the result
# the first one is the server list, and the second one is the transaction numer.
server_set, _ = get_edge_num(result)
ip_list = list(server_set)
```

## 2021 Data Set

1. Connect to the server with IP "140.112.42.161" through SSH.
2. Import the package and connect to the DB.
```python=
from pymongo import MongoClient
client = MongoClient('localhost:25555')
db = client.Twitch
serverStatusResult = db.command('serverStatus')
```
3. Receive the DB result with the given query statement.
```python=
# query streams with start time earlier than 1 am
# or and end time later than 0 am.
streams = db.United_States.find({ "start": { "$lte": "2021-05-08T01:00:00" }, "end": { "$gte": "2021-05-08T00:00:00" }})
```
4. Extract server IPs from the transaction lists.
```python=
cur_ip_list = list()
    for s in streams:
        for (tm, ip) in s["transactionList"].items():
            if tm >= "2021-"+d+"T"+argv[1] and tm <= "2021-"+d+"T"+argv[2]:
                if ip not in cur_ip_list:
                    cur_ip_list.append(ip)
```