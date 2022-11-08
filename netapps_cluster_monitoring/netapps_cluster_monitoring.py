#!/usr/bin/python3
import json
import requests
import urllib3 as ur
import base64

PLUGIN_VERSION=1
HEARTBEAT=True
METRICS_UNITS={}


metrics={
    "throughtput_read":("metric","throughput","read"),
    "throughtput_total":("metric","throughput","total"),
    "throughtput_write":("metric","throughput","write"),
    "latency_read":("metric","latency","read"),
    "latency_total":("metric","latency","total"),
    "latency_write":("metric","latency","write"),
    "iops_read":("metric","iops","read"),
    "iops_total":("metric","iops","total"),
    "iops_write":("metric","iops","write")
}

class netapps:

    def __init__(self,args):
        
        self.maindata={}
        self.maindata['plugin_version'] = PLUGIN_VERSION
        self.maindata['heartbeat_required']=HEARTBEAT
        self.maindata['units']=METRICS_UNITS
        self.hostname=args.hostname
        self.port=args.port
        self.username=args.username
        self.password=args.password

    def setup_connection(self,api_user: str, api_pass: str):
        base64string = base64.encodebytes(
            ('%s:%s' %
            (api_user, api_pass)).encode()).decode().replace('\n', '')

        headers = {
            'authorization': "Basic %s" % base64string,
            'content-type': "application/json",
            'accept': "application/json"
        }
        return headers
    
    def apiconnect(self):
        try:
            #conn = HostConnection("1.1.1.1", username="admin",password="mypassword", verify=False)
            #config.CONNECTION = conn

            cluster=self.hostname+":"+self.port
            api_url=f"http://{cluster}/cluster"
            headers=self.setup_connection(self.username,self.password)
            response=requests.get(api_url,headers=headers,verify=False)

            if response.status_code == 200 :
                self.response=response
            else:
                self.maindata['status'] = '0'
                self.maindata['msg'] = 'Invalid response after opening URL : ' + str(response.status_code) 

        except requests.exception.HTTPError as e:
            self.maindata['status'] = '0'
            self.maindata['msg'] ='HTTP Error '+str(e.code)
        except requests.exceptions.URLError as e:
            self.maindata['status'] = '0'
            self.maindata['msg'] = 'URL Error '+str(e.reason)
        except requests.exceptions.InvalidURL as e:
            self.maindata['status'] = '0'
            self.maindata['msg'] = 'Invalid URL'
        except requests.exceptions.Exception as e:
            self.maindata['status'] = '0'
            self.maindata['msg'] = str(e)
        finally:
            return response.status_code 


    def metriccollector(self):
        try:
            status_code=self.apiconnect()
            if status_code == 200:
                response=json.loads(self.response.text)
                for metric in metrics:
                    data=response
                    for _ in metrics[metric]:
                        data=data[_]
                    self.maindata[metric]=data

                self.maindata["name"]=response['name']
                self.maindata["uuid"]=response['uuid']

        except Exception as e:
            self.maindata['msg']=str(e)
            self.maindata['status']=0
        return self.maindata


if __name__=="__main__":
    
    username=None
    password=None
    hostname="localhost"
    port="433"

    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--hostname',help="Enter the hostname for netapps",default=hostname)
    parser.add_argument('--port',help="Enter the port for netapps",default=hostname)
    parser.add_argument('--username',help="Enter the username for netapps",default=username)
    parser.add_argument('--password',help="Enter the password for netapps",default=password)

    args=parser.parse_args()
    obj=netapps(args)
    result=obj.metriccollector()
    print(json.dumps(result,indent=True))
