#!/usr/bin/python3
#http://hyperion.nvf.io/latest-image/f437c149-5311-41f1-bddc-60369e69a000

APIURL = dict()

APIURL["dat"] = "https://hyperion.nvf.io/latest-image/f967a20a-7b8b-4afe-b9a5-8b45285627a9/?format=json"
APIURL["ict"] = "https://hyperion.nvf.io/latest-image/57068cd1-60ab-4545-915a-e568ee030fa5/?format=json"
APIURL["tri"] = "https://hyperion.nvf.io/latest-image/256035cb-c972-4e47-9eb9-def5dfc0f08a/?format=json"
APIURL["lem"] = "https://hyperion.nvf.io/latest-image/aa389088-02c6-4849-8785-da19683c50c4/?format=json"

files = list()
base_dir = "/tmp/rsyncing"
temp_suffix = ".iowait"

import os, requests
from datetime import datetime as dt
from sys import argv

def getJSONObject(url):
    return requests.get(url, verify=False).json()

def getDate(rfc3339):
    return dt.strptime(rfc3339, '%Y-%m-%dT%H:%M:%SZ')

def downloadJPEG(url, dest_path):
    r = requests.get(url, stream=False, verify=False)
    f = open("{0}{1}".format(dest_path, temp_suffix), "wb")
    f.write(r.content)
    r.close()
    f.close()
    files.append(dest_path)

def checkAndCreateDir(dest_dir):
    if not (os.path.isdir(dest_dir)):
        os.makedirs(dest_dir)

def main(argv):
    print("Lemminbot v0.8-tbo")
    print("Downloading to {}".format(base_dir))
    #do this for all api endpoints
    for site in APIURL:
        #get the json object from API request
        try:
            obj = getJSONObject(APIURL[site])
        except ValueError:
            print("The {0} API endpoint is dead.".format(site))
            continue
        #parse the timestamp
        ts = getDate(obj["timestamp"])
        #directory and file name
        dest_dir = "{0}/{1:02}{2:02}{3:02}/{4}".format(base_dir, ts.year, ts.month, ts.day, site)
        dest_filename = "{0}-{1}.jpg".format(site, obj["timestamp"].replace(":", "-"))
        #check the destination dir, if it doesn't exist, just create it
        path = "{0}/{1}".format(dest_dir, dest_filename)
        checkAndCreateDir(dest_dir)

        #be verbose about status to find problems
        if os.path.exists(path):
            print("We already got the {0}-image!".format(site))
            continue
        elif os.path.exists("{0}{1}".format(path, temp_suffix)):
            print("Temporary file found, skipping {0}".format(site))
            continue
        else:
            downloadJPEG(obj["file"], path)
            print("The file is downloaded to {0}{1}".format(path, temp_suffix))

    #done, commit changes to disk before next run
    for filepath in files:
        os.rename("{0}{1}".format(filepath, temp_suffix), filepath)
        print("{0}{1} ==> {0}".format(filepath, temp_suffix))

if __name__ == "__main__":
    # execute only if run as a script
    main(argv[1:])
