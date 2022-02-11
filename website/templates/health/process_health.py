import flask_login
from website import db
from website.models import *
from sqlalchemy.sql import desc
from datetime import timedelta

def get_fulldisplayname(prefix, firstname, middleinit, lastname, suffix):
    if prefix: name = f'{prefix} '
    else: name = f''
    if firstname: name = f'{name}{firstname} '
    else: name =f'{name}'
    if middleinit: name = f'{name}{middleinit} '
    else: name = f'{name}'
    if lastname and suffix: name = f'{name}{lastname}, '
    elif lastname and not suffix: name = f'{name}{lastname} '
    else: name = f'{name}'
    if suffix: name = f'{name}{suffix}'
    else: name = f'{name}'
    return name

def get_shortdisplayname(firstname, lastname):
    name = ""
    if firstname: name = f'{firstname} '
    else: name =f'{name}'
    if lastname: name = f'{name}{lastname}'
    else: name = f'{name}'
    return name

def add_doctor(prefix, firstname, lastname, middleinit, suffix, facility, address, city, state, zip, phone, email, asst, thisuserid, doctorbtn=''):
    newdr = Doctor(
        prefix = prefix,
        firstname = firstname,
        lastname = lastname, 
        middleinit = middleinit,
        suffix = suffix,
        fulldisplayname = get_fulldisplayname(prefix, firstname, lastname, middleinit, suffix),
        shortdisplayname = get_shortdisplayname(firstname, lastname),
        address = address,
        city = city,
        state = state,
        zip = zip,
        phone = phone, 
        email = email, 
        userid = thisuserid,
        asst = asst,
        facilityfk = facility
    )
    db.session.add(newdr)
    db.session.commit()
    
def update_doctor(id, prefix, firstname, middleinit, lastname, suffix, drname, facility, address, city, state, zip, phone, email, asst, thisuserid, docSubmit):
    editDr = db.session.query(Doctor).filter(Doctor.id == id).first()
    editDr.prefix=prefix
    editDr.firstname=firstname
    editDr.middleinit=middleinit
    editDr.lastname=lastname
    editDr.suffix=suffix
    editDr.fulldisplayname = get_fulldisplayname(prefix, firstname, middleinit, lastname, suffix)
    editDr.shortdisplayname = get_shortdisplayname(firstname, lastname)
    editDr.facilityfk=facility
    editDr.userid=thisuserid
    editDr.address=address
    editDr.city=city
    editDr.state=state
    editDr.zip=zip
    editDr.phone=phone
    editDr.email=email
    editDr.asst=asst
    db.session.commit()
    
def calculateAge(startdate):
    bday = flask_login.current_user.dob
    age = startdate.year - bday.year
    return age
    
def update_surgeries(id, name, sdate, bodypart, desc, doctor, facility, thisuserid):
    editSurg = db.session.query(Surgeries).filter_by(id=id).first()
    editSurg.name = name.title()
    editSurg.startdate = datetime.datetime.strptime(sdate,"%Y-%m-%d")
    editSurg.body_part = bodypart.title()
    editSurg.description = desc.title()
    editSurg.doctorfk = doctor
    editSurg.facilityfk = facility
    editSurg.age = calculateAge(datetime.datetime.strptime(sdate,"%Y-%m-%d"))
    db.session.commit()
    
def make_vfc(info):
    nameforfn = info.name.replace(" ", "").replace(".","").lower()
    splitname = info.name.split()
    last_name = splitname[-1]
    first_name = splitname[int(len(splitname) / 2)]
    title = splitname[0]
    filename = nameforfn + ".vcf"
    with open ("website/"+filename, 'w') as file:
        file.write("BEGIN:VCARD\nVERSION:3.0\nPRODID:-//Apple Inc.//macOS 12.0//EN\n")
        file.write("N:" + last_name + ";" + first_name + ";;" + title + ";\n")
        file.write("FN:" + info.name + "\n")
        file.write("item1.EMAIL;type=INTERNET;type=pref:" + info.email + "\n")
        file.write("ORG:"+info.company+"\n")
        file.write("TEL;type=WORK;type=VOICE;type=pref:" + info.phone + "\n")
        file.write("ADR;type=WORK;type=pref:;;" + info.address + ";" + info.city + ";" + info.state + ";" + info.zip + ";United States\n")
        file.write("END:VCARD")
    return filename

def make_ics(fullname, cal):
    with open(fullname, 'w') as my_file:
        my_file.write('BEGIN:VCALENDAR\nVERSION:2.0\n')
        my_file.write('X-WR-CALNAME:'+ cal + "\n")
    
def details_ics(med, fullname):
    with open (fullname, 'a') as my_file:
        startdate = datetime.datetime.strftime(med.next_refill,"%Y%m%d")
        enddate = datetime.datetime.strftime(med.next_refill + timedelta(days=1),"%Y%m%d")
        MedName = med.name
        TaskName = "Call to Order " + MedName
        PickupDate = datetime.datetime.strftime(med.next_refill,"%m-%d-%Y")
        Pharmacy = db.session.query(Facility).filter(Facility.id  == med.pharmacy).first().name
        
        my_file.write('BEGIN:VEVENT\n')
        my_file.write('SUMMARY:' + TaskName +"\n")
        my_file.write('LOCATION:' + Pharmacy +"\n")
        my_file.write('DESCRIPTION:' + "Call " + Pharmacy + " to request a refill of " + MedName + " to be picked up on " + PickupDate + "\n")
        my_file.write('DTSTART;VALUE=DATE:'+ str(startdate) +"\n")
        my_file.write('DTEND;VALUE=DATE:'+ str(enddate) +"\n")
        my_file.write('END:VEVENT\n')

def close_ics(path,filename,fullname):
    with open (fullname, 'a') as my_file:
        my_file.write('END:VCALENDAR')

        
        
def make_tasks(med):
    Pharmacy = db.session.query(Facility).filter(Facility.id  == med.pharmacy).first().name
    MedName = med.name
    PickupDate = med.next_refill
    Project = db.session.query(Projects).filter(Projects.name == "Medical").first().id
    
    newtask = Tasks(
        item = "Call " + Pharmacy + " to request a refill of " + MedName + " to be picked up on " + PickupDate.strftime('%m-%d-%Y'),
        userid = current_user.id,
        project = Project,
        duedate = PickupDate
    )
    db.session.add(newtask)
    db.session.commit()


def set_process_to_no(med):
    medication = db.session.query(Medications).filter(Medications.id == med.id).first()
    medication.process = False
    db.session.commit()