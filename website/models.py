from enum import unique
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from website import db

from flask_login import UserMixin, current_user
from sqlalchemy.sql import func
import datetime

# Users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    dob = db.Column(db.DateTime)
    address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    avatar = db.Column(db.Text)
    avatar_filename = db.Column(db.Text)
    avatar_mimetype = db.Column(db.Text)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


# Guill Menu
class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.Text)
    pictureURL = db.Column(db.String(1000))
    numServings = db.Column(db.Integer)
    servingSize = db.Column(db.String(150))
    cookTime = db.Column(db.String(10))
    prepTime = db.Column(db.String(10))
    cookTemp = db.Column(db.String(5))
    notionID = db.Column(db.String(50), unique=True)
    origurl = db.Column(db.Text)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    recipe = db.relationship("Recipe", backref="dish", passive_deletes=True)
    steps = db.relationship("Steps", backref="dish", passive_deletes=True)
    plan = db.relationship("Planner", backref="dish", passive_deletes=True)
    catagory = db.relationship("Catagories", backref="catagories", passive_deletes=True)
    tags = db.relationship("Tags", backref="tags", passive_deletes=True)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.String(10))
    measurement = db.Column(db.String(50))
    ing = db.Column(db.String(150))
    catagory = db.Column(db.String(50))
    notes = db.Column(db.String(250), nullable=True)
    fat_total = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Integer, nullable=True)
    fat_sat = db.Column(db.Integer, nullable=True)
    fat_trans = db.Column(db.Integer, nullable=True)
    cholesterol = db.Column(db.Integer, nullable=True)
    sodium = db.Column(db.Integer, nullable=True)
    potassium = db.Column(db.Integer, nullable=True)
    carb_total = db.Column(db.Integer, nullable=True)
    carb_fiber = db.Column(db.Integer, nullable=True)
    carb_sugar = db.Column(db.Integer, nullable=True)
    protein = db.Column(db.Integer, nullable=True)
    servsize = db.Column(db.String(100), nullable=True)
    calories = db.Column(db.Integer, nullable=True)
    calories_fat = db.Column(db.Integer, nullable=True)
    pictureURL = db.Column(db.String(500), nullable=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    dishfk = db.Column(
        db.Integer, db.ForeignKey("dish.id", ondelete="CASCADE"), nullable=False
    )


class Steps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    step_num = db.Column(db.Integer)
    step_text = db.Column(db.Text)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    dishfk = db.Column(
        db.Integer, db.ForeignKey("dish.id", ondelete="CASCADE"), nullable=False
    )


class Planner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True))
    dayofwk = db.Column(db.Integer)
    wknum = db.Column(db.Integer)
    item = db.Column(db.String(200))
    dishfk = db.Column(
        db.Integer, db.ForeignKey("dish.id", ondelete="CASCADE"), nullable=True
    )
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class PlanDish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wknum = db.Column(db.Integer)
    planidfk = db.Column(db.Integer)
    mainidfk = db.Column(db.Integer)
    sideidfk = db.Column(db.Integer)
    drinkidfk = db.Column(db.Integer)
    dessertidfk = db.Column(db.Integer)
    notes = db.Column(db.Text)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class CatTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dish = db.Column(db.Integer)
    cat = db.Column(db.Integer)
    tag = db.Column(db.Integer)


class Catagories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catagory = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # Forign Key
    dishfk = db.Column(db.Integer, db.ForeignKey("dish.id"), nullable=False)


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # Forign Key
    dishfk = db.Column(db.Integer, db.ForeignKey("dish.id"), nullable=False)


# Medical
class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    type = db.Column(db.String(50))
    userid = db.Column(db.Integer, nullable=False)
    # relationship
    doctor = db.relationship("Doctor", backref="facility", passive_deletes=True)
    hosptial = db.relationship("Hosptial", backref="facility", passive_deletes=True)
    surgeries = db.relationship("Surgeries", backref="facility", passive_deletes=True)


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prefix = db.Column(db.String(25))
    firstname = db.Column(db.String(75))
    middleinit = db.Column(db.String(2))
    lastname = db.Column(db.String(75))
    suffix = db.Column(db.String(50))
    fulldisplayname = db.Column(db.Text)
    shortdisplayname = db.Column(db.Text)
    address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    asst = db.Column(db.String(100))
    userid = db.Column(db.Integer, nullable=False)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # relationships
    hosptial = db.relationship("Hosptial", backref="doctor", passive_deletes=True)
    surgeries = db.relationship("Surgeries", backref="doctor", passive_deletes=True)
    medication = db.relationship("Medications", backref="doctor", passive_deletes=True)
    a1c = db.relationship("A1C", backref="doctor", passive_deletes=True)
    # forignkeys
    facilityfk = db.Column(
        db.Integer, db.ForeignKey("facility.id", ondelete="CASCADE"), nullable=False
    )


class Hosptial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datestart = db.Column(db.Date, nullable=False)
    dateend = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(100))
    userid = db.Column(db.Integer, nullable=False)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # forign keys
    doctorfk = db.Column(
        db.Integer, db.ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False
    )
    facilityfk = db.Column(
        db.Integer, db.ForeignKey("facility.id", ondelete="CASCADE"), nullable=False
    )


class Surgeries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    startdate = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(500))
    body_part = db.Column(db.String(50))
    age = db.Column(db.Integer)
    userid = db.Column(db.Integer, nullable=False)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # forign keys
    doctorfk = db.Column(
        db.Integer, db.ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False
    )
    facilityfk = db.Column(
        db.Integer, db.ForeignKey("facility.id", ondelete="CASCADE"), nullable=False
    )


class Medications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    dose = db.Column(db.String(50))
    how_often = db.Column(db.String(100))
    num_filled_days = db.Column(db.Integer)
    reason_for_taking = db.Column(db.String(100))
    pharmacy = db.Column(db.String(100))
    last_refilled = db.Column(db.DateTime)
    next_refill = db.Column(db.DateTime)
    process = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    userid = db.Column(db.Integer, nullable=False)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # forign keys
    doctorfk = db.Column(
        db.Integer, db.ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False
    )


class Allergies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    reaction = db.Column(db.String(50))
    dateadded = db.Column(db.Date, nullable=False)
    userid = db.Column(db.Integer, nullable=False)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class A1C(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    testresult = db.Column(db.Float)
    userid = db.Column(db.Integer, nullable=False)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # forign keys
    doctorfk = db.Column(
        db.Integer, db.ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False
    )


class Wifi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    SSID = db.Column(db.String(100))
    password = db.Column(db.String(100))
    path = db.Column(db.String(1000))
    userid = db.Column(db.Integer, nullable=False)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class Vehicles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), unique=True)
    year = db.Column(db.Integer)
    make = db.Column(db.String(75))
    model = db.Column(db.String(75))
    trim = db.Column(db.String(20))
    color = db.Column(db.String(25))
    purchase_date = db.Column(db.DateTime)
    sell_date = db.Column(db.DateTime)
    reasonforsale = db.Column(db.String(75))
    owner = db.Column(db.Integer)
    saleamount = db.Column(db.Float)
    purchaseprice = db.Column(db.Float)
    purchasefrom = db.Column(db.String(75))
    tagsexpire = db.Column(db.DateTime)
    pictureURL = db.Column(db.String(500))
    vinnumber = db.Column(db.String(25))
    licenseplate = db.Column(db.String(20))
    curown = db.Column(db.Boolean)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # Relationships
    service = db.relationship(
        "Service", backref="vehicles", lazy="dynamic", passive_deletes=True
    )


class States(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(50))
    abr = db.Column(db.String(2))


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    # MENU
    menu_planner = db.Column(db.Boolean)
    menu_rec = db.Column(db.Boolean)
    menu_shopping = db.Column(db.Boolean)
    menu_extra1 = db.Column(db.Boolean)
    menu_extra2 = db.Column(db.Boolean)
    menu_extra3 = db.Column(db.Boolean)
    menu_extra4 = db.Column(db.Boolean)
    menu_extra5 = db.Column(db.Boolean)
    menu_extra1_label = db.Column(db.String(30))
    menu_extra1_url = db.Column(db.String(200))
    menu_extra2_label = db.Column(db.String(30))
    menu_extra2_url = db.Column(db.String(200))
    menu_extra3_label = db.Column(db.String(30))
    menu_extra3_url = db.Column(db.String(200))
    menu_extra4_label = db.Column(db.String(30))
    menu_extra4_url = db.Column(db.String(200))
    menu_extra5_label = db.Column(db.String(30))
    menu_extra5_url = db.Column(db.String(200))
    # HEALTH
    health_facilities = db.Column(db.Boolean)
    health_doctors = db.Column(db.Boolean)
    health_meds = db.Column(db.Boolean)
    health_medlist = db.Column(db.Boolean)
    health_hospt = db.Column(db.Boolean)
    health_surg = db.Column(db.Boolean)
    health_allergies = db.Column(db.Boolean)
    health_a1c = db.Column(db.Boolean)
    health_cpap = db.Column(db.Boolean)
    health_extra1 = db.Column(db.Boolean)
    health_extra2 = db.Column(db.Boolean)
    health_extra3 = db.Column(db.Boolean)
    health_extra4 = db.Column(db.Boolean)
    health_extra5 = db.Column(db.Boolean)
    health_extra1_label = db.Column(db.String(30))
    health_extra1_url = db.Column(db.String(200))
    health_extra2_label = db.Column(db.String(30))
    health_extra2_url = db.Column(db.String(200))
    health_extra3_label = db.Column(db.String(30))
    health_extra3_url = db.Column(db.String(200))
    health_extra4_label = db.Column(db.String(30))
    health_extra4_url = db.Column(db.String(200))
    health_extra5_label = db.Column(db.String(30))
    health_extra5_url = db.Column(db.String(200))
    # PRODUCTIVITY
    prod_goals = db.Column(db.Boolean)
    prod_projects = db.Column(db.Boolean)
    prod_tasks = db.Column(db.Boolean)
    prod_extra1 = db.Column(db.Boolean)
    prod_extra2 = db.Column(db.Boolean)
    prod_extra3 = db.Column(db.Boolean)
    prod_extra4 = db.Column(db.Boolean)
    prod_extra5 = db.Column(db.Boolean)
    prod_extra1_label = db.Column(db.String(30))
    prod_extra1_url = db.Column(db.String(200))
    prod_extra2_label = db.Column(db.String(30))
    prod_extra2_url = db.Column(db.String(200))
    prod_extra3_label = db.Column(db.String(30))
    prod_extra3_url = db.Column(db.String(200))
    prod_extra4_label = db.Column(db.String(30))
    prod_extra4_url = db.Column(db.String(200))
    prod_extra5_label = db.Column(db.String(30))
    prod_extra5_url = db.Column(db.String(200))
    # PERSONAL
    personal_cars = db.Column(db.Boolean)
    personal_wifi = db.Column(db.Boolean)
    personal_extra1 = db.Column(db.Boolean)
    personal_extra2 = db.Column(db.Boolean)
    personal_extra3 = db.Column(db.Boolean)
    personal_extra4 = db.Column(db.Boolean)
    personal_extra5 = db.Column(db.Boolean)
    personal_extra1_label = db.Column(db.String(30))
    personal_extra1_url = db.Column(db.String(200))
    personal_extra2_label = db.Column(db.String(30))
    personal_extra2_url = db.Column(db.String(200))
    personal_extra3_label = db.Column(db.String(30))
    personal_extra3_url = db.Column(db.String(200))
    personal_extra4_label = db.Column(db.String(30))
    personal_extra4_url = db.Column(db.String(200))
    personal_extra5_label = db.Column(db.String(30))
    personal_extra5_url = db.Column(db.String(200))
    # OTHER
    other_extra1 = db.Column(db.Boolean)
    other_extra2 = db.Column(db.Boolean)
    other_extra3 = db.Column(db.Boolean)
    other_extra4 = db.Column(db.Boolean)
    other_extra5 = db.Column(db.Boolean)
    other_extra1_label = db.Column(db.String(30))
    other_extra1_url = db.Column(db.String(200))
    other_extra2_label = db.Column(db.String(30))
    other_extra2_url = db.Column(db.String(200))
    other_extra3_label = db.Column(db.String(30))
    other_extra3_url = db.Column(db.String(200))
    other_extra4_label = db.Column(db.String(30))
    other_extra4_url = db.Column(db.String(200))
    other_extra5_label = db.Column(db.String(30))
    other_extra5_url = db.Column(db.String(200))
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(75))
    place = db.Column(db.String(75))
    cost = db.Column(db.Float)
    mileage = db.Column(db.Integer)
    date = db.Column(db.Date)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # forign keys
    vehiclefk = db.Column(
        db.Integer, db.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=True
    )


class CodeSnips(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catagory = db.Column(db.Text)
    subcatagory = db.Column(db.Text)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    code = db.Column(db.Text)
    link1 = db.Column(db.Text)
    link2 = db.Column(db.Text)
    link3 = db.Column(db.Text)
    link4 = db.Column(db.Text)
    link5 = db.Column(db.Text)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class HousingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movein = db.Column(db.Date)
    moveout = db.Column(db.Date)
    address = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class Cpap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    lastordered = db.Column(db.Date)
    nextorderdate = db.Column(db.Date)
    howoften = db.Column(db.Integer)
    imageURL = db.Column(db.Text)
    itemnum = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class Graves(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    relationship = db.Column(db.Text)
    birthdate = db.Column(db.Text)
    birthplace = db.Column(db.Text)
    deathdate = db.Column(db.Text)
    deathplace = db.Column(db.Text)
    plot = db.Column(db.Text)
    fag_id = db.Column(db.Text)
    fag_url = db.Column(db.Text)
    notes = db.Column(db.Text)
    obituary = db.Column(db.Text)
    pictureURL = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # Forign Key
    cemeteriesfk = db.Column(
        db.Integer, db.ForeignKey("cemeteries.id", ondelete="CASCADE"), nullable=False
    )


class Cemeteries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    address = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip = db.Column(db.Text)
    phone = db.Column(db.Text)
    url = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # relationships
    graves = db.relationship("Graves", backref="cemeteries", passive_deletes=True)


class Insinfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    phone = db.Column(db.Text)
    policynum = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class APIKeys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    key = db.Column(db.Text)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class VehicleRecalls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetimechecked = db.Column(db.DateTime)
    recallcount = db.Column(db.Integer)
    message = db.Column(db.Text)
    vehicleid = db.Column(db.Integer)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class Recalls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recallid = db.Column(db.Integer)
    summary = db.Column(db.Text)
    conequence = db.Column(db.Text)
    remedy = db.Column(db.Text)
    notes = db.Column(db.Text)
    reportdate = db.Column(db.DateTime)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


# Mileage
class Mileage_catagory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catagoryname = db.Column(db.Text)
    description = db.Column(db.Text)
    pricepermile = db.Column(db.Float)
    imgcode = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    miles = db.relationship("Mileage", backref="mileage_catagory")


class Mileage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    legnumber = db.Column(db.Float)
    addressoriginfk = db.Column(db.Text)
    originfk = db.Column(db.Integer)
    addressdestinationfk = db.Column(db.Text)
    destinationfk = db.Column(db.Integer)
    providerfk = db.Column(db.Integer)
    mileage = db.Column(db.Integer)
    tripnumber = db.Column(db.Text)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    catagoryfk = db.Column(db.Integer, ForeignKey("mileage_catagory.id"))
    threeway = db.Column(db.Boolean)
    returnleg = db.Column(db.Boolean)
    tripprice = db.Column(db.Float)
    notes = db.Column(db.Text)
    # filters
    needTripNumber = db.Column(db.Boolean, default=True)
    needTripNumber_when = db.Column(db.DateTime)
    tosend = db.Column(db.Boolean, default=True)
    tosend_when = db.Column(db.DateTime)
    printed = db.Column(db.Boolean, default=False)
    printed_when = db.Column(db.DateTime)
    sent = db.Column(db.Boolean, default=False)
    sent_when = db.Column(db.DateTime)
    finished = db.Column(db.Boolean, default=False)
    finished_when = db.Column(db.DateTime)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    cats = db.relationship("Mileage_catagory", backref="mileage", lazy="select")


# Money
class Payees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    address = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10))
    dueDate = db.Column(db.Date)
    amount = db.Column(db.Float)
    reoccuring = db.Column(db.Boolean)
    onetime = db.Column(db.Boolean)
    active = db.Column(db.Boolean)
    billingwebsite = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # Relationships
    billdate = db.relationship("BillDates", backref="payees", passive_deletes=True)
    # forign keys
    catagory = db.Column(db.Integer, db.ForeignKey("budgetcats.id", ondelete="CASCADE"))


class BillDates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payeefk = db.Column(
        db.Integer, db.ForeignKey("payees.id", ondelete="CASCADE"), nullable=True
    )
    amount = db.Column(db.Float)
    dueDate = db.Column(db.Date)
    paid = db.Column(db.Boolean)
    paidDate = db.Column(db.Date)
    paidHow = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


# Budget
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_start = db.Column(db.Date)
    date_end = db.Column(db.Date)
    monthyear = db.Column(db.Integer, unique=True)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class BudgetExpenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duedate = db.Column(db.Date)
    amount = db.Column(db.Float)
    notes = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # forign-keys
    catagory = db.Column(
        db.Integer, db.ForeignKey("budgetcats.id", ondelete="CASCADE"), nullable=False
    )
    budget = db.Column(
        db.Integer, db.ForeignKey("budget.id", ondelete="CASCADE"), nullable=False
    )


class BudgetIncome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    amount = db.Column(db.Float)
    notes = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # forign keys
    catagory = db.Column(
        db.Integer, db.ForeignKey("budgetcats.id", ondelete="CASCADE"), nullable=False
    )
    budget = db.Column(
        db.Integer, db.ForeignKey("budget.id", ondelete="CASCADE"), nullable=False
    )


class Budgetcats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catagory = db.Column(db.Text)
    exp = db.Column(db.Boolean)
    inc = db.Column(db.Boolean)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # Relationships
    income = db.relationship("BudgetIncome", backref="budgetcats", passive_deletes=True)
    expenses = db.relationship(
        "BudgetExpenses", backref="budgetcats", passive_deletes=True
    )


# Calendar Holidays
class CalHolidays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    holiday = db.Column(db.Text)
    national = db.Column(db.Boolean)
    personal = db.Column(db.Boolean)
    wknum = db.Column(db.Integer)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


# Productivity
class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100))
    project_description = db.Column(db.Text)
    review_howOften = db.Column(db.Integer)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # Relationships
    tasks_rel = db.relationship("Tasks", backref="projects", lazy=True)
    # Forign Keys


class Goals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(100))
    goal_description = db.Column(db.Text)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # Relationships
    tasks_rel = db.relationship("Tasks", backref="goals", lazy=True)
    # Forign Keys


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100))
    done = db.Column(db.Boolean, default=False)
    userid = db.Column(db.Integer)
    update_time = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # Forign Keys
    projectfk = db.Column(db.Integer, db.ForeignKey("projects.id"))
    goalfk = db.Column(db.Integer, db.ForeignKey("goals.id"))
    # Relationships
    project_rel = db.relationship("Projects", backref="tasks", lazy=True)
    goal_rel = db.relationship("Goals", backref="tasks", lazy=True)


# Template
# class <ModelName>(db.Model):
#     id = db.Column(db.Integer, primary_key=True)

#     userid = db.Column(db.Integer)
#     update_time = db. Column (db. DateTime, default=datetime.datetime.now,onupdate=datetime.datetime.now)
#     date_created = db.Column(db.DateTime(timezone=True), default=func.now())
#     # Relationships
#     #Forign Keys
