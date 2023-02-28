from api.cline import Cline
from flask import Flask, request, render_template, redirect
import datetime as dt
import pytz, argparse
import api.keys as keys
import time
from api.utils import *
import json
import requests
import os

app         = Flask(__name__)
url         = os.environ.get('URL')

if (url):
    api         = Cline(url=url)
else:
    api         = Cline(url="https://tas.blockchain-servers.world")

account     = os.environ.get('ACCOUNT')
privatekey  = os.environ.get('PRIVATE_KEY')

def create(mod, trans_id, text) :
    action = mod
    
    action_data = {
        "id": trans_id, 
        "user": account,
        "data": text
    }

    payload = {
        "account": account,
        "name": action,
        "authorization": [{
            "actor": account,
            "permission": "owner",
        }]
    }

    # Converting payload to binary
    data = api.abi_json_to_bin(account, action, action_data)
    payload['data'] = data['binargs']

    # final transaction formed
    trx = {"actions": [payload]}
    trx['expiration'] = str((dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

    key = keys.INRKey(privatekey)
    
    resp = api.push_transaction(trx, key, broadcast=True)
    result = json.dumps(resp, indent = 4) 

    return result


def read(mod, trans_id):
    action = mod
    
    action_data = {
        "id": trans_id
    }

    payload = {
        "account": account,
        "name": action,
        "authorization": [{
            "actor": account,
            "permission": "owner",
        }]
    }

    # Converting payload to binary
    data = api.abi_json_to_bin(account, action, action_data)
    payload['data'] = data['binargs']

    # final transaction formed
    trx = {"actions": [payload]}
    trx['expiration'] = str((dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

    key = keys.INRKey(privatekey)
    
    resp = api.push_transaction(trx, key, broadcast=True)
    result = json.dumps(resp, indent = 4) 

    return result


@app.route("/", methods=["POST", "GET"])
def view_index():
    if request.method == "POST":
        if (request.form['option'] == '1' or request.form['option'] == '3'):
            if(request.form['option'] == '1'):
                name = 'create'
            else:
                name = 'update'
            
            try:
                dataCreate = create(name, request.form['id'], request.form['text'])
                return render_template("index.html", notes=dataCreate)
            except Exception as e:
                return render_template("index.html", notes=str(e))
        elif (request.form['option'] == '2' or request.form['option'] == '4'):
            if(request.form['option'] == '2'):
                name = 'read'
            else:
                name = 'destroy'
            
            try:
                dataRead = read(name, request.form['id'])
                return render_template("index.html", notes=dataRead)
            except Exception as e:
                return render_template("index.html", notes=str(e))
            
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
