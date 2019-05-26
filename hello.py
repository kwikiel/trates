from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

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
    compound2_dai = round(r.json()[1]["supply"][3]["rate"]*100, 2)
    dydx = round(r.json()[7]["supply"][1]["rate"]*100, 2)
    lever = round(r.json()[3]["supply"][1]["rate"]*100, 2)

   
    return render_template('index.html', c=compound2_dai, d=dydx, l=lever)

@app.route('/charts')
def charts():
    foo = ['x', '2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04', '2013-01-05', '2013-01-06']
    baz = ['Bazzinga', 100, 200, 300, 400, 500, 1337]

    
    return render_template("charts.html", foo=foo, baz=baz)


@app.route("/data")
def data():
    foo = ['x', '20130101', '20130102', '20130103', '20130104', '20130105', '20130106']
    return render_template("data.html", foo=foo)
