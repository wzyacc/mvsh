#!/bin/python
#coding:utf-8


cf_spiders = {
            "lol5s":[
                    {"spider":"lol5s_mv","update_type":0,"gap":5*60},
                    {"spider":"lol5s_tv","update_type":0,"gap":5*60},
                    {"spider":"lol5s_tv_en","update_type":0,"gap":5*60},
                    {"spider":"lol5s_dm","update_type":0,"gap":5*60},
                    {"spider":"lol5s_zy","update_type":0,"gap":5*60},
                ],
        }
cf_redis_uri = "redis://127.0.0.1"
cf_sd_base_url = "http://127.0.0.1:6800/"
cf_sd_schedule_url = cf_sd_base_url+'schedule.json'
cf_sd_job_url = cf_sd_base_url+'listjobs.json?project={0}'
