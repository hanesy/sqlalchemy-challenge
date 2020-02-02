# ## Step 2 - Climate App
# Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed.
# * Use FLASK to create your routes.

import numpy as np
from datetime import datetime, timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Get last date of Measurement database
session = Session(engine)
last_date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
last_date = datetime.strptime(last_date_query[0], '%Y-%m-%d')
session.close()

app = Flask(__name__)
# ### Routes

# * `/`
#   * Home page.
#   * List all routes that are available.
@app.route("/")
def welcome():
    return (
        f"<h1>Welcome to the Climate API!</h1><br/>"
        f"<h2>Available Routes:</h2><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"<h3>following date formats should be 'YYYY-MM-DD'</h3>"
        f"/api/v1.0/'start_date'<br/>"
        # f"/api/v1.0/'start_date'/'end_date'"
    )


# * `/api/v1.0/precipitation`
#   * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#   * Return the JSON representation of your dictionary.
### is this query for the last year?
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Convert list of tuples into normal list
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


# # * `/api/v1.0/stations`
# #   * Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


# # * `/api/v1.0/tobs`
# #   * query for the dates and temperature observations from a year from the last data point.
# #   * Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    query_date = last_date - timedelta(days=366)


    # ### if returning a list of temperatures only
    # results = session.query(Measurement.tobs).filter(Measurement.date > query_date).order_by(Measurement.date).all()
    # session.close()

    # lastyear_tobs = list(np.ravel(results))
    # return jsonify(lastyear_tobs)

    ### if returning a list of dictionary
    # Perform a query to retrieve the data and tobs scores
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > query_date).order_by(Measurement.date).all()
    session.close()

    lastyear_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        lastyear_tobs.append(tobs_dict)

    return jsonify(lastyear_tobs)

# # * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
# #   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# #   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# #   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>")
def date_search_start(start):
    sel = [func.min(Measurement.tobs), 
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)]

    session = Session(engine)
    results = session.query(*sel).filter(Measurement.date >= start).all()
    session.close()
    
    list_results = list(np.ravel(results))
    temp_dict = {}
    temp_dict["TMIN"] = list_results[0]
    temp_dict["TAVG"] = list_results[1]
    temp_dict["TMAX"] = list_results[2]
    return jsonify(temp_dict)

### Need to ask about this route.
# @app.route("/api/v1.0/<start>/<end>")
# def date_search_startend (start, end):
#     sel = [func.min(Measurement.tobs), 
#         func.avg(Measurement.tobs),
#         func.max(Measurement.tobs)]

#     session = Session(engine)
#     results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
#     session.close()
    
#     list_results = list(np.ravel(results))
#     # temp_dict = {}
#     # temp_dict["TMIN"] = list_results[0]
#     # temp_dict["TAVG"] = list_results[1]
#     # temp_dict["TMAX"] = list_results[2]
#     return jsonify(list_results)


# ## Hints
### I didn't need to join any tables... i might need to for the optional assignment
# * You will need to join the station and measurement tables for some of the analysis queries.
# * Use Flask `jsonify` to convert your API data into a valid JSON response object.


if __name__ == '__main__':
    app.run(debug=True)
