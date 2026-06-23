
from dao.runnable_services_dao import runnableServicesDao

from commons.function.common_function import *
from commons.classes.log import *


import os
from dotenv import load_dotenv
load_dotenv()
                               
import requests
import json
import math

class CoinVillageService():

    def __init__(self):
        self.log = Log()
        self.log.create_log()

        self.runnable_services_dao = runnableServicesDao()

    def load_runnable_services(self, request):
        
        runnable_services = self.runnable_services_dao.get_runnable_services()
        return {
            "request" : request,
            "response" : {
                "result" : True,
                "msg" : "",
                "data" : {
                    "runnable_services" : runnable_services
                }
            }
        }
    
    def onoff_runnable_services(self, request):
        
        params = {
            "activate_yn" : request["activate_yn"]
        }
        self.runnable_services_dao.update_runnable_services(params, request["seq"])

        return {
            "request" : request,
            "response" : {
                "result" : True,
                "msg" : "",
                "data" : {
                }
            }
        }
    
    def insert_runnable_services(self, request):

        params = {}
        if request.get("execution_method"):
            params["execution_method"] = request.get("execution_method")
            
        if request.get("service_options"):
            params["service_options"] = request.get("service_options")
            
        if request.get("product_name"):
            params["product_name"] = request.get("product_name")
            
        if request.get("product_desc"):
            params["product_desc"] = request.get("product_desc")
            
        if request.get("interval_options"):
            params["interval_options"] = request.get("interval_options")
            
        if request.get("schedule_options"):
            params["schedule_options"] = request.get("schedule_options")
        
        self.runnable_services_dao.insert_runnable_services(params)

        return {
            "request" : request,
            "response" : {
                "result" : True,
                "msg" : "",
                "data" : {
                }
            }
        }
        
    def update_runnable_services(self, request):
        
        params = {}
        if request.get("execution_method"):
            params["execution_method"] = request.get("execution_method")

        if request.get("service_options"):
            params["service_options"] = request.get("service_options")

        if request.get("interval_options"):
            params["interval_options"] = request.get("interval_options")

        if request.get("schedule_options"):
            params["schedule_options"] = request.get("schedule_options")
        
        self.runnable_services_dao.update_runnable_services(params, request["seq"])

        return {
            "request" : request,
            "response" : {
                "result" : True,
                "msg" : "",
                "data" : {
                }
            }
        }
    
    def onoff_webbot_services(self, request):
        
        res = self.runnable_services_dao.get_runnable_service(request["seq"])
        if request["activate_yn"] == "Y":
            url = f"{os.getenv('WEBBOT_HOST')}:{os.getenv('WEBBOT_PORT')}/{res['webbot_start_path']}"

        else:   
            url = f"{os.getenv('WEBBOT_HOST')}:{os.getenv('WEBBOT_PORT')}/{res['webbot_end_path']}"

        response = requests.get(url)

        params = {
            "activate_yn" : request["activate_yn"]
        }
        self.runnable_services_dao.update_runnable_services(params, request["seq"])

        return {
            "request" : request,
            "response" : {
                "result" : True,
                "msg" : "",
                "data" : {
                }
            }
        }