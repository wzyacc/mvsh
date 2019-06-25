#!/bin/python
#coding:utf-8

import requests
import json
import datetime
import pdb
import time

from config import *

def parse_need_run_spiders(project,spider_schedules):
    sp_pending = []
    sp_last_finished = {}
    url = cf_sd_job_url.format(project)
    req = requests.get(url)
    js = json.loads(req.content)
    for job in js["pending"]:
        sp_name = job["spider"]
        sp_pending.append(sp_name)
    for job in js["running"]:
        sp_name = job["spider"]
        sp_pending.append(sp_name)

    for job in js["finished"]:
        sp_name = job["spider"]
        sp_end_t = datetime.datetime.strptime(job["end_time"].split('.')[0],"%Y-%m-%d %H:%M:%S") 
        if not sp_last_finished.has_key(sp_name):
            sp_last_finished[sp_name] = sp_end_t
            continue

        if sp_last_finished[sp_name] < sp_end_t:
            sp_last_finished[sp_name] = sp_end_t
    for sp_name in spider_schedules.keys():
        if sp_name in sp_pending:
            continue
        end_t = sp_last_finished.get(sp_name,None)
        if not end_t:
            yield project,sp_name
            continue
        gap = spider_schedules[sp_name]
        now_t = datetime.datetime.now()
        if now_t > end_t + datetime.timedelta(seconds=gap):
            yield project,sp_name

        

def parse_spiders():
    for project in cf_spiders.keys():
        spider_schedules = {}
        for spider in cf_spiders[project]:
            spider_schedules[spider["spider"]]=spider["gap"]
        yield parse_need_run_spiders(project,spider_schedules)

def run_spider(project,spider):
    url = cf_sd_schedule_url
    data = {"project":project,"spider":spider}
    req = requests.post(url,data=data)
    print req.content
    js = json.loads(req.content)
    if js["status"] != 'ok':
        print js


def run():
    for sinfo in parse_spiders():
        for project,spider in sinfo:
            run_spider(project,spider)

def main():
    while True:
        run()
        time.sleep(3)

if __name__ == "__main__":
    main()
