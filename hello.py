from flask import Flask, request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask import jsonify

import json
import requests
import datetime
import psycopg2
import os
from sqlalchemy import create_engine
# cache setup
from flask_caching import Cache

# This trick is to render charts without X server


platforms = ['Nuo', 'CoinList','Compound','CompoundV2',
             'MakerDao',
             'Poloniex',
             'Bitfinex',
             'Celsius',
             'dYdX',
             'Nexo',
             'BlockFi',
             'Wealthfront',
             'Betterment',
             'SoFi',
             'CryptoCom',
             'Marcus',
             'Soda',
             'Coinbase',
             'SaltLending',
             'PersonalCapital',
             'Fulcrum',
             'Linen',
             'Dharma',
             'Lendingblock',
             'Hodlonaut',
             'InstaDapp',
             'DeFiSaver',
             'Zerion',
             'Argent',
             'AaveStable'
             ]

stablecoins = ["DAI", "TUSD", "USDT", "USDC", "GUSD", "USD", "SAI", "BUSD", "USDT"]

app = Flask(__name__)

def get_supply_rates(provider, symbol, data):
    for i in data:
        try:
            if(i["provider"] == provider):
                for k in(i["supply"]):
                    if(k["symbol"] == symbol):
                        return k["rate"]
        except:
            print("Could not obtain the rate")





@app.route('/')
def index():
    headers = {"content-type": "application/json",
               "x-api-key": "KQUl7wEC9y8UTIU30zR71670L5iKpVl18XFD5Iqd"}
    r = requests.get(
        "https://api.loanscan.io/v1/interest-rates", headers=headers)
    rates = r.json()

    trackato = []
    for p in platforms:
        for s in stablecoins:
            if get_supply_rates(p, str(s), rates) != None:
                trackato.append([p, s, get_supply_rates(p, str(s), rates)])

    #TODO get it from the database instead 
    trackato.append(["RealT", "8342 Schaefer Highway, Detroit, MI 48228", 0.1259, "https://realt.co/?ref=spike"])
    trackato.append(["RealT", "10024-28 Appoline St, Detroit, MI 48227", 0.1182, "https://realt.co/?ref=spike"])

    trackato = sorted(trackato, key=lambda x: x[2], reverse=True)

    return render_template('index.html', trackato=trackato)

@app.route('/api')
def api_main():
    headers = {"content-type": "application/json",
               "x-api-key": "KQUl7wEC9y8UTIU30zR71670L5iKpVl18XFD5Iqd"}
    r = requests.get(
        "https://api.loanscan.io/v1/interest-rates", headers=headers)
    rates = r.json()

    trackato = []
    for p in platforms:
        for s in stablecoins:
            if get_supply_rates(p, str(s), rates) != None:
                trackato.append([p, s, get_supply_rates(p, str(s), rates)])

    #TODO get it from the database instead 
    trackato.append(["RealT", "8342 Schaefer Highway, Detroit, MI 48228", 0.1259, "https://realt.co/?ref=spike"])
    trackato.append(["RealT", "10024-28 Appoline St, Detroit, MI 48227", 0.1182, "https://realt.co/?ref=spike"])

    trackato = sorted(trackato, key=lambda x: x[2], reverse=True)

    beauty = {}
    for t in trackato:
        print(t[0],t[1],t[2])
        beauty[t[0]+"#"+t[1]] = t[2]
    return jsonify([beauty])

if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=int(os.getenv('PORT', "5000")),
            debug=os.getenv('DEBUG', False))
