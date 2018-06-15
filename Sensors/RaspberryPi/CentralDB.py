import json
from uuid import uuid4
import requests

HTTP_SUCCESS = 200
AUTH_FILE = 'auth'

TABLES = ['AVG_HOUR', 'AVG_DAY', 'AVG_MONTH', 'AVG_YEAR', 'Type', 'System']
columns = {'date': 'Date', 'value': 'Value'}

class CentralDatabase():

    
    def __init__(self, db, logger, webServerURL):
        self.localDB = db
        self.logger = logger
        self.webServerURL = webServerURL
        self.systemID = self.get_system_id()

    def get_system_id(self):
        with open(AUTH_FILE, 'r+') as f:
            try:
                auth = json.load(f)
                sysID = auth['id']
            except json.decoder.JSONDecodeError:
                sysID = str(uuid4())
                json.dump({'id': sysID}, f)
                # @TODO : send to server
        return sysID

    def _sendGetRequest(self, query, httpParams):
        r = requests.get(self.webServerURL + query, params=httpParams)
        if r.status_code == HTTP_SUCCESS:
            return r.json()
        return None
    
    def getLastRemote(self, tableName):
        params = {'order':columns['date'], 'page': '1,1','transform': '1'}
        date = self._sendGetRequest('/' + tableName, params)
        return date[tableName][0][columns['date']]

    def getNewData(self, tableName):
        types, ret = self.localDB.get_new_data(tableName, self.getLastRemote(tableName))
        print(types)
        return { t:[{'SystemID':self.systemID, columns['date']:str(d['date']), columns['value']:str(d[t]), 'Type':i+1} for d in ret] for i,t in enumerate(types[1:])}

    def sendData(self, data):
        r = requests.post(self.webServerURL + "/AVG_HOUR", data = json.dumps(data))
        print(r)
