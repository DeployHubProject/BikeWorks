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
from flask import Flask, jsonify, request, abort, make_response
from flask_cors import CORS
from pprint import pprint

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)

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
   docker_sha  = parts[1][7:][:13]

   gitcommit  = data['trigger_metadata']['commit']
   repo   = data['trigger_metadata']['commit_info']['url']
   org  = repo.split('/')[3]
   repo  = repo.split('/')[4]
   buildid = data['build_id']

   print(docker_sha)
   print(docker_repo)
   print(gitcommit)
   print(org)
   print(repo)

   print("### Creating new component Version ###")  

   url = "https://console.deployhub.com/dmadminweb/API/component/" + repo + "?user=stella&pass=Littlebear01"
   r = requests.get(url)
   data = r.json()
   vers = data['result']['versions']

   if (len(vers) >= 1):
    parent = vers[-1]['name']
   else:
    parent = repo 
   
   url = "https://console.deployhub.com/dmadminweb/API/new/compver/" + parent + "?user=stella&pass=Littlebear01"
   r = requests.get(url)
   data = r.json()
   pprint(data)

   url = "https://console.deployhub.com/dmadminweb/API/component/" + repo + "?user=stella&pass=Littlebear01"
   r = requests.get(url)
   data = r.json()

   vers = data['result']['versions']
   pprint(vers)
   print(len(vers))
   id = 0
   if (len(vers) >= 1):
    newver = vers[-1]['name']
    id = vers[-1]['id']
   else:
    newver = repo 

   pprint(newver)
   pprint(parent)
   if (newver == parent):
    print("ERROR: Creating new version")
    return

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?user=stella&pass=Littlebear01&name=DockerSha&value=" + urllib.parse.quote(docker_sha[:13])
   r = requests.get(url)
 
   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?user=stella&pass=Littlebear01&name=DockerRepo&value=" + urllib.parse.quote(docker_repo) 
   r = requests.get(url)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?user=stella&pass=Littlebear01&name=GithubRepo&value=" + urllib.parse.quote(org + "/" + repo) 
   r = requests.get(url)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?user=stella&pass=Littlebear01&name=GitCommit&value=" + urllib.parse.quote(gitcommit) 
   r = requests.get(url)

   url = "https://console.deployhub.com/dmadminweb/API/setvar/component/" + str(id) + "?user=stella&pass=Littlebear01&name=BuildId&value=" + urllib.parse.quote(buildid) 
   r = requests.get(url)

   t = threading.Thread(target=tagit, args=[docker_sha, docker_repo, gitcommit, org, repo])  
   t.start()
#   tagit(docker_sha, docker_repo, gitcommit, org, repo)

   response_object = []
   return jsonify(response_object)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
