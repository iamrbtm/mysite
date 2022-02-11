from flask.helpers import flash
import requests, json, flask_login
from website import db
from website.models import *
from sqlalchemy.sql import desc
from datetime import datetime,timedelta


def check_for_recalls(id):
    veh = db.session.query(Vehicles).filter_by(id = id).first()
    results = get_recalls(veh.year, veh.make, veh.model)
    return results

def get_recalls(year, make, model):
    api = f'https://api.nhtsa.gov/recalls/recallsByVehicle?make={make}&model={model}&modelYear={year}'
    request = requests.request("GET",api)
    recalljson = json.loads(request.text)
    return recalljson

def save_to_db(results, id):
        newrecall = VehicleRecalls(
            datetimechecked = datetime.now(),
            recallcount = results['Count'],
            message = results['Message'],
            vehicleid = id,
            userid = flask_login.current_user.id
        )
        db.session.add(newrecall)
        db.session.commit()

        if len(results['results']) != 0:
            for i in range(len(results['results'])):
                recallnew = Recalls(
                    summary = results['results'][i]['Summary'],
                    conequence = results['results'][i]['Conequence'],
                    remedy = results['results'][i]['Remedy'],
                    notes = results['results'][i]['Notes'],
                    reportdate = datetime.strptime(results['results'][i]['ReportReceivedDate'],"%d/%m/%Y"),
                    recallid = newrecall.id,
                    )
                db.session.add(recallnew)
                db.session.commit()

    
def flashresults(count):
    if count == 0:
        msg=f'Recalls were checked: {count} were found.'
    else:
        msg=f"Recalls were checked: {count} were found. See the recalls section of your vehicles page for more details"
    flash(msg)
    
def check_timing_for_recall(id):
    try:
        veh = db.session.query(VehicleRecalls).filter_by(vehicleid=id).order_by(desc(VehicleRecalls.datetimechecked)).first()
        datecheck = veh.datetimechecked + timedelta(days=10) < datetime.now()
        if datecheck:
            check = check_for_recalls(id)
            save_to_db(check, id)
            flashresults(check['Count'])
    except:
        pass
    finally:
        return datecheck