import flask_login
from dateutil.relativedelta import relativedelta
from website import db
from website.models import *
from flask_login import current_user
from flask import flash

def sdem(dayofmonth, startdate, name, amount, cat):
    yr = startdate.split("-")[0]
    mnth = startdate.split("-")[1]

    budgets = db.session.query(Budget).filter(Budget.userid == current_user.id).filter(Budget.date_start >= datetime.date(int(yr),int(mnth),1)).all()
    
    for budget in budgets:
        duedatenew = datetime.date(budget.date_start.year,budget.date_start.month,int(dayofmonth))
        new = BudgetExpenses(
            duedate = duedatenew,
            amount = amount,
            notes = name,
            userid = current_user.id,
            catagory = cat,
            budget = budget.id,
        )
        db.session.add(new)
        db.session.commit()

def ewo(everyweekon, startdate, name, amount, cat):
    yr = startdate.split("-")[0]
    mnth = startdate.split("-")[1]
    dy = startdate.split("-")[2]
    
    startdate = datetime.datetime.strptime(startdate,'%Y-%m-%d')
    dayofweek = startdate.weekday()
    budgets = db.session.query(Budget).filter(Budget.userid == current_user.id).filter(Budget.date_start >= datetime.date(int(yr),int(mnth),int(dy))).all()
    
    if dayofweek == int(everyweekon):
        duedatenew = startdate
    else:
        invdays = (int(everyweekon) - startdate.weekday()) % 7
        duedatenew = startdate + datetime.timedelta(days=invdays)
        
    for budget in budgets:
        mth = budget.date_start.month
        while duedatenew.month == mth:
            new = BudgetExpenses(
                duedate = duedatenew,
                amount = amount,
                notes = name,
                userid = current_user.id,
                catagory = cat,
                budget = budget.id,
            )
            db.session.add(new)
            db.session.commit()
        
            duedatenew = duedatenew + datetime.timedelta(days=7)

def eowo(everyotherweekon, startdate, name, amount, cat):
    yr = startdate.split("-")[0]
    mnth = startdate.split("-")[1]
    dy = startdate.split("-")[2]
    
    startdate = datetime.datetime.strptime(startdate,'%Y-%m-%d')
    dayofweek = startdate.weekday()
    budgets = db.session.query(Budget).filter(Budget.userid == current_user.id).filter(Budget.date_start >= datetime.date(int(yr),int(mnth),int(dy))).all()
    
    if dayofweek == int(everyotherweekon):
        duedatenew = startdate
    else:
        invdays = (int(everyotherweekon) - startdate.weekday()) % 7
        duedatenew = startdate + datetime.timedelta(days=invdays)
        
    for budget in budgets:
        mth = budget.date_start.month
        while duedatenew.month == mth:
            new = BudgetExpenses(
                duedate = duedatenew,
                amount = amount,
                notes = name,
                userid = current_user.id,
                catagory = cat,
                budget = budget.id,
            )
            db.session.add(new)
            db.session.commit()
        
            duedatenew = duedatenew + datetime.timedelta(days=14)
            


def one_time(name, cat, duedate, amount):
    yr = duedate.split("-")[0]
    mnth = duedate.split("-")[1]

    newduedate = datetime.datetime.strptime(duedate,"%Y-%m-%d")    
    budget = db.session.query(Budget).filter(Budget.userid == current_user.id).filter(Budget.date_start == datetime.date(int(yr),int(mnth),1)).first().id
    new = BudgetExpenses(
        duedate = newduedate,
        amount = amount,
        notes = name,
        userid = current_user.id,
        catagory = cat,
        budget = budget,
    )
    db.session.add(new)
    db.session.commit()
    
    
def add_payee(name, active, address, city, state, zip, website, type, duedate, amount, startdate, samedayeverymonth, weekselect, dayofweek, everyweekon, everyotherweekon, when, cat):
    dup = db.session.query(Payees).filter(Payees.name == name).filter(Payees.userid == current_user.id).count()
    if dup == 0:
        if type == "reoccuring":
            duedate = startdate
            reoccuring = True 
            onetime=False
            if when == 'sdem': #samedayeverymonth
                sdem(samedayeverymonth, startdate, name, amount, cat)
            elif when == 'ewo': #everyweekon
                ewo(everyweekon, startdate, name, amount, cat)
            elif when == 'exdoem': #TODO:Every x day of each month
                pass
            elif when == 'eowo': # Every Other week on
                eowo(everyotherweekon, startdate, name, amount, cat)
        
        elif type == "onetime":
            reoccuring = False 
            onetime=True
            one_time(name, cat, duedate, amount)
        
        if active == 'active':
            active_result = True
        else:
            active_result = False
        
        newpayee = Payees(
            name = name,
            address = address,
            city = city,
            state = state,
            zip = zip,
            userid = current_user.id,
            dueDate = datetime.datetime.strptime(duedate,('%Y-%m-%d')),
            amount = float(amount),
            reoccuring = reoccuring,
            onetime = onetime,
            active = active_result,
            billingwebsite = website,
            catagory = cat
        )
        db.session.add(newpayee)
        db.session.commit()
    else:
        flash(f"A record named {name} is already exists.  Please edit that record.",category = 'error')
        
def budget_check_dates():
    """Check to see if there is at least 12
    records or months coming up.  If not, add 
    records to get to 12.  If so, pass"""

    cnt = db.session.query(Budget).filter(Budget.userid == flask_login.current_user.id).count()
    if cnt <= 12:
        budget_add_dates(12-cnt)

def budget_add_dates(cnt):
    import calendar
    
    for _ in range(cnt):
        lastrecord = db.session.query(func.max(Budget.date_end).label('MaxDate')).first()
        if lastrecord.MaxDate == None:
            rightnow = datetime.datetime.now()
            date = datetime.date(rightnow.year,rightnow.month,1)
        else:
            date = lastrecord.MaxDate + relativedelta(days=1)
            
        thismonth = date.month
        thisyear = date.year
        lastday = calendar.monthrange(thisyear, thismonth)[1]
        startdt = datetime.date(thisyear,thismonth,1)
        enddt = datetime.date(thisyear,thismonth,lastday)
        
        newdate = Budget(
            date_start = startdt,
            date_end = enddt,
            monthyear = int(str(thismonth)+str(thisyear)),
            userid = flask_login.current_user.id
        )
        db.session.add(newdate)
        db.session.commit()
        
def add_to_budget(id, expcat=None, expamount=None, expsource=None, inccat=None, incamount=None, incsource=None, expduedate=None, incdate=None):
    if expcat != None:
        if expduedate == '':
            expdate = None
        else:
            expdate = datetime.datetime.strptime(expduedate, "%Y-%m-%d")
        
        item = BudgetExpenses(
            duedate = expdate,
            amount = expamount,
            notes = expsource,
            userid = current_user.id,
            catagory = expcat,
            budget = id
        )
    else:
        if incdate == '':
            incomedate = None
        else:
            incomedate = datetime.datetime.strptime(incdate, "%Y-%m-%d")
        
        item = BudgetIncome(
            date = incomedate,
            amount = incamount,
            notes = incsource,
            userid = current_user.id,
            catagory = inccat,
            budget = id
        )
    db.session.add(item)
    db.session.commit()
    
def add_catagory(type, catagory):
    if type == 'exp':
        exp = True
        inc = False
    else:
        inc = True
        exp = False
        
    new = Budgetcats(
        inc = inc,
        exp = exp,
        catagory = catagory,
        userid = current_user.id
    )
    db.session.add(new)
    db.session.commit()
        