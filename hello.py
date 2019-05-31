from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import json
import requests
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgres://mkiizzsexpqbeb:853ead1f17f3dc191da7a0149c247920e39f8e0f7d89402dce983ae2af478fe1@ec2-54-235-114-242.compute-1.amazonaws.com:5432/d553bngfbfj4ov'

db = SQLAlchemy(app)

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(140))

    def __repr__(self):
        return "<#{id} {date} {name}:  {value}>".format(id=self.id, date=self.date, name=self.name,value=self.value)



@app.route('/')
def hello_world():
    headers = {"content-type": "application/json", "x-api-key": "KQUl7wEC9y8UTIU30zR71670L5iKpVl18XFD5Iqd"}

    r = requests.get("https://api.loanscan.io/v1/interest-rates", headers=headers)
    compound2_dai = round(r.json()[1]["borrow"][3]["rate"]*100, 2)
    dydx = round(r.json()[7]["supply"][1]["rate"]*100, 2)
    lever = round(r.json()[3]["supply"][1]["rate"]*100, 2)

   
    return render_template('index.html', c=compound2_dai, d=dydx, l=lever)

@app.route('/charts')
def charts():
    
    kek = DataPoint.query.filter(DataPoint.name=="Dharma Lever")
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
    
    return render_template("charts.html", xdates=d, dharma_values=v, compound_values=c, dydx_values=dx)


@app.route("/process")
def data():
    headers = {"content-type": "application/json", "x-api-key":"KQUl7wEC9y8UTIU30zR71670L5iKpVl18XFD5Iqd"}

    r = requests.get("https://api.loanscan.io/v1/interest-rates", headers=headers)
    compound2_dai = round(r.json()[1]["borrow"][3]["rate"]*100, 2)
    dydx = round(r.json()[7]["supply"][1]["rate"]*100, 2)
    lever = round(r.json()[3]["supply"][1]["rate"]*100, 2)
    
    c = DataPoint(date=datetime.datetime.now(), value=compound2_dai, name="Compound")
    db.session.add(c)
    d = DataPoint(date=datetime.datetime.now(), value=dydx, name="dYdX")
    db.session.add(d)
    e = DataPoint(date=datetime.datetime.now(), value=lever, name="Dharma Lever")
    db.session.add(e)
    db.session.commit()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

            
                  
                 

