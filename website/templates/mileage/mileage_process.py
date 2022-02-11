import flask_login
from website import db
from website.models import *
import requests, json, re
import pdfrw
from sqlalchemy.sql import desc
from flask import send_file 
from fillpdf import fillpdfs
from website.templates.health.process_health import *

    
def add_catagory(svg, catagoryname, desc, price, thisuserid, catagorybtn):
    newcat = MileageCatagory(
        catagoryname = catagoryname,
        description = desc,
        pricepermile = float(price),
        imgcode = svg,
        userid = flask_login.current_user.id
    )
    db.session.add(newcat)
    db.session.commit()
    
def add_facility(name, addy, city, state, zip, type, phone, thisuserid, facilitybtn):
    newfac = Facility(
        name = name,
        address = addy,
        city = city,
        state = state,
        zip = zip,
        phone = phone, 
        type = type,
        userid = thisuserid
    )
    db.session.add(newfac)
    db.session.commit()
    
def get_address(id):
    record = db.session.query(Facility).filter_by(id=id).first()
    address = record.address +" "+ record.city +", "+ record.state +" "+ record.zip
    return address

def threewaytrip(item):
    if item == "threeway":
        return True
    else:
        return False
    
def returnlegtrip(item):
    if item == "returnleg":
        return True
    else:
        return False

def onewaylegtrip(item):
    if item == "oneway":
        return True
    else:
        return False
    
def googlereadyaddress(id):
    address = get_address(id)
    address = address.replace(' ','+')
    address = address + "+USA"
    return address
    
def get_mileage(origin_address, destination_address):
    key = db.session.query(APIKeys.key).filter(APIKeys.name == 'googledistance').first().key
    url =  f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin_address}&destinations={destination_address}&mode=auto&language=en&units=imperial&key="+key
    request = requests.request("GET",url)
    fulljson = json.loads(request.text)
    with open('fulljson.json', 'w') as file:
        file.write(json.dumps(request.text))
    miles = re.findall('\d*\.?\d+',fulljson['rows'][0]['elements'][0]['distance']['text'])
    return float(miles[0])
    
def add_oneway_reservation(date, time, tripnum, origin, dest, catagory, whom, thisuserid, reservation, tripoption, notes):
    #firstleg / original trip
    mileage = get_mileage(googlereadyaddress(origin),googlereadyaddress(dest))
    price = mileage * float(db.session.query(MileageCatagory).filter_by(id = catagory).first().pricepermile)
    originalres = Mileage(
        addressoriginfk = get_address(origin),
        originfk = origin,
        addressdestinationfk = get_address(dest),
        destinationfk = dest,
        providerfk = whom,
        mileage = mileage,
        tripnumber = tripnum,
        date = datetime.datetime.strptime(date, "%Y-%m-%d"),
        time = datetime.time(datetime.datetime.strptime(time, "%H:%M").hour,datetime.datetime.strptime(time, "%H:%M").minute),
        catagoryfk = catagory,
        threeway = threewaytrip(tripoption),
        returnleg = returnlegtrip(tripoption),
        onewayleg = onewaylegtrip(tripoption),
        tripprice = price,
        needTripNumber = True,
        needTripNumber_when = datetime.datetime.now(),
        tosend = False,
        printed = False,
        sent = False,
        finished = False,
        userid = thisuserid
        )
    db.session.add(originalres)
    db.session.commit()
    db.session.refresh(originalres)
    originalres.legnumber = originalres.id
    db.session.commit()

def add_roundtrip_reservation(date, time, tripnum, origin, dest, catagory, whom, thisuserid, reservation, tripoption, notes):
    #firstleg / original trip
    mileage = get_mileage(googlereadyaddress(origin),googlereadyaddress(dest))
    price = mileage * float(db.session.query(MileageCatagory).filter_by(id = catagory).first().pricepermile)
    originalres = Mileage(
        addressoriginfk = get_address(origin),
        originfk = origin,
        addressdestinationfk = get_address(dest),
        destinationfk = dest,
        providerfk = whom,
        mileage = mileage,
        tripnumber = tripnum,
        date = datetime.datetime.strptime(date, "%Y-%m-%d"),
        time = datetime.time(datetime.datetime.strptime(time, "%H:%M").hour,datetime.datetime.strptime(time, "%H:%M").minute),
        catagoryfk = catagory,
        threeway = threewaytrip(tripoption),
        returnleg = returnlegtrip(tripoption),
        tripprice = price,
        needTripNumber = True,
        needTripNumber_when = datetime.datetime.now(),
        tosend = False,
        printed = False,
        sent = False,
        finished = False,
        notes = notes,
        userid = thisuserid
        )
    db.session.add(originalres)
    db.session.commit()
    db.session.refresh(originalres)
    originalres.legnumber = originalres.id
    db.session.commit()
    
    #return leg of trip
    if tripoption == 'returnleg':
        mileage = get_mileage(googlereadyaddress(dest),googlereadyaddress(origin))
        price = mileage * float(db.session.query(MileageCatagory).filter_by(id = catagory).first().pricepermile)
        returntrip = Mileage(
            addressoriginfk = get_address(dest),
            originfk = dest,
            addressdestinationfk = get_address(origin),
            destinationfk = origin,
            providerfk = whom,
            mileage = get_mileage(googlereadyaddress(dest),googlereadyaddress(origin)),
            tripnumber = tripnum,
            date = datetime.datetime.strptime(date, "%Y-%m-%d"),
            time = datetime.time(datetime.datetime.strptime(time, "%H:%M").hour,datetime.datetime.strptime(time, "%H:%M").minute),
            catagoryfk = catagory,
            threeway = threewaytrip(tripoption),
            returnleg = returnlegtrip(tripoption),
            tripprice = price,
            needTripNumber = True,
            needTripNumber_when = datetime.datetime.now(),
            tosend = False,
            printed = False,
            sent = False,
            finished = False,
            userid = thisuserid
            )
        db.session.add(returntrip)
        db.session.commit()
        db.session.refresh(returntrip)
        legnum = "%s%s" % (originalres.id , ".11")
        returntrip.legnumber = float(legnum)

        db.session.commit()
        
def add_threeway_reservation(date, tripnum, origin, dest2, catagory2, whom2, time2, time, dest, catagory, whom, thisuserid, reservation, tripoption, notes):
    #firstleg / original trip
    mileage = get_mileage(googlereadyaddress(origin),googlereadyaddress(dest))
    price = mileage * float(db.session.query(MileageCatagory).filter_by(id = catagory).first().pricepermile)
    originalres = Mileage(
        addressoriginfk = get_address(origin),
        originfk = origin,
        addressdestinationfk = get_address(dest),
        destinationfk = dest,
        providerfk = whom,
        mileage = mileage,
        tripnumber = tripnum,
        date = datetime.datetime.strptime(date, "%Y-%m-%d"),
        time = datetime.time(datetime.datetime.strptime(time, "%H:%M").hour,datetime.datetime.strptime(time, "%H:%M").minute),
        catagoryfk = catagory,
        threeway = threewaytrip(tripoption),
        returnleg = returnlegtrip(tripoption),
        tripprice = price,
        needTripNumber = True,
        needTripNumber_when = datetime.datetime.now(),
        tosend = False,
        printed = False,
        sent = False,
        finished = False,
        userid = thisuserid,
        notes = notes
        )
    db.session.add(originalres)
    db.session.commit()
    db.session.refresh(originalres)
    originalres.legnumber = originalres.id
    db.session.commit()
    
    #middle leg
    mileage = get_mileage(googlereadyaddress(dest),googlereadyaddress(dest2))
    price = mileage * float(db.session.query(MileageCatagory).filter_by(id = catagory2).first().pricepermile)
    middleleg = Mileage(
        addressoriginfk = get_address(dest),
        originfk = dest,
        addressdestinationfk = get_address(dest2),
        destinationfk = dest2,
        providerfk = whom2,
        mileage = mileage,
        tripnumber = tripnum,
        date = datetime.datetime.strptime(date, "%Y-%m-%d"),
        time = datetime.time(datetime.datetime.strptime(time2, "%H:%M").hour,datetime.datetime.strptime(time2, "%H:%M").minute),
        catagoryfk = catagory2,
        threeway = threewaytrip(tripoption),
        returnleg = returnlegtrip(tripoption),
        tripprice = price,
        needTripNumber = True,
        needTripNumber_when = datetime.datetime.now(),
        tosend = False,
        printed = False,
        sent = False,
        finished = False,
        userid = thisuserid
        )
    db.session.add(middleleg)
    db.session.commit()
    db.session.refresh(middleleg)
    legnum = "%s%s" % (originalres.id , ".10")
    middleleg.legnumber = float(legnum)
    db.session.commit()
    

    
    #return leg
    mileage = get_mileage(googlereadyaddress(dest2),googlereadyaddress(origin))
    price = mileage * float(db.session.query(MileageCatagory).filter_by(id = catagory2).first().pricepermile)
    returnleg = Mileage(
        addressoriginfk = get_address(dest2),
        originfk = dest2,
        addressdestinationfk = get_address(origin),
        destinationfk = origin,
        providerfk = whom2,
        mileage = mileage,
        tripnumber = tripnum,
        date = datetime.datetime.strptime(date, "%Y-%m-%d"),
        time = datetime.time(datetime.datetime.strptime(time2, "%H:%M").hour,datetime.datetime.strptime(time2, "%H:%M").minute),
        catagoryfk = catagory2,
        threeway = threewaytrip(tripoption),
        returnleg = returnlegtrip(tripoption),
        tripprice = price,
        needTripNumber = True,
        needTripNumber_when = datetime.datetime.now(),
        tosend = False,
        printed = False,
        sent = False,
        finished = False,
        userid = thisuserid
        )
    db.session.add(returnleg)
    db.session.commit()
    db.session.refresh(returnleg)
    legnum = "%s%s" % (originalres.id , ".11")
    returnleg.legnumber = float(legnum)

    db.session.commit()
    
def set_flag(id):
    updateflag = db.session.query(Mileage).filter_by(id = id).first()
    if updateflag.needTripNumber == True \
        and updateflag.tosend == False \
        and updateflag.printed == False \
        and updateflag.sent == False:
            if updateflag.tripnumber != "":
                updateflag.tosend = True
                updateflag.tosend_when = datetime.datetime.now()
                updateflag.needTripNumber = False
    elif updateflag.needTripNumber == False \
        and updateflag.tosend == True \
        and updateflag.printed == False \
        and updateflag.sent == False:
            if updateflag.tripnumber != "":
                updateflag.printed = True
                updateflag.printed_when = datetime.datetime.now()
                updateflag.tosend = False
    elif updateflag.needTripNumber == False \
        and updateflag.tosend == False \
        and updateflag.printed == True \
        and updateflag.sent == False:
            if updateflag.tripnumber != "":
                updateflag.sent = True
                updateflag.sent_when = datetime.datetime.now()
                updateflag.printed = False
    elif updateflag.needTripNumber == False \
        and updateflag.tosend == False \
        and updateflag.printed == False \
        and updateflag.sent == True:
            if updateflag.tripnumber != "":
                updateflag.finished = True
                updateflag.finished_when = datetime.datetime.now()
                updateflag.sent == False
    db.session.commit()
    
def pdf_generate_datafile(trips):
    data = {}
    i = 1
    for trip in trips:
        dr = db.session.query(Doctor).filter_by(id=trip.providerfk).first()
        origin = db.session.query(Facility).filter_by(id=trip.originfk).first()
        dest = db.session.query(Facility).filter_by(id=trip.destinationfk).first()
        data[f'TripDateRow{i}'] = str(trip.date.strftime("%m/%d/%y"))
        data[f'TripRow{i}'] = str(trip.tripnumber)
        if "{:.2f}".format(trip.legnumber % 1) == "0.10":
            data[f'MedicalProviderRow{i}'] = "Return Trip"
            data[f'MedicalProviderPhoneRow{i}'] = ""
        else:
            data[f'MedicalProviderRow{i}'] = str(dr.name)
            data[f'MedicalProviderPhoneRow{i}'] = str(dr.phone)
        data[f'ToAddressRow{i}'] = str(dest.name+"\n"+dest.address+"\n"+dest.city+", "+dest.state+" "+dest.zip)
        data[f'FromAddressRow{i}'] = str(origin.name+"\n"+origin.address+"\n"+origin.city+", "+origin.state+" "+origin.zip)
        i += 1
    return data

def fill_pdf(input_pdf_path, output_pdf_path, data_dict):
    ANNOT_KEY = '/Annots'
    ANNOT_FIELD_KEY = '/T'
    ANNOT_VAL_KEY = '/V'
    ANNOT_RECT_KEY = '/Rect'
    SUBTYPE_KEY = '/Subtype'
    WIDGET_SUBTYPE_KEY = '/Widget'
    try:
        template_pdf = pdfrw.PdfReader(input_pdf_path)
        for page in template_pdf.pages:
            annotations = page[ANNOT_KEY]
            for annotation in annotations:
                if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                    if annotation[ANNOT_FIELD_KEY]:
                        key = annotation[ANNOT_FIELD_KEY][1:-1]
                        if key in data_dict.keys():
                            if type(data_dict[key]) == bool:
                                if data_dict[key] == True:
                                    annotation.update(pdfrw.PdfDict(
                                        AS=pdfrw.PdfName('Yes')))
                                    annotation.update(pdfrw.PdfDict(Ff=1))
                            else:
                                annotation.update(
                                    pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                                )
                                annotation.update(pdfrw.PdfDict(AP=''))
        template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
        pdfrw.PdfWriter().write(output_pdf_path, template_pdf)
        
        fillpdfs.flatten_pdf(output_pdf_path, output_pdf_path, as_images=False)
        
        return True
    except:
        return False
    
def edit_catagory(id, catagoryname, description, pricepermile, imgcode):
    record = db.session.query(MileageCatagory).filter_by(id=id).first()
    record.catagoryname = catagoryname
    record.description = description
    record.pricepermile = pricepermile
    record.imgcode = imgcode
    db.session.commit()