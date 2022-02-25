from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website.models import *
from website.templates.mileage.mileage_process import *
from datetime import datetime
from website import db

# import css_inline, html2text
from sqlalchemy.sql import desc
import datetime, os
from math import ceil

mileage = Blueprint("mileage", __name__)


@mileage.route("/", methods=["GET", "POST"])
@login_required
def mileageHome():
    if request.method == "POST":
        formdata = request.form.to_dict()
        if request.form.get("catagorybtn") == "catagory":
            add_catagory(**formdata)
            flash(formdata["catagoryname"] + " was added to the database!", "success")
        elif request.form.get("doctorbtn") == "doctor":
            add_doctor(**formdata)
            flash(
                formdata["firstname"]
                + " "
                + formdata["lastname"]
                + " was added to the database!",
                "success",
            )
        elif request.form.get("facilitybtn") == "facility":
            add_facility(**formdata)
            flash(formdata["name"] + " was added to the database!", "success")
        elif request.form.get("reservation") == "single":
            add_roundtrip_reservation(**formdata)
            flash("Trip added to database", "success")
        elif request.form.get("reservation") == "threeway":
            add_threeway_reservation(**formdata)
            flash("Trip added to database", "success")
        elif request.form.get("reservation") == "oneway":
            add_oneway_reservation(**formdata)
            flash("Trip added to database", "success")

    sentPrice = 0.0
    finalPrice = 0.0
    printPrice = 0.0
    tosendPrice = 0.0
    ntnPrice = 0.0
    totalPrice = 0.0
    totalMileage = 0
    ntnMileage = 0
    tosendMileage = 0
    printMileage = 0
    finalMileage = 0
    sentMileage = 0
    sent = []
    print = []
    tosend = []
    final = []
    ntn = []
    total = []

    trips = (
        db.session.query(Mileage)
        .filter_by(userid=flask_login.current_user.id)
        .order_by(desc(Mileage.date), Mileage.time, Mileage.legnumber)
        .all()
    )

    for trip in trips:
        if trip.sent:
            sentPrice += trip.tripprice
            sentMileage += trip.mileage
        elif trip.printed:
            printPrice += trip.tripprice
            printMileage += trip.mileage
        elif trip.tosend:
            tosendPrice += trip.tripprice
            tosendMileage += trip.mileage
        elif trip.finished:
            finalPrice += trip.tripprice
            finalMileage += trip.mileage
        elif trip.needTripNumber:
            ntnPrice += trip.tripprice
            ntnMileage += trip.mileage
        totalPrice += trip.tripprice
        totalMileage += trip.mileage
    total.append(totalPrice)
    total.append(totalMileage)
    sent.append(sentPrice)
    sent.append(sentMileage)
    ntn.append(ntnPrice)
    ntn.append(ntnMileage)
    final.append(finalPrice)
    final.append(finalMileage)
    tosend.append(tosendPrice)
    tosend.append(tosendMileage)
    print.append(printPrice)
    print.append(printMileage)

    doctors = (
        db.session.query(Doctor)
        .filter_by(userid=flask_login.current_user.id)
        .order_by(Doctor.lastname, Doctor.firstname)
        .all()
    )
    facilities = (
        db.session.query(Facility)
        .filter_by(userid=flask_login.current_user.id)
        .order_by(Facility.name)
        .all()
    )
    catagories = (
        db.session.query(MileageCatagory)
        .filter_by(userid=flask_login.current_user.id)
        .all()
    )
    tosendCount = db.session.query(Mileage).filter_by(tosend=True).count()
    needTripNumCount = (
        db.session.query(Mileage)
        .filter(Mileage.needTripNumber == True)
        .filter_by(userid=flask_login.current_user.id)
        .count()
    )
    return render_template(
        "/mileage/mileage.html",
        user=User,
        doctors=doctors,
        facilities=facilities,
        trips=trips,
        catagories=catagories,
        total=total,
        ntn=ntn,
        final=final,
        print=print,
        sent=sent,
        tosend=tosend,
        tosendCount=tosendCount,
        needTripNumCount=needTripNumCount,
    )


@mileage.route("/fillpdf", methods=["GET", "POST"])
@login_required
def fillpdf():
    numtrips = (
        db.session.query(Mileage)
        .filter_by(tosend=True)
        .order_by(desc(Mileage.date), Mileage.legnumber)
        .count()
    )
    trips = (
        db.session.query(Mileage)
        .filter_by(tosend=True)
        .order_by(desc(Mileage.date), Mileage.legnumber)
        .all()
    )

    smalltriplist = [trips[i : i + 7] for i in range(0, len(trips), 7)]
    pages = ceil(numtrips / 7)
    pg = 1
    inc = 0
    while pg <= pages:
        isExist = os.path.exists(
            os.path.join(
                "website", "static", "pdf", datetime.datetime.now().strftime("%m%d%y")
            )
        )
        if not isExist:
            os.makedirs(
                os.path.join(
                    "website",
                    "static",
                    "pdf",
                    datetime.datetime.now().strftime("%m%d%y"),
                )
            )

        data = pdf_generate_datafile(smalltriplist[inc])
        pathTemplate = os.path.join("website", "static", "pdf", "MileageReimburse.pdf")
        pathOutput = os.path.join(
            "website",
            "static",
            "pdf",
            datetime.datetime.now().strftime("%m%d%y"),
            f"{pg}.pdf",
        )
        outcome = fill_pdf(pathTemplate, pathOutput, data)

        if outcome:
            for num in smalltriplist[inc]:
                set_flag(num.id)

        pg += 1
        inc += 1

    return redirect(url_for("mileage.mileageHome"))


@mileage.route("/tripnumadd/<id>", methods=["GET", "POST"])
@login_required
def tripnumadd(id):
    from math import floor

    if request.method == "POST":
        legnumber = str(db.session.query(Mileage).filter_by(id=id).first().legnumber)
        base = legnumber.find(".")
        baselegnumber = int(legnumber[:base])
        legs = [
            float(baselegnumber + 0.00),
            float(baselegnumber + 0.1),
            float(baselegnumber + 0.11),
        ]
        records = db.session.query(Mileage).filter(Mileage.legnumber.in_(legs)).all()
        for record in records:
            record.tripnumber = request.form.get("tripnum")
            record.needTripNumber = False
            record.tosend = True
            record.tosend_when == datetime.datetime.now()
            db.session.commit()
    return redirect(request.referrer)


@mileage.route("/tripnumremove/<id>")
@login_required
def tripnumremove(id):
    from math import floor

    tripnum = str(db.session.query(Mileage).filter_by(id=id).first().tripnumber)
    records = db.session.query(Mileage).filter(Mileage.tripnumber == tripnum).all()
    for record in records:
        record.tripnumber = ""
        record.needTripNumber = True
        record.tosend = False
        record.tosend_when == ""
        db.session.commit()
    return redirect(url_for("mileage.mileageHome"))


@mileage.route("/catagory", methods=["GET", "POST"])
@login_required
def catagory():
    if request.method == "POST":
        formdata = request.form.to_dict()
        print(formdata)
        edit_catagory(**formdata)

    catagories = (
        db.session.query(MileageCatagory)
        .filter_by(userid=flask_login.current_user.id)
        .all()
    )
    return render_template("/mileage/catagory.html", user=User, catagories=catagories)


@mileage.route("/tripnum", methods=["GET"])
@login_required
def mileageTripNum():
    trips = (
        db.session.query(Mileage)
        .filter_by(userid=flask_login.current_user.id)
        .filter_by(needTripNumber=True)
        .order_by(desc(Mileage.date), Mileage.time, Mileage.legnumber)
        .all()
    )
    if len(trips) == 0:
        return redirect(url_for("mileage.mileageHome"))
    doctors = (
        db.session.query(Doctor).filter_by(userid=flask_login.current_user.id).all()
    )
    facilities = (
        db.session.query(Facility).filter_by(userid=flask_login.current_user.id).all()
    )
    catagories = (
        db.session.query(MileageCatagory)
        .filter_by(userid=flask_login.current_user.id)
        .all()
    )
    tosendCount = db.session.query(Mileage).filter_by(tosend=True).count()
    return render_template(
        "/mileage/tripnum.html",
        user=User,
        doctors=doctors,
        facilities=facilities,
        trips=trips,
        catagories=catagories,
        tosendCount=tosendCount,
    )


@mileage.route("/report/", methods=["GET"])
def mileage_report():

    mileages = db.session.query(Mileage).filter(Mileage.userid==current_user.id).order_by(Mileage.legnumber).all()
    facilities = db.session.query(Facility).filter(Facility.userid==current_user.id).all()
    providers = db.session.query(Doctor).filter(Doctor.userid==current_user.id).all()
    catagories = db.session.query(MileageCatagory).filter(MileageCatagory.userid==current_user.id).all()
    
    content = {'mileages':mileages, 'facilities':facilities, 'providers':providers, 'catagories':catagories}
    return render_template("mileage/mileage_report.html", **content)

@mileage.context_processor
def inject_today_date():
    return {'today_date': datetime.datetime.now()}