import json
from uuid import uuid4
import requests

HTTP_SUCCESS = 200
AUTH_FILE = 'auth'

TABLES = ['AVG_HOUR', 'AVG_DAY', 'AVG_MONTH', 'AVG_YEAR', 'Type', 'System']
columns = {'date': 'Date', 'value': 'Value'}

class CentralDatabase():

    systemID = None
    
    def __init__(self, db, logger, webServerURL):
        self.localDB = db
        self.logger = logger
        self.webServerURL = webServerURL
        self.get_system_id()

    def get_system_id(self):
        with open(AUTH_FILE, 'r+') as f:
            try:
                auth = json.load(f)
                sysID = auth['ID']
                self.logger.info("System authentication key found : " + sysID)
            except json.decoder.JSONDecodeError:
                sysID = str(uuid4())
                self.logger.info("New system authentication key : " + sysID)
            while(not self.systemID):
                params = {'filter': 'ID,eq,' + sysID, 'transform': '1'}
                self.logger.info("Checking key validity...")
                if(not self._sendGetRequest("/System", params)['System']):
                    newID = json.dumps({'ID': sysID, 'Name': 'Rpi', 'Location': 'Grenoble'})
                    requests.post(self.webServerURL + "/System", data=newID)
                    json.dump({'ID': sysID, 'Name': 'Rpi',
                                'Location': 'Grenoble'}, f)
                    self.systemID = sysID
                    self.logger.info("System key created in remote server")
                sysID = str(uuid4())

        

    def _sendGetRequest(self, query, httpParams):
        r = requests.get(self.webServerURL + query, params=httpParams)
        if r.status_code == HTTP_SUCCESS:
            return r.json()
        return r.status_code
    
    def getLastRemote(self, tableName):
        params = {'order':columns['date'] + ",desc", 'page': '1,1','transform': '1'}
        date = self._sendGetRequest('/' + tableName, params)
        if(len(date[tableName]) == 0):
            return "0"
        return date[tableName][0][columns['date']]

    def getNewData(self, tableName):
        types, ret = self.localDB.get_new_data(tableName, self.getLastRemote(tableName))
        print(types)
        return { t:[{'SystemID':self.systemID, columns['date']:str(d['date']), columns['value']:str(d[t]), 'Type':i+1} for d in ret] for i,t in enumerate(types[1:])}

    def sendData(self, scale, data):
        for i in data:
            self.logger.info("Saving data " + i + " in remote server")
            r = requests.post(self.webServerURL + "/" + scale, data = json.dumps(data[i]))
        print(r)
