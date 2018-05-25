#!/usr/bin/python3
# coding=utf-8

import sys, argparse, abc, datetime
import mysql.connector
from mysql.connector import errorcode

def setup_parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-l",help="Host connection MySQL",default="localhost")
        parser.add_argument("-p",help="Port MySQL",default="8001")
        parser.add_argument("-u",help="User MySQL",default="Raspi")
        parser.add_argument("-m",help="Password MySQL",default="Raspi")
        self.args = parser.parse_args()

def setup_mysql(self):
        conn = mysql.connector.connect(
                host=self.args.l, 
                port=self.args.p, 
                user=self.args.u,
                password=self.args.m,
                database="capteur_multi_pollutions"
                )                                
        self.cursor = conn.cursor()

def sens_query(self,query):
        try:
                self.cursor.execute(query)
                self.conn.commit()
        except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))  

today = datetime.date.today()

print(today.year,today.month,today.day)

