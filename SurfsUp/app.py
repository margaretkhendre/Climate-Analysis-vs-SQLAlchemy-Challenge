# Import the dependencies.
from flask import Flask, jsonify 
import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# create engine that points to hawaii sqlite file in Resources
engine= create_engine("sqlite:///Resources/hawaii.sqlite")


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
Base= automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station =  Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#List all available routes on the homepage
@app.route("/")
def homepage():
    return (f"Welcome to the Hawaii Climate Analysis homepage! <br>"
            f" Available routes: <br>"
            f"/ <br>"
            f"/api/v1.0/precipitation <br>"
            f"/api/v1.0/stations <br>"
            f"/api/v1.0/tobs <br>"
            f"/api/v1.0/start/end <br>")

# Precipitaion route
@app.route("/api/v1.0/precipitation")
def precip():
    # Convert the query results from your precipitation analysis 
    recentYear = dt.date(2017,8,23)
    prevYear = recentYear - dt.timedelta(days= 365)

    # query to retrieve data and precipitation scores
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= prevYear).all()
    session.close()

    # dictionary using date as the key and prcp as the value
    precipAnalysis= {date: prcp for date, prcp in precipitation}

    # Return the JSON representation of your dictionary.
    return jsonify(precipAnalysis)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # show list of stations
    # perform a query to retrieve the names of the stations
    results = session.query(station.station).all()
    session.close()

    # make a list 
    stationList= list(np.ravel(results))

    # Return a JSON list of stations from the dataset.
    return jsonify(stationList)

# tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    recentYear = dt.date(2017,8,23)
    prevYear = recentYear - dt.timedelta(days= 365)

    mostActiveTemp= session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= prevYear).all()

    session.close()

    # make a list
    temperatureList= list(np.ravel(mostActiveTemp))

    # Return a JSON list of temperature observations for the previous year.
    return jsonify(temperatureList)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature 
    # for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):

    # select statement
    selection= [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]

    if not end:

        startDate= dt.datetime.strptime(start,"%m%d%Y" )

        results = session.query(*selection).filter(measurement.date >= startDate).all()

        session.close()

        #make a list
        startEndList= list(np.ravel(results))

        # Return a JSON list 
        return jsonify(startEndList)  

    else:

        startDate= dt.datetime.strptime(start,"%m%d%Y" )
        endDate= dt.datetime.strptime(end,"%m%d%Y" )

        results = session.query(*selection).filter(measurement.date >=startDate).filter(measurement.date <= endDate).all()

        session.close()

        startEndList= list(np.ravel(results))

        # return the json list 
        return jsonify(startEndList)
        
# app launcher
if __name__ == '__main__':
    app.run(debug=True)
