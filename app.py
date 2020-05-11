from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
import json
import corona
import csv
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "sfdhsdklfjwerjfcksldfjkdlsfjekl"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICTIONS"] = False

raw_data = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
)
selected = 'False'
# test

db = SQLAlchemy(app)
def dump_data(state, county, file, x, y, json_file):
    corona.get_data(x, y, file, state, county)
    data = {
        'x': x,
        'y': y,
        'state': state,
        'county': county
    }
    with open(json_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    ip = db.Column("ip", db.String(100))
    state = db.Column("state", db.String(100))
    county = db.Column("county", db.String(100))


    def __init__(self, ip, state, county):
        self.ip = ip
        self.state = state
        self.county = county


@app.route('/', methods=["POST", "GET"])
def home():
    ''''global selected
    if not selected:
        file = corona.get_file(raw_data)
        states = corona.get_states(file)
        keys = []
        values = []
        corona.create_dict(keys, values, file, raw_data)
        return render_template("index.html", states=states, len=len(states), len2=len(keys), keys=keys, values=values, seleceted=selected)
    else:'''

    global selected
    if request.method == "POST":
        state = request.form['state']
        county = request.form['county']
        if state == 'default' or county == 'county':
            state = 'California'
            county = 'San Francisco'
        file = corona.get_file(raw_data)
        x = []
        y = []
        dump_data(state, county, file, x, y, 'data.json')

        corona.get_data(x, y, file, state, county)
        ip_addr = request.remote_addr
        found_user = users.query.filter_by(ip=ip_addr).first()
        if found_user:
            found_user.state = state
            found_user.county = county
            db.session.commit()
        else:
            user = users(ip_addr, state, county)
            db.session.add(user)
            db.session.commit()
            
        file = corona.get_file(raw_data)
        states = corona.get_states(file)
        keys = []
        values = []
        corona.create_dict(keys, values, file, raw_data)
        print(selected)
        return render_template("index.html", states=states, len=len(states), len2=len(keys), keys=keys, values=values, selected='True')
    else:
        ip_addr = request.remote_addr
        file = corona.get_file(raw_data)
        states = corona.get_states(file)
        keys = []
        values = []
        corona.create_dict(keys, values, file, raw_data)
        file = corona.get_file(raw_data)
        x = []
        y = []    
        data = json.load(open('data.json'))
        jtopy = json.dumps(data) 
        dict_json = json.loads(jtopy) 
        state = dict_json['state']
        county = dict_json['county']
        found_user = users.query.filter_by(ip=ip_addr).first()
        if found_user:
            found_user.state = state
            found_user.county = county
            db.session.commit()
        else:
            user = users(ip_addr, state, county)
            db.session.add(user)
            db.session.commit()
        dump_data(state, county, file, x, y, 'data.json')
        file = corona.get_file(raw_data)
        return render_template("index.html", states=states, len=len(states), len2=len(keys), keys=keys, values=values, selected=selected) 

@app.route('/send', methods=["POST", "GET"])
def send():
    ip_addr = request.remote_addr
    if request.method == "POST":
        return redirect(url_for("home"))
    data = json.load(open('data.json'))
    jtopy = json.dumps(data) 
    dict_json = json.loads(jtopy)
    print(jsonify(dict_json))
    x = dict_json['x']
    y = dict_json['y']
    found_user = users.query.filter_by(ip=ip_addr).first()
    state = found_user.state
    county = found_user.county
    file = corona.get_file(raw_data)
    x = []
    y = []
    corona.get_data(x,y, file, state, county)
    return render_template("graph.html", state=state, county=county, json_data=dict_json, x=x, y=y)

@app.route('/counties', methods=['POST', 'GET'])
def counties():
    counties = []
    if request.method == "POST":
        if request.form['submit'] == "home":
            return redirect(url_for("home"))
        file = corona.get_file(raw_data)
        real_state = corona.check_state(request.form['state'], file)
        if not real_state:
            flash("Either your state was not found")
            return redirect(url_for("counties"))

        file = corona.get_file(raw_data)
        counties = corona.get_counties(request.form['state'], file)
        return render_template("counties.html", len=len(counties), counties=counties, state=request.form['state'])
    else:
        return render_template("counties.html", len=len(counties), counties=counties, state="")

@app.route('/graph')
def graph():
    data = json.load(open('data.json'))
    jtopy = json.dumps(data) 
    dict_json = json.loads(jtopy) 

    file = corona.get_file(raw_data)
    real_state = corona.check_state(dict_json['state'], file)
    file = corona.get_file(raw_data)
    real_county = corona.check_county(dict_json['state'], dict_json['county'], file)

    if not real_state or not real_county:
        flash("Either your state or county were not found")
        return redirect(url_for("home"))

    #return render_template("graph.html", state=dict_json['state'], county=dict_json['county']), 
    return redirect(url_for("send"))

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0')