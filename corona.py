import csv
import requests


def get_file(url):
    return csv.DictReader(requests.get(url).iter_lines(decode_unicode=True))


def get_data(x, y, file, state, county):
    for row in file:
        if row['Province_State'] == state and row['Admin2'] == county:
            i = 0
            for _, value in row.items():
                i += 1
                if i >= 12:
                    x.append(i - 11)
                    y.append(int(value))
            break


def print_counties(state, file):
    for row in file:
        if row['Province_State'] == state:
            print(row['Admin2'])


def get_counties(state, file):
    counties = []
    for row in file:
        if row['Province_State'] == state:
            counties.append(row['Admin2'])
    return counties


def check_county(state, county, file):
    for row in file:
        if row['Admin2'] == county:
            return True
    return False


def check_state(state, file):
    for row in file:
        if row['Province_State'] == state:
            return True
    return False

def get_states(file):
    states = []
    for row in file:
        if row['Province_State'] not in states:
            states.append(row['Province_State'])
    return states

def create_dict(keys, values, file, raw_data):
    file = get_file(raw_data)
    for row in file:
        keys.append(row['Province_State'])
        values.append(row['Admin2'])