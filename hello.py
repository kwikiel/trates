from flask import Flask
from flask import render_template

import requests

app = Flask(__name__)

@app.route('/')
def hello_world():
    headers = {"content-type": "application/json", "x-api-key": "KQUl7wEC9y8UTIU30zR71670L5iKpVl18XFD5Iqd"}

    r = requests.get("https://api.loanscan.io/v1/interest-rates", headers=headers)
    compound2_dai = round(r.json()[1]["borrow"][3]["rate"]*100, 2)
    dydx = round(r.json()[7]["supply"][1]["rate"]*100, 2)
    lever = round(r.json()[3]["supply"][1]["rate"]*100, 2)

   
    return render_template('index.html', c=compound2_dai, d=dydx, l=lever)
