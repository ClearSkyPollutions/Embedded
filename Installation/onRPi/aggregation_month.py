#!/usr/bin/python3
# coding=utf-8

import sys, argparse, abc
import mysql.connector
from mysql.connector import errorcode

global conn,cursor

query_create =  "CREATE TABLE AVG_MONTH (" \
                "date DATETIME NOT NULL, " \
                "pm25 DECIMAL(5,2) UNSIGNED NOT NULL, " \
                "pm10 DECIMAL(5,2) UNSIGNED NOT NULL, " \
                "temperature DECIMAL(5,2) UNSIGNED NOT NULL, " \
                "humidity DECIMAL(5,2) UNSIGNED NOT NULL, " \
                "PRIMARY KEY (date)" \
                ")"

query_insert =  "INSERT INTO AVG_MONTH(date,pm25,pm10,temperature,humidity) " \
                "SELECT date, AVG(pm25), AVG(pm10), AVG(temperature),AVG(humidity) FROM AVG_DAY " \
                "GROUP BY YEAR(date), MONTH(date);"

query_drop = "DELETE FROM AVG_DAY WHERE date < SUBDATE(CURDATE(), INTERVAL 1 YEAR);"
                

def setup_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l",help="Host connection MySQL",default="localhost")
    parser.add_argument("-p",help="Port MySQL",default="7001")
    parser.add_argument("-u",help="User MySQL",default="Sensor")
    parser.add_argument("-m",help="Password MySQL",default="Sensor")
    return parser.parse_args()

def setup_mysql(args):
    global conn,cursor
    conn = mysql.connector.connect(
            host=args.l, 
            port=args.p, 
            user=args.u,
            password=args.m,
            database="capteur_multi_pollutions"
            )                                
    cursor = conn.cursor()

def send_query(query):
    global conn,cursor
    try:
        cursor.execute(query)
        conn.commit()
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


if __name__ == "__main__":
    args = setup_parse()
    setup_mysql(args)

    send_query(query_create)

    send_query(query_insert)

    send_query(query_drop)