# Import the dependencies.

from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement

Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>" +
        f"/api/v1.0/precipitation<br/>" +
        f"/api/v1.0/stations<br/>" +
        f"/api/v1.0/tobs<br/>" +
        f"/api/v1.0/start<br/>" +
        f"/api/v1.0/start/end<br/>" 
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    #Convert the query results from your precipitation analysis 
    #(i.e. retrieve only the last 12 months of data) 
    #to a dictionary using date as the key and prcp as the value
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prev_date = dt.date(one_year.year, one_year.month, one_year.day)

    query_results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_date, Measurement.prcp != None).\
    order_by(Measurement.date).all()

    precipitation_list = []
    for date, prcp in query_results:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        precipitation_list.append( precipitation_dict)

    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset. 
    query_total = session.query(Station.station).all()
    station = list(np.ravel(query_total))

    return jsonify(station = station)

@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of 
    #the most-active station for the previous year of data.
    
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    temperature_date_results = session.query(Measurement.tobs).\
    filter(Measurement.date >= one_year).\
    filter(Measurement.station == 'USC00519281').\
    order_by(Measurement.tobs).all()

    tobs_temps = list(np.ravel(temperature_date_results))
    

    #Return a JSON list of temperature observations for the previous year.
    return jsonify(tobs_temps = tobs_temps)  
  

@app.route("/api/v1.0/<start>")
def start(start):
    #Return a JSON list of the minimum temperature, 
    #the average temperature, and the maximum temperature for a specified start
    temperature = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.station == 'USC00519281').all()


    #For a specified start, calculate TMIN, TAVG, and TMAX 
    #for all the dates greater than or equal to the start date.
    
    #start_temp = list(np.ravel(temperature))
    #return jsonify(start_temp = start_temp) 



    #for min, max, avg in temperature:
       # temp_dict = {}
        #temp_dict["date"] = date
       # temp_dict["TMIN"] = min
       # temp_dict["TMAX"] = max
       # temp_dict["TAVG"] = avg
       # start_list.append(temp_dict)
    start_list = []
    for min_temp, max_temp, avg_temp in temperature:
        temp_dict = {}
        temp_dict["TMIN"] = min_temp
        temp_dict["TMAX"] = max_temp
        temp_dict["TAVG"] = avg_temp
        start_list.append(temp_dict)
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_to_end(start, end):
    #Return a JSON list of the minimum temperature, the average temperature, 
    #and the maximum temperature for a specified start-end range.

    temperature_start_end = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <=  end).\
    filter(Measurement.station == 'USC00519281').all()

    #For a specified start date and end date, calculate TMIN, TAVG, and TMAX 
    #for the dates from the start date to the end date, inclusive.

    start_end_list = []
    for min, max, avg in temperature_start_end:
        temp_dict = {}
        temp_dict["TMIN"] = min
        temp_dict["TMAX"] = max
        temp_dict["TAVG"] = avg
        start_end_list.append(temp_dict)
    
    return jsonify(start_end_list)


if __name__ == '__main__':
    app.run(debug=True)

