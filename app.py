from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
import json
import corona
import csv
import requests

app = Flask(__name__)
app.secret_key = "sfdhsdklfjwerjfcksldfjkdlsfjekl"
raw_data = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
)

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



@app.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":
        if request.form['submit'] == 'county':
            return redirect(url_for("counties"))
        state = request.form['state']
        county = request.form['county']
        print(state, county)
        file = corona.get_file(raw_data)
        x = []
        y = []
        dump_data(state, county, file, x, y, 'data.json')
        return redirect(url_for("graph"))
    else:
        file = corona.get_file(raw_data)
        states = corona.get_states(file)
        state_counties = corona.create_dict(states, file, raw_data)
        print(len(state_counties))
        return render_template("index.html", states=states, len=len(states), state_counties=state_counties)

@app.route('/send', methods=["POST", "GET"])
def send():
    if request.method == "POST":
        return redirect(url_for("home"))
    data = json.load(open('data.json'))
    jtopy = json.dumps(data) 
    dict_json = json.loads(jtopy)
    print(jsonify(dict_json))
    x = dict_json['x']
    y = dict_json['y']
    return render_template("graph.html", state=dict_json['state'], county=dict_json['county'], json_data=dict_json, x=x, y=y)

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
    app.run(debug=True)