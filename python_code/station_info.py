import urllib.request, urllib.parse, urllib.error
import json
import csv

with open('citybik_bicing_sample.json', 'r') as jsonfile:
    
    #json reading from a local donwloaded sample of https://api.citybik.es/v2/networks/bicing
    try:
        js = json.load(jsonfile)
        js = js['network']['stations']
    except:
        print('==== Error de format ====')

    with open('station_info.csv', 'w', encoding='utf-8') as csvfile:
        
        # csv header
        fieldnames = ['uid','type','name','latitude','longitude','altitude','streetName','streetNumber']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,  quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
       
        # reading URL with other bicing info
        url = 'http://wservice.viabicing.cat/v2/stations'
        uh = urllib.request.urlopen(url)
        data = uh.read().decode()
        try:
            js2 = json.loads(data)
            js2=js2['stations']
        except:
            print('==== Error de recepció ====')
        
        #obtaining bicing static info and csv fullfillment
        for station in js:
            uid = station['extra']['uid']
            streetName = station['extra']['address']
            name = station['name']
            streetName = station['extra']['address']
            longitude  =station['longitude']
            latitude = station['latitude']
            for station2 in js2:
                if int(station2['id'])==uid:
                    typebike=station2['type']
                    altitude=int(station2['altitude'])
                    streetNumber = station2['streetNumber']

            writer.writerow({'uid': uid, 'type':typebike,'name':name,'latitude':latitude,'longitude':longitude,'altitude':altitude,'streetName':streetName,'streetNumber':streetNumber})
            

