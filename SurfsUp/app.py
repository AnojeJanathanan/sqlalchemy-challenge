# Import the dependencies.

from sqlalchemy import func
import pandas as pd
import datetime as d
import matplotlib.pyplot as plt
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

# reflect the tables


# Save references to each table

database_path = Path("C:/Users/anoje/.anaconda/Starter_Code/Resources/hawaii.sqlite") #Import database path
engine = create_engine(f"sqlite:///{database_path}") #Create engine/connect path

Base = automap_base() #Base class for database, created to fit python classes 
Base.prepare(engine, reflect=True)

Station = Base.classes.station #References for tables 
Measurement = Base.classes.measurement

app = Flask(__name__) 

@app.route("/")  #Create routes for pages 
def anoje():
    output = "Climate Summaries (Anoje Janathanan) <br/>" \
             "All Route:<br/>" \
             "/api/v1.0/precipitation<br/>" \
             "/api/v1.0/stations<br/>" \
             "/api/v1.0/tobs<br/>" \
             "/api/v1.0/start <br/>" \
             "/api/v1.0/start/end"

    return output

@app.route("/api/v1.0/precipitation")
def precipitation_route():
    session = Session(bind=engine)

    recent_new = session.query(func.max(Measurement.date)).scalar()

    twelve_surf = (d.datetime.strptime(recent_new, '%Y-%m-%d') - d.timedelta(days=365)).strftime('%Y-%m-%d')

    p = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= twelve_surf).\
        filter(Measurement.date <= recent_new).all()

    session.close()

    data = [{"Date": date, "Precipitation": prcp} for date, prcp in p]

    return jsonify(data)

@app.route("/api/v1.0/stations")
def stations_route():
    session = Session(bind=engine)
    station_data = session.query(Measurement.station).distinct().all()
    session.close()

    stations_list = [station[0] for station in station_data]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs_route():
    session = Session(bind=engine)

    m = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    recent_new = session.query(func.max(Measurement.date)).scalar()
    twelve = (d.datetime.strptime(recent_new, '%Y-%m-%d') - d.timedelta(days=365)).strftime('%Y-%m-%d')

    t = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == m).\
        filter(Measurement.date >= twelve).all()

    session.close()

    l = [{"date": date, "tobs": tobs} for date, tobs in t]

    return jsonify(l)

@app.route("/api/v1.0/start/<start>")
def temp_start(start):
    session = Session(bind=engine)

    temper = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    dict_temp = {
        "TMIN": temper[0][0],
        "TAVG": temper[0][1],
        "TMAX": temper[0][2]
    }

    return jsonify(dict_temp)

@app.route("/api/v1.0/start/<start>/end/<end>")
def start_end(start, end):
    session = Session(bind=engine)

    temper = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    dict = {
        "TMIN": temper[0][0],
        "TAVG": temper[0][1],
        "TMAX": temper[0][2]
    }

    return jsonify(dict)

if __name__ == '__main__':
    app.run(debug=True)
