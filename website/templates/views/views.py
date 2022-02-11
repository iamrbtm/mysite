from flask import Blueprint, render_template, request, redirect, url_for
from flask.helpers import flash
from flask_login import login_required
from website.models import *
from website.templates.views.process_views import *
from datetime import datetime, timedelta
from website import db
from sqlalchemy.sql import func
import datetime, flask_login, json
from dateutil.relativedelta import relativedelta
from math import ceil

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    weeknum = datetime.datetime.now().isocalendar()[1]
    currentvalue = db.session.query(func.max(A1C.date).label('ld'), A1C.testresult, A1C.userid).filter(A1C.userid == flask_login.current_user.id).order_by(A1C.date).first()
    if currentvalue.testresult is None:
        eag=0
    else:
        eag = ceil(28.7 * currentvalue.testresult - 46.7)
    
    cntProjects = db.session.query(Projects).filter(Projects.userid == flask_login.current_user.id).filter(Projects.next_review <= datetime.datetime.now()).filter(Projects.status != "Complete").count()
    cntMeds = db.session.query(Medications).filter(Medications.next_refill <= datetime.datetime.now()+timedelta(days=5)).filter(Medications.userid == flask_login.current_user.id).count()
    cntTasks = db.session.query(Tasks.id, Tasks.duedate, Tasks.checked, Tasks.item, Tasks.project, Tasks.userid, Projects.name.label('nameOfProject')).join(Projects, Projects.id == Tasks.project).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.duedate <= (datetime.datetime.today()+timedelta(days=2))).filter(Tasks.checked==False).order_by(Tasks.duedate.desc(), Tasks.project).count()
    cntA1C = db.session.query(A1C).filter(A1C.userid == flask_login.current_user.id).limit(1).count()
    cntCpap = db.session.query(Cpap).filter(Cpap.nextorderdate <= datetime.datetime.now()+timedelta(days=5)).filter(Cpap.userid == flask_login.current_user.id).count()
    cntMenu = db.session.query(Planner).filter(Planner.wknum == weeknum).count()
    projects = db.session.query(Projects).filter(Projects.userid == flask_login.current_user.id).filter(Projects.next_review <= datetime.datetime.now()).filter(Projects.status != "Complete").all()
    tasks = db.session.query(Tasks.id, Tasks.duedate, Tasks.checked, Tasks.item, Tasks.project, Tasks.userid, Projects.name.label('nameOfProject')).join(Projects, Projects.id == Tasks.project).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.duedate <= (datetime.datetime.today()+timedelta(days=2))).filter(Tasks.checked==False).order_by(Tasks.duedate.desc(), Tasks.project).all()
    plans = db.session.query(Planner).filter(Planner.wknum == weeknum).order_by(Planner.wknum, Planner.dayofwk).limit(7)
    items = Recipe.query.order_by(Recipe.dishfk).all()
    plandish = db.session.query(PlanDish).filter(PlanDish.wknum == weeknum).all()
    dishlist = Dish.query.order_by(Dish.name).all()
    firstdow = db.session.query(Planner).filter(Planner.dayofwk==0, Planner.wknum == int(weeknum)).first().date.strftime("%B %d, %Y")
    lastdow = db.session.query(Planner).filter(Planner.dayofwk==6, Planner.wknum == int(weeknum)).first().date.strftime("%B %d, %Y")
    holidays = db.session.query(CalHolidays).filter(CalHolidays.wknum == weeknum).all()
    meds = db.session.query(Medications).filter(Medications.next_refill <= (datetime.datetime.today()+timedelta(days=5))).filter(Medications.userid == flask_login.current_user.id).order_by(Medications.next_refill).all()
    cpaps = db.session.query(Cpap).filter(Cpap.nextorderdate <= datetime.datetime.now()+timedelta(days=5)).filter(Cpap.userid == flask_login.current_user.id).all()
    return render_template("views/home.html", user=User, meds=meds, currentvalue=currentvalue, eag=eag, plans=plans, tasks=tasks, projects=projects, cntTasks=cntTasks, cntMeds=cntMeds, cntProjects=cntProjects, cntA1C=cntA1C, cntCpap=cntCpap, cpaps=cpaps, cntMenu=cntMenu, items=items, plandish=plandish, dishes=dishlist, holidays=holidays, firstdow=firstdow, lastdow=lastdow)


@views.route("/profile", methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        profile = db.session.query(User).filter(User.id == flask_login.current_user.id).first()
        profile.firstname = request.form.get('firstname')
        profile.lastname = request.form.get('lastname')
        profile.address = request.form.get('address')
        profile.city = request.form.get('city')
        profile.state = request.form.get('state')
        profile.zip = request.form.get('zip')
        profile.phone = request.form.get('phone')
        profile.email = request.form.get('email')
        profile.username = request.form.get('un')
        profile.password = request.form.get('pw')
        profile.avatar_filename = filename
        db.session.commit()

        return redirect(url_for("views.profile"))
        
    states = db.session.query(States).all()
    profile = db.session.query(User).filter(User.id == flask_login.current_user.id).first()
    return render_template('views/profile.html', user=User, profile=profile, states=states)

@views.route('/updatepa')
@login_required
def update_pa():
    rest = console_update()
    rest = json.loads(rest)
    if rest['status'] == "OK":
        flash("Python Anywhere sucessfully updated", category='success')
    else:
        flash(f"Something happened and Python Anywhere wasnt able to update. {rest}", category="error")
    return redirect(url_for('views.home'))

@views.route('/importholidays<year>')
@login_required
def holidays(year):
    from website.templates.menu.process_menu import get_holidays
    get_holidays(year)
    return redirect(url_for('views.home'))

@views.route('/specialdates', methods=['GET','POST'])
@login_required
def special_dates():
    def addToDB(date, title):
        dt = datetime.datetime.strptime(date,"%Y-%m-%d")
        newdate = CalHolidays(
            date = dt,
            holiday = title,
            personal = True,
            national = False,
            wknum = dt.isocalendar()[1],
            userid = flask_login.current_user.id
            )
        db.session.add(newdate)
        db.session.commit()
        
    if request.method == 'POST':
        # all = request.form.to_dict()
        # print(all)
        if request.form.get('rep') == 'on':
            howoften = request.form.get('gridRadios')
            if howoften == "Yearly":
                startdate = datetime.datetime.strptime(request.form.get('date'),"%Y-%m-%d")
                holiday = request.form.get('holiday')
                i=0
                
                if "Birthday" in holiday:
                    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
                    ages = [ordinal(n) for n in range(0,85)]
                    
                    for age in ages:
                        dt = startdate + relativedelta(years=i)
                        dt = datetime.datetime.strftime(dt,"%Y-%m-%d")
                        title = holiday[:holiday.index(' ')] + " " + age + " Birthday"
                        addToDB(dt,title)
                        i+=1
                else:
                    for _ in range(0,85):
                        dt = startdate + relativedelta(years=i)
                        dt = datetime.datetime.strftime(dt,"%Y-%m-%d")
                        addToDB(dt,holiday)
                        i+=1
                
            elif howoften == "Monthly":
                startdate = datetime.datetime.strptime(request.form.get('date'),"%Y-%m-%d")
                holiday = request.form.get('holiday')
                i=0
                
                for _ in range(0,96):
                    dt = startdate + relativedelta(months=i)
                    dt = datetime.datetime.strftime(dt,"%Y-%m-%d")
                    addToDB(dt,holiday)
                    i+=1
        else:
            addToDB(request.form.get('date'),request.form.get('holiday'))
        
    specialdates = CalHolidays.query.filter(CalHolidays.date >= datetime.datetime.today()).order_by(CalHolidays.date).all()
    return render_template('views/specialdates.html', user=User, specialdates=specialdates)


@views.route('/editdocs', methods=['GET'])
@login_required
def editdocs():
    return render_template('views/editdocs.html', user=User)

@views.route('/xfer')
def xfer():
    from website.xfer import xfer
    xfer()
    return 'done'