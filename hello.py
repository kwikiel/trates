import matplotlib.pyplot as plt
from flask import Flask, request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import json
import requests
import datetime
import psycopg2
import os
from sqlalchemy import create_engine
# cache setup
from flask_caching import Cache

# This trick is to render charts without X server
import matplotlib as mpl
mpl.use('Agg')

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 50
}

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
             'Argent']

stablecoins = ["DAI", "TUSD", "USDT", "USDC", "GUSD", "USD", "SAI"]

app = Flask(__name__)

app.config.from_mapping(config)

cache = Cache(app)

# Environment variables secret
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["LOANSCAN_API"] = os.getenv("LOANSCAN_API")
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)
migrate = Migrate(app, db)



class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(140))

    def __repr__(self):
        return "<#{id} {date} {name}:  {value}>".format(id=self.id, date=self.date, name=self.name, value=self.value)

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(280))

    def __repr__(self):
        return "<{id} {comment}>".format(id=self.id, comment=self.comment)


def get_supply_rates(provider, symbol, data):
    for i in data:
        try:
            if(i["provider"] == provider):
                for k in(i["supply"]):
                    if(k["symbol"] == symbol):
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
def index():
    headers = {"content-type": "application/json",
               "x-api-key": app.config["LOANSCAN_API"]}
    r = requests.get(
        "https://api.loanscan.io/v1/interest-rates", headers=headers)
    rates = r.json()

    trackato = []
    for p in platforms:
        for s in stablecoins:
            if get_supply_rates(p, str(s), rates) != None:
                trackato.append([p, s, get_supply_rates(p, str(s), rates)])

    #TODO get it from the database instead 
    trackato.append(["RealT", "Marlowe St, Detroit", 0.139])

    trackato = sorted(trackato, key=lambda x: x[2], reverse=True)

    return render_template('index.html', trackato=trackato)

@app.route('/result', methods=["GET", "POST"])
def display():
    if request.method == 'POST':
        result = request.form["suggestion"]
        s = Suggestion(comment=result)
        db.session.add(s)
        db.session.commit()
        comments = Suggestion.query.all()
        return render_template("result.html",result = comments)


@app.route('/charts')
@cache.cached(timeout=50)
def charts():

    # This is for data points
    kek = DataPoint.query.order_by(DataPoint.id).filter(
        DataPoint.name == "Compound")
    dates = []
    dvalues = []
    for k in kek:
        dates.append(k.date.strftime('%Y-%m-%d'))
        dvalues.append(k.value)
    d = ["x"] + (dates)

    kek = DataPoint.query.order_by(DataPoint.id).filter(
        DataPoint.name == "Compound")
    dates = []
    dvalues = []
    for k in kek:
        dates.append(k.date.strftime('%Y-%m-%d'))
        dvalues.append(k.value)
    c = ["Compound Supply rate (%)"] + dvalues

    return render_template("charts.html", xdates=d,  compound_values=c)

# Key above isn't a secret - it's just verification for load test
@app.route("/loaderio-b8661169a16b9c814aaf0ac212fe462f.html")
def check_token():
    return "loaderio-b8661169a16b9c814aaf0ac212fe462f"


@app.route("/process_gas")
def data_gas():
    r = requests.get("https://ethgasstation.info/json/ethgasAPI.json")
    gas_fee = r.json()["safeLow"]/10

    d = DataPoint(date=datetime.datetime.now(), value=gas_fee, name="safeLow")
    db.session.add(d)
    db.session.commit()

    return "200"
@app.route("/gas_chart")
def create_gas_chart():
    fbq = DataPoint.query.filter(
        DataPoint.name == "safeLow").order_by(DataPoint.date)
    y = []
    x = []
    for f in fbq:
        x.append(f.id)
        y.append(f.value)
    plt.plot(x, y)
    plt.ylabel('Gas Price (Gwei)')
    plt.xticks(rotation=45)
    plt.title("Gas price history ( 10 minute ticks)")
    plt.axhline(y=22, linestyle='-', color='red')
    plt.axhline(y=10, linestyle='-', color='blue')
    plt.axhline(y=3.5, linestyle='-', color='green')
    plt.legend(['Safe Low History', 'Fast', 'Standard', 'Safe Low'])
    plt.savefig('static/gas.png', dpi=300, bbox_inches='tight')
    return "ok"

@app.route("/process")
def data():
    headers = {"content-type": "application/json",
               "x-api-key": app.config["LOANSCAN_API"]}

    r = requests.get(
        "https://api.loanscan.io/v1/interest-rates", headers=headers)
    compound2_dai = round(
        100*get_supply_rates("CompoundV2", "DAI", r.json()), 2)
    dydx = round(100*get_supply_rates("dYdX", "DAI", r.json()), 2)
    #lever = round(100*get_supply_rates("Lever", "DAI", r.json()),2)

    c = DataPoint(date=datetime.datetime.now(),
                  value=compound2_dai, name="Compound")
    d = DataPoint(date=datetime.datetime.now(), value=dydx, name="dYdX")
    #e = DataPoint(date=datetime.datetime.now(), value=lever, name="Dharma Lever")

    dipor = round(((compound2_dai+dydx)/2.0), 2)

    dipor2 = DataPoint(date=datetime.datetime.now(), value=dipor, name="Dipor")

    last = DataPoint.query.filter(DataPoint.name == "Compound").order_by(
        DataPoint.date.desc())[0].date
    if(datetime.datetime.now().strftime('%Y-%m-%d') == last.strftime('%Y-%m-%d')):
        db.session.rollback()
        return json.dumps({'Already existing': True}), 200, {'ContentType': 'application/json'}
    else:
        db.session.add(c)
        db.session.add(d)

        db.session.add(dipor2)
        db.session.commit()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=int(os.getenv('PORT', "5000")),
            debug=os.getenv('DEBUG', False),
            threaded=True)
