# -*- coding: utf-8 -*-

#import requests
import urllib.request, urllib.parse, urllib.error
import json
import pymysql.cursors
import os
import time
import re
from datetime import datetime as dt, timedelta as td

def escriu_a_mysql(bicing,v2):
    #fem connexió
    connection = pymysql.connect(host='localhost',
                                user='root',
                                password='',
                                db='bicing',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # idBici=int(bicing["id"])
            # altitude=int(bicing["altitude"])
            # slots=int(bicing["slots"])
            # bikes=int(bicing["bikes"])
            # sql = "INSERT INTO bicing (id, type, latitude, longitude, streetName, streetNumber, altitude, slots, bikes,\
            # nearbyStations,status,date1) \
            # VALUES (%d, %s, %8.6f, %7.6f, %s, %s, %d, %d, %d, %s, %s, %s)"
            # #executem SQL amb valors del camp "bicing"
            # cursor.execute(sql, (idBici, bicing["type"],\
            # float(bicing["latitude"]), float(bicing["longitude"]), bicing["streetName"], bicing["streetNumber"], \
            # altitude, slots, bikes, bicing["nearbyStations"], bicing["status"], date1))
            #definim plantilla ordre SQL

            #Modificar dates
            updateTime=str(dt.now())
            updateTime=re.sub('\..*','',updateTime)

            timeStp=v2['timestamp']
            if len(timeStp)<19:
                timeStp=re.sub(r'(T)(.+)(:\w)',r' \2:00',timeStp)
            else:
                timeStp=re.sub(r'(T)(.+)(\..*)',r' \2',timeStp)
                
            timeStp=dt.strptime(timeStp, "%Y-%m-%d %H:%M:%S")+td(hours=1)

            #Inserir dades a la BD
            sql = "INSERT INTO bicing (uid, type, name, latitude, longitude, altitude, streetName, streetNumber, cp, districtCode, \
            slots, bikes, nearbyStations, status, timestamp, updateTime) "\
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" 
            #executem SQL amb valors del camp "bicing"
            cursor.execute(sql, (bicing["id"], bicing["type"], v2['name'], bicing["latitude"], bicing["longitude"], bicing["altitude"], \
            bicing["streetName"], bicing["streetNumber"], v2['extra']['zip'], v2['extra']['districtCode'], \
            bicing["slots"], bicing["bikes"], bicing["nearbyStations"], bicing["status"], timeStp, updateTime))

        connection.commit()

    except Exception as e:
        print (e)

    finally:
        connection.close()

    return True

def mysql_bicis(elm):
    #fem connexió
    conn = pymysql.connect(host='localhost',
                                user='root',
                                password='',
                                db='bicing',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO bicing (uid, type, name, latitude, longitude, altitude, streetName, streetNumber, cp, districtCode, \
            slots, bikes, nearbyStations, status, timestamp, updateTime) "\
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" 
            
        conn.commit()

    except Exception as e:
        print (e)

    finally:
        conn.close()

    return True

#App
def internet_on():
    try:
        urllib.request.urlopen('http://216.58.211.238', timeout=1)
        return True
    except urllib.request.URLError as err: 
        print(err)
        return False

#BICING
url = "http://wservice.viabicing.cat/v2/stations"
url2= "http://api.citybik.es/v2/networks/bicing"

last_str_json = ""
last_str_json2 = ""

cont=0
while True:
    origen_web = urllib.request.urlopen(url)
    origen_web2 = urllib.request.urlopen(url2)
    # obtenim el darrer json de la web
    str_json = origen_web.read().decode()
    str_json2 = origen_web2.read().decode()

    # si l'anterior json llegit és igual a l'acabat de llegir, voldrà dir que ja és a la BDD
    # esperem un minut i reiniciem el loop
    if (last_str_json==str_json and last_str_json2==str_json2) or not internet_on():
      time.sleep(60)
      continue
    cont+=1
    print(cont)

    # actualizem "last_str_json" per al proper loop
    last_str_json = str_json
    last_str_json2 = str_json2
    
    #iniciem desat a base de dades
    try:
        current_dataset = json.loads(str_json)
        current_dataset=current_dataset['stations']

        current_dataset2 = json.loads(str_json2)
        current_dataset2=current_dataset2['network']['stations']
    except Exception as e:
        current_dataset = None
        current_dataset2 = None
        print(e)

    #si la comprobació es correcte, passar a l'acció
    if current_dataset != None and current_dataset2 != None:

        for element in current_dataset:
            elm2=""

            for elm in current_dataset2:
                if int(elm['extra']['uid'])==int(element['id']):
                    elm2=elm
                    break

            escriu_a_mysql(element,elm2)