#################################################
# Hawaii weather API
#################################################

# Import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect tables
Base.prepare(engine, reflect=True)

# Save reference to tables
Measurements = Base.classes.measurement
Stations = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Default landing page of webserver
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp_dates/yyyy-mm-dd<br/>"
        f"/api/v1.0/temp_dates/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )

#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation data"""
    # Query rainfall for last 12 months
    rain_query = session.query(Measurements.date, Measurements.prcp).\
                     filter(Measurements.date >= '2016-08-23').\
                     filter(Measurements.date <= '2017-08-23').all()

    session.close()

    # Transform query result into List of Dictionaries for JSONification
    precipitation_list = []
    for date, rain in rain_query:
        rain_dictionary = {}
        rain_dictionary[date] = rain
        precipitation_list.append(rain_dictionary)
    return jsonify(precipitation_list)

#################################################

@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return list of stations"""
   # Query all stations
    station_query = session.query(Stations.station).\
                            group_by(Stations.station).all()
                            
    session.close()

    # Flatten List using np.ravel for JSONification
    station_list = list(np.ravel(station_query))
    return jsonify(station_list)
    
#################################################    

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return tobs data"""
    # Query rainfall for last 12 months from most active station
    temp_query = session.query(Measurements.date, Measurements.tobs).\
                 filter(Measurements.station == 'USC00519281').\
                 filter(Measurements.date >= '2016-08-18').\
                 filter(Measurements.date <= '2017-08-18').\
                 order_by(Measurements.date.desc()).all()

    session.close()

    # Transform query result into List of Dictionaries for JSONification
    temperature_list = []
    for date, temp in temp_query:
        temp_dictionary = {}
        temp_dictionary[date] = temp
        temperature_list.append(temp_dictionary)
    return jsonify(temperature_list)

#################################################

@app.route("/api/v1.0/temp_dates/<start>")
def temp_dates_start(start):
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return tobs data"""
    # Query TMIN, TMAX and TAVG for defined time period
    temp_stats_functions = [func.min(Measurements.tobs),
                            func.max(Measurements.tobs),
                            func.avg(Measurements.tobs)]

    temp_start_stats = session.query(*temp_stats_functions).\
                       filter(Measurements.date >= start).\
                       order_by(Measurements.station).all()

    session.close()

    # Transform query result into List for JSONification
    stats_start_dictionary = {
    'TMIN' : temp_start_stats[0][0],
    'TMAX' : temp_start_stats[0][1],
    'TAVG' : temp_start_stats[0][2]}
    return jsonify(stats_start_dictionary)

#################################################

@app.route("/api/v1.0/temp_dates/<start>/<end>")
def temp_dates(start, end):
    # Create session (link) from Python to the DB
    session = Session(engine)

    """Return tobs data"""
    # Query TMIN, TMAX and TAVG for defined time period
    temp_stats_functions = [func.min(Measurements.tobs),
                            func.max(Measurements.tobs),
                            func.avg(Measurements.tobs)]

    temp_stats = session.query(*temp_stats_functions).\
                filter(Measurements.date >= start).\
                filter(Measurements.date <= end).\
                order_by(Measurements.station).all()

    session.close()

    # Transform query result into Dictionary for JSONification
    stats_dictionary = {
    'TMIN' : temp_stats[0][0],
    'TMAX' : temp_stats[0][1],
    'TAVG' : temp_stats[0][2]}
    return jsonify(stats_dictionary)

if __name__ == '__main__':
    app.run(debug=True)
