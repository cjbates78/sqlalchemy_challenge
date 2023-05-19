# Import the dependencies.

import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

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

last_12_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)



#################################################
# Flask Routes
#################################################

#Homepage with list of all available routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


#Convert query results from precipitation analysis for the last 12 months to a dictionary return JSON representation
@app.route("/api/v1.0/precipitation")
def precipitation():
    p_scores = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_12_months).\
        group_by(Measurement.date).all()
    
    session.close()

    year_prcp = []
    for date, prcp in p_scores:
       dict = {}
       dict["date"] = date
       dict["prcp"] = prcp
       year_prcp.append(dict)
    
    return jsonify(year_prcp)


#Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    station_info = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()
    return jsonify(station_info)


#Query the dates and temperature observations of the most-active station for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
   temp_data = session.query(Measurement.station, Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= last_12_months).all()
   return jsonify(temp_data)


#Return a JSON list of the min temp, the avg temp, and max temp for a specified start 
@app.route("/api/v1.0/<start>")
def start_date(date):
    single_day_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date == date).all()
    return jsonify(single_day_temp)

##Return a JSON list of the min temp, the avg temp, and max temp for a specified start-end range
@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):
   date_range_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
         filter(Measurement.date >= start).\
         filter(Measurement.date <= end).all()
   return(date_range_temp)

if __name__ == '__main__':
   app.run(debug=True)