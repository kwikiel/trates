#!/usr/bin/python

from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import json
import requests
import datetime
import psycopg2

from sqlalchemy import create_engine

app = Flask(__name__)
#TODO move this key to ENV 

app.config['SQLALCHEMY_DATABASE_URI']='postgres://mkiizzsexpqbeb:853ead1f17f3dc191da7a0149c247920e39f8e0f7d89402dce983ae2af478fe1@ec2-54-235-114-242.compute-1.amazonaws.com:5432/d553bngfbfj4ov'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(140))

    def __repr__(self):
        return "<#{id} {date} {name}:  {value}>".format(id=self.id, date=self.date, name=self.name,value=self.value)

def get_supply_rates(provider, symbol, data):
    for i in data:
        try:
            if(i["provider"]==provider):
                for k in(i["supply"]):
                    if(k["symbol"]==symbol):
                        return k["rate"]
        except: 
            print("Could not obtain the rate")

def raw_sql(query):
    with engine.connect() as con:
        rs = con.execute(query)
    result = []
    for r in rs:
        result.append(r)
    return result 

@app.route('/')
def hello_world():
    r = requests.get("https://ethgasstation.info/json/ethgasAPI.json")

    safe_low_price = float(int(float(r.json()["safeLowWait"])))/10.0
    rates = raw_sql('SELECT name,value FROM data_point \
                      ORDER BY date DESC, value DESC \
                      LIMIT (SELECT COUNT(DISTINCT name) FROM data_point)')
   
    return render_template('index.html',rates=rates, safe_low_price = safe_low_price)

@app.route('/charts')
def charts():
    
    # This is for data points
    kek = DataPoint.query.filter(DataPoint.name=="Compound")
    dates = []
    dvalues = []
    for k in kek:
        dates.append(k.date.strftime('%Y-%m-%d'))
        dvalues.append(k.value)
    d = ["x"] + sorted(dates)
    v = ["Dharma Lever"] + dvalues
    
    kek = DataPoint.query.filter(DataPoint.name=="Compound")
    dates = []
    dvalues = []
    for k in kek:
        dates.append(k.date.strftime('%Y-%m-%d'))
        dvalues.append(k.value)
    c = ["Compound"] + dvalues
    
    kek = DataPoint.query.filter(DataPoint.name=="dYdX")
    dates = []
    dvalues = []
    for k in kek:
        dates.append(k.date.strftime('%Y-%m-%d'))
        dvalues.append(k.value)
    dx = ["dYdX"] + dvalues



    kek = DataPoint.query.filter(DataPoint.name=="Dipor")
    dates = []
    dvalues = []
    for k in kek:
        dates.append(k.date.strftime('%Y-%m-%d'))
        dvalues.append(k.value)
    dipor = ["Dipor"] + dvalues
    
    return render_template("charts.html", xdates=d, dharma_values=v, compound_values=c, dydx_values=dx, dipor_values=dipor)


@app.route("/process")
def data():
    headers = {"content-type": "application/json", "x-api-key":"KQUl7wEC9y8UTIU30zR71670L5iKpVl18XFD5Iqd"}

    r = requests.get("https://api.loanscan.io/v1/interest-rates", headers=headers)
    compound2_dai = round(100*get_supply_rates("CompoundV2", "DAI", r.json()),2)
    dydx = round(100*get_supply_rates("dYdX", "DAI", r.json()),2)
    #lever = round(100*get_supply_rates("Lever", "DAI", r.json()),2)
    
    c = DataPoint(date=datetime.datetime.now(), value=compound2_dai, name="Compound")
    d = DataPoint(date=datetime.datetime.now(), value=dydx, name="dYdX")
    #e = DataPoint(date=datetime.datetime.now(), value=lever, name="Dharma Lever")


    dipor = round(((compound2_dai+dydx)/2.0),2)

    dipor2 = DataPoint(date=datetime.datetime.now(), value=dipor, name="Dipor")
    
    last = DataPoint.query.filter(DataPoint.name=="Compound").order_by(DataPoint.date.desc())[0].date
    if(datetime.datetime.now().strftime('%Y-%m-%d')==last.strftime('%Y-%m-%d')):
        db.session.rollback()
        return json.dumps({'Already existing':True}), 200, {'ContentType':'application/json'}
    else:
        db.session.add(c)
        db.session.add(d)

        db.session.add(dipor2)
        db.session.commit()
 
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

import os 


if __name__=='__main__':
    app.run(host='0.0.0.0',
            port=int(os.getenv('PORT',"5000")),
            debug=os.getenv('DEBUG', False)
                )
