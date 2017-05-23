#!/usr/bin/python3
#http://hyperion.nvf.io/latest-image/f437c149-5311-41f1-bddc-60369e69a000/?format=json

APIURL = dict()

APIURL["dat"] = "https://hyperion.nvf.io/latest-image/f967a20a-7b8b-4afe-b9a5-8b45285627a9"
APIURL["ict"] = "https://hyperion.nvf.io/latest-image/57068cd1-60ab-4545-915a-e568ee030fa5"
APIURL["lem"] = "https://hyperion.nvf.io/latest-image/aa389088-02c6-4849-8785-da19683c50c4"
APIURL["hes"] = "https://hyperion.nvf.io/latest-image/f437c149-5311-41f1-bddc-60369e69a000"
APIURL["tri"] = "https://hyperion.nvf.io/latest-image/256035cb-c972-4e47-9eb9-def5dfc0f08a"

WEATHERURL = "http://at8.abo.fi/cgi-bin/en/get_weather"

xpaths = dict()
xpaths["temp"] = '//*[@id="WeatherInfo"]/tr[1]/td[2]/text()'
xpaths["dew"] = '//*[@id="WeatherInfo"]/tr[2]/td[2]/text()'
xpaths["relhumidity"] = '//*[@id="WeatherInfo"]/tr[3]/td[2]/text()'
xpaths["wind"] = '//*[@id="WeatherInfo"]/tr[4]/td[2]/text()'
xpaths["windchill"] = '//*[@id="WeatherInfo"]/tr[5]/td[2]/text()'
xpaths["solarpower"] = '//*[@id="WeatherInfo"]/tr[6]/td[2]/text()'
xpaths["baropressure"] = '//*[@id="WeatherInfo"]/tr[7]/td[2]/text()'
xpaths["rainfall"] = '//*[@id="WeatherInfo"]/tr[8]/td[2]/text()'


import os, sys

files = list()
temp_suffix = ".iowait"

import json
import requests
from datetime import datetime as dt
from lxml import html

def getJSONObject(url):
    #we get the jason data from the API
    json_text = requests.get(url, verify=False).text
    #and we parse it and return it
    return json.loads(json_text)

def getDate(rfc3339):
    return dt.strptime(rfc3339, '%Y-%m-%dT%H:%M:%SZ')

def downloadJPEG(url, dest_path):
    r = requests.get(url, stream=False, verify=False)
    f = open("{0}{1}".format(dest_path, temp_suffix), "wb")
    f.write(r.content)
    r.close()
    f.close()
    files.append(dest_path)

def getWeatherData(url, xpaths):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    data = dict()
    for item in xpaths:
        data[item] = tree.xpath(xpaths[item])[0].strip()

    return json.dumps(data)

def saveJSON(path, json):
    f = open("{0}{1}".format(path, temp_suffix), "w")
    f.write(json)
    f.close()
    files.append(path)
    
def checkAndCreateDir(dest_dir):
    #check the destination dir, if it doesn't exist, just create it
    if not (os.path.isdir(dest_dir)):
        os.makedirs(dest_dir)
    
def main(argv):
    print("Lemminbot v0.5-tbo")    
    BASE_DIR = "/tmp/rsyncing"
    print("Downloading to {}".format(BASE_DIR))
    
    #get weather data
    try:
        weather_json = getWeatherData(WEATHERURL, xpaths)
        now = dt.utcnow()
        now_rfc3339 = dt.strftime(now, '%Y-%m-%dT%H:%M:%SZ').replace(":", "-")
        
        weather_dest_dir = "{0}/{1:02}{2:02}{3:02}/weather".format(BASE_DIR, now.year, now.month, now.day)
        weather_dest_filename = "weather-{0}.json".format(now_rfc3339)
        weather_path = "{0}/{1}".format(weather_dest_dir, weather_dest_filename)
        
        #check the destination dir, if it doesn't exist, just create it
        checkAndCreateDir(weather_dest_dir)
        saveJSON(weather_path, weather_json)
        print("Saved weather data on {0}{1}".format(weather_path, temp_suffix))
    except IndexError:
        print("The weather site is dead?")
    except requests.exceptions.ConnectionError:
        print("Weather data unavailable. Probably abo.fi dead")
    
    #do this for all api endpoints
    for site in APIURL:
        #get the json object from API request
        try:
            obj = getJSONObject(APIURL[site])
        except ValueError:
            print("The {0} API endpoint is dead.".format(site))
            continue

        #get the timestamp
        ts = getDate(obj["timestamp"])
        #directory and file name 
        dest_dir = "{0}/{1:02}{2:02}{3:02}/{4}".format(BASE_DIR, ts.year, ts.month, ts.day, site)
        dest_filename = "{0}-{1}.jpg".format(site, obj["timestamp"].replace(":", "-"))
        path = "{0}/{1}".format(dest_dir, dest_filename)
        
        #check the destination dir, if it doesn't exist, just create it
        checkAndCreateDir(dest_dir)
        #check if the file has already been downloaded
        if os.path.exists(path):
            print("We already got the {0}-image!".format(site))
            continue
        
        downloadJPEG(obj["file"], path)
        print("The file is downloaded to {0}{1}".format(path, temp_suffix))
        
    
    for filepath in files:
        os.rename("{0}{1}".format(filepath, temp_suffix), filepath)
        print("{0}{1} ==> {0}".format(filepath, temp_suffix))


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1:])
