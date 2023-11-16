# Import the dependencies.

from flask import Flask,jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import numpy as np
from datetime import datetime,timedelta
from sqlalchemy import desc



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found

Base.classes.keys()

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB

    #retrieve only the last 12 months of data)
    #to a dictionary using date as the key 
    # and prcp as the value.
    lastest_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    one_year_before_str = lastest_date[0]
    one_year_before = datetime.strptime(one_year_before_str,'%Y-%m-%d')- timedelta(days=365)


    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.asc()).\
          filter(Measurement.date >= one_year_before).all()
    
    #Return the JSON representation of your dictionary.
    prcp_data = []
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)

    print(prcp_data)
    return jsonify(prcp_data)




#/api/v1.0/stations
@app.route('/api/v1.0/stations')
def stations():

    stations = session.query(Station.station, Station.name).all()
    station_list = [{"station":station,"name":name} 
                    for station, name in stations]
    return jsonify(station_list) 
    

#/api/v1.0/tobs
@app.route('/api/v1.0/tobs')
def tobs():
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    most_active_station_id = most_active_stations[0][0]

    lastest_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    one_year_before_str = lastest_date[0]
    one_year_before = datetime.strptime(one_year_before_str,'%Y-%m-%d')- timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == most_active_station_id).\
    filter(Measurement.date >= one_year_before).all()

    tobs_data = [{"date":date, "tobs":tobs} for date,tobs in results]

    return jsonify(tobs_data)
    

 #/api/v1.0/<start> and /api/v1.0/<start>/<end>

@app.route("/api/v1.0/<start>")
def calc_temps_sd(start):
    
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
   
    temp_obs={}
    temp_obs["Min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)

#A start/end route that: Accepts the start and end dates as parameters from the URL

@app.route('/api/v1.0/<start>/<end>')
def calc_temps(start_date, end_date=None):

    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date)

    if end_date:
        query = query.filter(Measurement.date <= end_date)

    result = query.all()

    if not result:
        return None

    tmin, tavg, tmax = result[0]
    return {"TMIN": tmin, "TAVG": tavg, "TMAX": tmax}



if __name__ == '__main__':
    app.run(debug=True)
