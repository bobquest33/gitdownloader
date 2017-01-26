# -*- coding: utf-8 -*-
from bottle import Bottle, jinja2_view,post, request
#from git import Repo
from dulwich import porcelain
import json
import threading
import os
import traceback
lock = threading.Lock()
downloadq = dict()

home_app = Bottle()


@home_app.route('/')
@jinja2_view('index.html')
def index():
    return {'get_url': home_app.get_url}

@home_app.post('/download')
def getdownload():
    urlj = json.load(request.body)
    urls = urlj["url"]
    with lock:
        downloadq[urls]=False
    threading.Thread(target=download, kwargs=dict(url=urls)).start()
    return json.dumps({"Submitted":True})

@home_app.post('/status')
def getstatus():
    global downloadq
    urlj = json.load(request.body)
    urls = urlj["url"]
    downloaded_stat = "In Progress"
    with lock:
        try:
            downloaded_stat = downloadq[urls]
        except:
            # NOTE: if you don't do anything here, this thread
            # will consume a single CPU core
            pass        
    return json.dumps({"Completed":downloaded_stat})


def download(url):
    gitrepo = url.rsplit('/', 1)[-1]
    tlocaldir = gitrepo.replace(".git","")
    rootpath =  os.environ.get('DWROOT', ".")
    localdir = os.path.join(rootpath,tlocaldir)
    print localdir
    try:
        with lock:
            downloadq[url]="In Progress"

#        Repo.clone_from(url, localdir)
        porcelain.clone(url, localdir)
        with lock:
            downloadq[url]="Completed"
    except:
        traceback.print_exc()
        with lock:
            downloadq[url]="Failed"
        
