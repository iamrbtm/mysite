from website.templates.health.process_health import get_fulldisplayname, get_shortdisplayname
from website import db
from website.models import *

def updatedocs():
    doctors = db.session.query(Doctor).filter_by(userid=2).all()
    
    for doc in doctors:
        doc.fulldisplayname = get_fulldisplayname(doc.prefix, doc.firstname, doc.middleinit, doc.lastname, doc.suffix)
        doc.shortdisplayname = get_shortdisplayname(doc.firstname, doc.lastname)
        db.session.commit()