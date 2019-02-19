#!/usr/bin/python

import sys
import os
import json
import requests 
import tempfile
import subprocess
import threading
import urllib
import shutil
import toml
from requests.auth import HTTPBasicAuth
from flask import Flask, jsonify, request, abort, make_response
from flask_cors import CORS
from pprint import pprint

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)

cookies = dict(p1="stella", p2="Littlebear01")

def tagit(docker_sha, docker_repo, gitcommit, org, repo):
   print("### Tagging Github Repo ###")  

   tempdir = tempfile.mkdtemp()
   os.chdir(tempdir)
   print(tempdir)

   p = subprocess.Popen('git clone -q git@github.com:' + org + '/' + repo + '.git .', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   for line in p.stdout.readlines():
      print(line)
   p.wait()

   tag = '"' + docker_repo + "@" + docker_sha + '"'
   print(tag)
   p = subprocess.Popen('git tag ' + tag + ' ' + gitcommit , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   for line in p.stdout.readlines():
      print(line)
   p.wait()   

   p = subprocess.Popen('git push origin --tags', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   for line in p.stdout.readlines():
      print(line)
   p.wait() 

   os.chdir('/tmp')
   shutil.rmtree(tempdir)
   return

@app.route('/updatecomponent', methods=['POST'])
def updatecomponent():
 
   print("### Grabbing Docker SHA ###")  
 
   data = request.get_json()
   pprint(data)

   docker_repo = data['docker_url']
#   url = 'https://quay.io/v2/' + data['repository'] + "/manifests/latest"
#
#   headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
#   r = requests.head(url, headers=headers)

   
   docker_sha = data['manifest_digests'][0]
   parts = docker_sha.split('@')
   docker_repo = parts[0]
   docker_sha  = parts[1][7:][:7]

   gitcommit  = data['trigger_metadata']['commit'][:7]
   repo   = data['trigger_metadata']['commit_info']['url']
   org  = repo.split('/')[3]
   repo  = repo.split('/')[4]
   buildid = data['build_id']
   buildurl = data['homepage']
   tag = data['docker_tags'][0]

   print(docker_sha)
   print(docker_repo)
   print(gitcommit)
   print(org)
   print(repo)
   print(tag)

   print("### Creating new component Version ###")  

   url = "https://console.deployhub.com/dmadminweb/API/component/" + repo
   r = requests.get(url, cookies=cookies)
   data = r.json()
   vers = data['result']['versions']

   parent = repo 
   for v in vers:
     if (repo + ";" + tag == v['name']):
       parent = repo + ";" + tag 

   if (repo + ";" + tag != parent):
    url = "https://console.deployhub.com/dmadminweb/API/new/compver/" + parent 
    r = requests.get(url, cookies=cookies)
    data = r.json()

   url = "https://console.deployhub.com/dmadminweb/API/component/" + repo 
   r = requests.get(url, cookies=cookies)
   data = r.json()

   vers = data['result']['versions']

   id = 0
   if (len(vers) >= 1):
    newver = vers[-1]['name']
    id = vers[-1]['id']

   for v in vers:
     if (repo + ";" + tag == v['name']):
       id = v['id'] 

   if (newver == parent):
    print("Updating existing version " + newver)

   url = "https://console.deployhub.com/dmadminweb/UpdateSummaryData?objtype=23&id=" + str(id) + "&change_1=" + urllib.parse.quote(repo + ";" + tag) 
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=image.tag&value=" + urllib.parse.quote(tag)
   r = requests.get(url, cookies=cookies)
 
   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=image.repository&value=" + urllib.parse.quote(docker_repo) 
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=GithubRepo&value=" + urllib.parse.quote(org + "/" + repo) 
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=GitCommit&value=" + urllib.parse.quote(gitcommit) 
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=BuildId&value=" + urllib.parse.quote(buildid) 
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=BuildUrl&value=" + urllib.parse.quote(buildurl) 
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=image.pullPolicy&value=Always"
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=image.version&value=" + urllib.parse.quote(tag) 
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=DockerSha&value=" + urllib.parse.quote(docker_sha) 
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=GitTag&value=" + urllib.parse.quote(tag) 
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=GitDir&value=" + urllib.parse.quote(".") 
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=GitUrl&value=" + urllib.parse.quote("git@github.com:" + org + "/" + repo + ".git")
   r = requests.get(url, cookies=cookies)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?name=Chart&value=" + urllib.parse.quote("chart/" + repo)
   r = requests.get(url, cookies=cookies)

 #  t = threading.Thread(target=tagit, args=[docker_sha, docker_repo, gitcommit, org, repo])  
 #  t.start()
#   tagit(docker_sha, docker_repo, gitcommit, org, repo)

   response_object = []
   return jsonify(response_object)

@app.route('/updateapp', methods=['POST'])
def updateapp():

   feature_ready = []
   url = "https://console.deployhub.com/dmadminweb/API/components?all=y" 
   r = requests.get(url, cookies=cookies)
   data = r.json()
   complist = {}
   for comp in data['result']:
      complist[comp['name']] = comp['id']

   print("### Grabbing featureset.toml ###")  
 
   # checkout bikeworks project for istio config

   tempdir = tempfile.mkdtemp()
   os.chdir(tempdir)
   print(tempdir)

   p = subprocess.Popen('git clone -q git@github.com:DeployHubProject/BikeWorks.git .', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   for line in p.stdout.readlines():
      print(line)
      p.wait()

   with open("featureset.toml","r") as f:
    r = f.read()

#   headers =  {'Accept' : 'application/vnd.github.v3.raw'}
#   url = 'https://raw.githubusercontent.com/DeployHubProject/BikeWorks/master/featureset.toml'
#   r = requests.get(url, headers=headers, auth=('sbtaylor15', 'G0p!1966'))
   data = toml.loads(r)
   pprint(data)
   print("#########")

   Feature2User = data['Feature to Users']
   del data['Feature to Users']

   pprint(complist)

   print("#########")

   for app in data.keys():
#     print(app)
     for feature in data[app].keys():
#     print(feature)
      comps = data[app][feature]
      
      compmatch = []
      for comp in comps.keys():
         compver = comp + ";" + comps[comp]

         if (compver in complist):
            compmatch.append(complist[compver])

      if (len(compmatch) == len(comps) and len(compmatch) > 0):
         print("Components ready App Version for " + app + ";" + feature)
         feature_ready.append(feature)

         url = "https://console.deployhub.com/dmadminweb/API/application/" + urllib.parse.quote(app + ";" + feature)
         r = requests.get(url, cookies=cookies)
         d = r.json()

         vers = d['result']['versions']
         print("Checking")
         pprint(vers)

         parent = "" 
         id = 0
         for v in vers:
            if (app + ";" + feature == v['name']):
                parent = app + ";" + feature 
            if (v['id'] > id):
               id = v['id']    
  
         if (app + ";" + feature != parent):
            print("Creating new app version " + app)
            url = "https://console.deployhub.com/dmadminweb/API/new/appver/" + app 
            r = requests.get(url, cookies=cookies)
            d2 = r.json()

         url = "https://console.deployhub.com/dmadminweb/API/application/" + app 
         r = requests.get(url, cookies=cookies)
         d2 = r.json()

         vers = d2['result']['versions']
         print("Updating")
         pprint(vers)

         id = 0
         for v in vers:
            if (v['id'] > id):
               id = v['id']  

         for v in vers:
            if (app + ";" + feature == v['name']):
               id = v['id'] 

         print("Updating existing version " + str(id))

         url = "https://console.deployhub.com/dmadminweb/UpdateSummaryData?objtype=17&id=" + str(id) + "&change_1=" + urllib.parse.quote(app + ";" + feature) 
         r = requests.get(url, cookies=cookies)

         compvers = d2['result']['components']
         for comp in compvers:
            url = "https://console.deployhub.com/dmadminweb/UpdateAttrs?f=acd&a=" +  str(id) + "&c=" + str(comp['id'])
            r = requests.get(url, cookies=cookies)

         lastid = 0
         ypos = 100
         for compid in compmatch:
            url = "https://console.deployhub.com/dmadminweb/UpdateAttrs?f=acvm&a=" +  str(id) + "&c=" + str(compid) + "&ypos=" + str(ypos) + "&xpos=100"
            r = requests.get(url, cookies=cookies)

            url = "https://console.deployhub.com/dmadminweb/UpdateAttrs?f=cal&a=" +  str(id) + "&fn=" + str(lastid) + "&tn=" + str(compid)
            r = requests.get(url, cookies=cookies)
            lastid = compid
            ypos = ypos + 100

         compmatch = []

         url = "https://console.deployhub.com/dmadminweb/API/environment/" + urllib.parse.quote("GLOBAL.Chasing Horses LLC.BikeWorks.My Pipeline.Development.Dev")
         r = requests.get(url, cookies=cookies)
         d2 = r.json()
         envid = d2['result']['id']

         url = "https://console.deployhub.com/dmadminweb/API/deploy/" +  str(id) + "/" + str(envid)
         r = requests.get(url, cookies=cookies)

   pprint(Feature2User)
   
   for feature in Feature2User:
      if (feature in feature_ready):
         users = Feature2User[feature]
         for user in users:
           print("Setting feature \"" + feature + "\" for user " + user)
           url = "http://bikeworks.gotdns.com/features/" + urllib.parse.quote(feature) + "/" +  urllib.parse.quote(user)
           r = requests.get(url)

   response_object = []
   return jsonify(response_object)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
