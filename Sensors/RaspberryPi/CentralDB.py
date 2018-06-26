import json
from uuid import uuid4
import requests

HTTP_SUCCESS = 200
AUTH_FILE = 'auth'

TABLES = ['AVG_HOUR', 'AVG_DAY', 'AVG_MONTH', 'AVG_YEAR', 'POLLUTANT', 'SYSTEM']
columns = {'date': 'date', 'value': 'value'}

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
                sysID = json.load(f)['id']
                self.logger.info("System authentication key found : " + sysID)
            except json.decoder.JSONDecodeError:
                sysID = str(uuid4())
                self.logger.info("New system authentication key : " + sysID)
            while(not self.systemID):
                params = {'filter': 'id,eq,' + sysID, 'transform': '1'}
                self.logger.info("Checking key validity...")
                self.logger.info(params)
                if(not self._sendGetRequest("/SYSTEM", params)['SYSTEM']):
                    newID = json.dumps({'id': sysID, 'name': 'Rpi_Strasbourg ', 'latitude': '48.57340529999999', 'longitude': '7.752111300000024'})
                    requests.post(self.webServerURL + "/SYSTEM", data=newID)
                    f.seek(0)
                    json.dump({'id': sysID, 'name': 'Rpi', 'latitude': '45.214498', 'longitude': '5.805896'}, f)
                    self.systemID = sysID
                    self.logger.info("System key created in remote server")
                else:
                    self.systemID = sysID

                sysID = str(uuid4())

        

    def _sendGetRequest(self, query, httpParams):
        r = requests.get(self.webServerURL + query, params=httpParams)
        if r.status_code == HTTP_SUCCESS:
            return r.json()
        return None
    
    def getLastRemote(self, tableName):
        params = {'filter':'systemId,eq,' + self.systemID, 'order':columns['date'] + ",desc", 'page': '1,1','transform': '1'}
        date = self._sendGetRequest('/' + tableName, params)
        self.logger.info(date)
        if(len(date[tableName]) == 0):
            return "0"
        return date[tableName][0][columns['date']]

    def getNewData(self, tableName):
        types, ret = self.localDB.get_new_data(tableName, self.getLastRemote(tableName))
        print(types)
        return { t:[{'systemId':self.systemID, columns['date']:str(d['date']), columns['value']:str(d[t]), 'typeId':i+1} for d in ret] for i,t in enumerate(types[1:])}

    def sendData(self, scale, data):
        for i in data:
            self.logger.info("Saving data " + i + " in remote server")
            r = requests.post(self.webServerURL + "/" + scale, data = json.dumps(data[i]))
        print(r)
