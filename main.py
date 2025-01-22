from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from api import WeatherAPI
from llama import Llama
import os
import sqlite3
from datetime import date, timedelta, datetime
import json


app = Flask(__name__)
secret_key = os.urandom(12)
app.secret_key = secret_key

@app.route("/createDB", methods=["GET", "POST"])
def createDB():
    return render_template("/createDb.html")


def create_table():
    db_connection = sqlite3.connect("weather.db")
    cursor = db_connection.cursor()

    create_table = """
    CREATE TABLE IF NOT EXISTS weather (
    location VARCHAR(20),
    date DATE,
    temp FLOAT );
    """

    cursor.execute(create_table)

@app.route('/insertDB', methods=["GET", "POST"])
def insertDB():
    create_table()
    today = date.today()
    days = request.form['daysTo']
    try:
        date2 = date(int(days[:4]), int(days[5:7]), int(days[8:]))
    except: 
        session['error'] = "Not valid date"
        return redirect(url_for('redirectToHome'))
    
    delta = date2 - today
    days = delta.days
    
    userCity = request.form['location2']
    
    api_object = WeatherAPI(userCity, days)
    if api_object.invalid == True:
        session['error'] = "Invalid Location"
        return redirect(url_for('redirectToHome'))
    
    db_connection = sqlite3.connect("weather.db")
    cursor = db_connection.cursor()
    temp_list = api_object.forecast()

    insert_data = """
    INSERT INTO weather (location, date, temp)
    VALUES (?, ?, ?);
    """
    try:
        for data in temp_list:
            temp = data['maxTemp']  
            dates = data['dates']
            cursor.execute(insert_data, (userCity, dates, temp)) 
        db_connection.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        session['error'] = "Database error"
        return redirect(url_for('redirectToHome'))
    finally:
        db_connection.close()
        return redirect(url_for('readDB'))

@app.route('/readDB', methods=["GET", "POST"])
def readDB():
    db_connection = sqlite3.connect("weather.db")
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM weather")
    read_data = cursor.fetchall()
    data_list = []
    for i in read_data:
        data_list.append(i)
    list_length = len(data_list)
    return render_template('readDB.html', data_list=data_list, list_length=list_length)

@app.route('/updateDB1', methods=["GET", "POST"])
def updateDB1():
    return render_template('updateDB.html')

@app.route('/updateDB', methods=["GET", "POST"])
def updateDB():
    db_connection = sqlite3.connect("weather.db")
    cursor = db_connection.cursor()
    dates = request.form['date3']
    location = request.form['location4']
    api_object = WeatherAPI(location, 5)
    if api_object.invalid == True:
        session['error'] = "Invalid Location"
        return redirect(url_for('redirectToHome'))
    temp = request.form['temp3']
    try:
        temp = float(temp)
    except:
        session['error'] = "Not valid temp"
        return redirect(url_for('redirectToHome'))
    try:
        date2 = date(int(dates[:4]), int(dates[5:7]), int(dates[8:]))
    except: 
        session['error'] = "Not valid date"
        return redirect(url_for('redirectToHome'))
    update_query = """
    UPDATE weather SET temp = ? WHERE location = ? AND date = ?;
    """
    try:
        cursor.execute(update_query,(temp, location, dates))
    except sqlite3.Error as e:
        print(e)
        session['error'] = "Unsuccessful, check parameters"
        return redirect(url_for('redirectToHome'))
    db_connection.commit()
    db_connection.close()

    return redirect(url_for('redirectToHome'))

    
@app.route("/deleteDB1", methods=["GET", "POST"])
def deleteDB1():
    return render_template('deleteDB.html')

@app.route('/deleteDB', methods=["GET", "POST"])
def deleteDB():
    
    db_connection = sqlite3.connect('weather.db')
    location = request.form['location3']
    dates = request.form['date2']
    
    try:
        date2 = date(int(dates[:4]), int(dates[5:7]), int(dates[8:]))
    except: 
        session['error'] = "Not valid date"
        return redirect(url_for('redirectToHome'))
    
    cursor = db_connection.cursor()
    delete_query = """
    DELETE FROM weather WHERE location = ? AND date = ?
    """
    cursor.execute(delete_query,(location, dates))
    db_connection.commit()
    db_connection.close()
    return redirect(url_for('redirectToHome'))

@app.route('/', methods=['GET', 'POST'])
def redirectToHome():
    message = None
    if "error" in session:
        message = session['error']
        
    return render_template('index.html', message=message)

@app.route('/results', methods=['POST', 'GET'])
def results():
    userCity = request.form['userCity']
    api_object = WeatherAPI(userCity, 5)
    if api_object.invalid == True:
        session['error'] = "Invalid Location"
        return redirect(url_for('redirectToHome'))
    else:
        forecast_data = api_object.forecast()
        llama_obj = Llama(forecast_data=forecast_data)
        forecast = llama_obj.define_model()['content']
        if '**' in forecast:
            forecast = forecast.replace("**", " ")
    return render_template('results.html', forecast=forecast, api_object=forecast_data )

@app.route('/export', methods=["GET", "POST"])
def export():
    import sqlite3
    
    db_connection = sqlite3.connect('weather.db')
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM weather")  
    rows = cursor.fetchall()

    column_names = [description[0] for description in cursor.description]

    data = []
    for row in rows:
        row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
        data.append(row_dict)
        
    with open('data_export.json', 'w') as exportFile:
        json.dump(data, exportFile, indent=2)

    db_connection.close()
    json_file = 'data_export.json'  
    return send_file(json_file, mimetype='application/json', as_attachment=True)

@app.route('/info', methods=["GET", "POST"])
def info():
    return render_template("info.html")
        
if __name__ == "__main__":
    app.run(debug=True)
