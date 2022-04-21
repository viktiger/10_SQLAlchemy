import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup i.e. Creating an App
#################################################
app = Flask(__name__)


#################################################
# Flask Routes i.e. Defining static routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our Session (link) from Python to the DB
    Session = Session(engine)

    """Return a list of all stations precipitation"""
    # Query all stations
    results = Session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

    # Convert to list of dictionaries to jsonify
    precipitation_date_list = []

    for date, prcp in results:
        new_dict = {}
        new_dict[date] = prcp
        precipitation_date_list.append(new_dict)

    Session.close()

    # Convert list of tuples into normal list
    # all_names = list(np.ravel(results))

    return jsonify(precipitation_date_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our Session (link) from Python to the DB
    Session = Session(engine)

    """Return a list of stations data including the precipitation, age, and sex of each stations"""
    # Query all stations
    results = Session.query(Station.station, Station.name).all()

    # convert results to a dict
    stations_dict = dict(stations)

    Session.close()

    # return json list of dict (I decided to do a dict instead of a list here to show both the station name and the station number)
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the last date contained in the dataset and date from one year ago
    most_recent_date = Session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = dt.datetime.strptime(most_recent_date[0],'%Y-%m-%d')
    start_date = end_date - dt.timedelta(days=365).strftime('%Y-%m-%d')

    # Query for the dates and temperature values
    results =   session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start_date).order_by(Measurement.date).all()

    # Convert to list of dictionaries to jsonify
    tobs_list = []

    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        tobs_list.append(new_dict)

    session.close()

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")

# min, average, and max temps for a given date range
def temp_range_start(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)

    startdate_list = []

    results =   session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()

    for date, min, max, avg in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TMAX"] = max
        new_dict["TAVG"] = avg
        startdate_list.append(new_dict)

    session.close()    

    return jsonify(startdate_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):
    """TMIN, TAVG, and TMAX per date for a date range.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)

    startend_list = []

    results =   session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(and_(Measurement.date >= start, Measurement.date <= end)).\
                        group_by(Measurement.date).all()

    for date, min, max, avg in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TMAX"] = max
        new_dict["TAVG"] = avg
        startend_list.append(new_dict)

    session.close()    

    return jsonify(startend_list)

#################################################
# Flask Main i.e. Defining main behavior
#################################################

if __name__ == '__main__':
    app.run(debug=True)
