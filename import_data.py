#! /usr/bin/env python
# -*- coding: utf-8 -*-

from influxdb import InfluxDBClient
from pprint import pprint
import json
import csv
import time
import datetime
from os import listdir
from os.path import isfile, join

def parse_file(file):
    data = {}
    with open(file, 'rb') as csvfile:
        aqireader = csv.reader(csvfile, delimiter=',')
        headers = next(aqireader, None)
        for row in aqireader:
            process_row(row, headers, data)
    return data

def process_row(row, headers, data):
    date = row[0]
    hour = row[1]
    timestamp = int(time.mktime(time.strptime(date+" "+hour, "%Y%m%d %H"))).__str__()
    data_type = row[2]
    for column in range(3, len(headers)):
        city = headers[column]
        value = row[column]
        if city not in data:
            data[city] = {}
        if timestamp not in data[city]:
            data[city][timestamp] = {}
        data[city][timestamp][data_type] = value

def prepare_db_data(data):
    batch = []
    for city, timedata in data.iteritems():
        for timestamp, air_quality in timedata.iteritems():
            dbdata = {
                "measurement": "air_quality",
                "time": datetime.datetime.fromtimestamp(float(timestamp)).isoformat("T"),
                "fields": air_quality,
                "tags":{
                    "city": city
                }
            }
            batch.append(dbdata)
    return batch

#file = "./data/china_cities_20140514.csv"
directory = "./data"
client = InfluxDBClient('localhost', 8086, 'admin', 'xjvw43sfd', 'pkaqi')
print(client.get_list_database())
print(client.query('show measurements;'))
client.query("drop measurement air_quality")
#client.create_database('pkaqi')

csvfiles = [f for f in listdir(directory) if isfile(join(directory, f)) and f.endswith(".csv")]

for csvfile in csvfiles:
    csvfile = join(directory, csvfile)
    print(csvfile)
    try:
        raw_data = parse_file(csvfile)
        db_data = prepare_db_data(raw_data)
        client.write_points(db_data)
    except Exception, e:
        pprint(e)
        continue