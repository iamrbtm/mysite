from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from website.models import *
from website import db
from sqlalchemy.sql import func
from website.templates.money.process_money import *

money = Blueprint("money", __name__)

@money.route("/")
@login_required
def home():
    return render_template("money/money.html", user=User)

@money.route("/reports")
@login_required
def reports():
    
    return render_template("money/reports.html", user=User)

@money.route("/payees", methods=['GET','POST'])
@login_required
def payees():
    if request.method == "POST":
        all = request.form.to_dict()
        print(all)
        add_payee(**all)
    
    payees = db.session.query(Payees).filter(Payees.userid == current_user.id).all()
    cats = db.session.query(Budgetcats).filter(Budgetcats.exp == True).filter(Budgetcats.userid == current_user.id).all()
    states = States.query.all()
    context = {'payees':payees, 'user':User, 'states':states, 'cats':cats}
    return render_template("money/payees.html", **context)

@money.route("/budget", methods=['GET','POST'])
@login_required
def budget():
    if request.method == "POST":
        id = request.form.get('budget')
        return redirect(url_for('money.budget_single', id=id))
        
    check = budget_check_dates()
    
    budgets = db.session.query(Budget).filter(Budget.userid == flask_login.current_user.id).all()
    return render_template('money/budget.html', user=User, budgets=budgets)

@money.route("/budget/<id>", methods=['GET','POST'])
@login_required
def budget_single(id):
    
    expenses = db.session.query(BudgetExpenses).filter(BudgetExpenses.userid == flask_login.current_user.id).filter(BudgetExpenses.budget == id).all()
    expensetotal = db.session.query(func.sum(BudgetExpenses.amount)).filter(BudgetExpenses.userid == flask_login.current_user.id).filter(BudgetExpenses.budget == id).scalar()
    incomes = db.session.query(BudgetIncome).filter(BudgetIncome.userid == flask_login.current_user.id).filter(BudgetIncome.budget == id).all()
    incometotal = db.session.query(func.sum(BudgetIncome.amount)).filter(BudgetIncome.userid == flask_login.current_user.id).filter(BudgetIncome.budget == id).scalar()
    allbudgets = db.session.query(Budget).filter(Budget.userid == flask_login.current_user.id).all()
    budget = db.session.query(Budget).filter(Budget.userid == flask_login.current_user.id).filter(Budget.id == id).first()
    cats = db.session.query(Budgetcats).filter(Budgetcats.userid == flask_login.current_user.id).all()
    
    if incometotal == None:
        incometotal = 0.00
    if expensetotal == None:
        expensetotal =0.00
    
    contexts = {'user' : User, 'allbudgets' : allbudgets, 'budget' : budget, 'expenses' : expenses, 'incomes' : incomes, 'cats' : cats, 'incometotal' : incometotal, 'expensetotal' : expensetotal}
    return render_template('money/budget_single.html', **contexts)

@money.route("/budget/update/<id>", methods=['GET','POST'])
@login_required
def budget_single_update(id):
    if request.method == "POST":
        all = request.form.to_dict()
        # print(all)
        add_to_budget(id, **all)
        
    expenses = db.session.query(BudgetExpenses).filter(BudgetExpenses.userid == flask_login.current_user.id).filter(BudgetExpenses.budget == id).all()
    expensetotal = db.session.query(func.sum(BudgetExpenses.amount)).filter(BudgetExpenses.userid == flask_login.current_user.id).filter(BudgetExpenses.budget == id).scalar()
    incomes = db.session.query(BudgetIncome).filter(BudgetIncome.userid == flask_login.current_user.id).filter(BudgetIncome.budget == id).all()
    incometotal = db.session.query(func.sum(BudgetIncome.amount)).filter(BudgetIncome.userid == flask_login.current_user.id).filter(BudgetIncome.budget == id).scalar()
    allbudgets = db.session.query(Budget).filter(Budget.userid == flask_login.current_user.id).all()
    budget = db.session.query(Budget).filter(Budget.userid == flask_login.current_user.id).filter(Budget.id == id).first()
    cats = db.session.query(Budgetcats).filter(Budgetcats.userid == flask_login.current_user.id).all()
    
    if incometotal == None:
        incometotal = 0.00
    if expensetotal == None:
        expensetotal =0.00
    
    contexts = {'user' : User, 'allbudgets' : allbudgets, 'budget' : budget, 'expenses' : expenses, 'incomes' : incomes, 'cats' : cats, 'incometotal' : incometotal, 'expensetotal' : expensetotal}
    return render_template('money/budget_single_update.html', **contexts)

@money.route("/budget/update/<id>/deleteincli/<li>", methods=['GET','POST'])
@login_required
def delete_income_line_item(id, li):
    db.session.query(BudgetIncome).filter_by(id=li).delete()
    db.session.commit()
    return redirect(request.referrer)

@money.route("/budget/update/<id>/deleteexpli/<li>", methods=['GET','POST'])
@login_required
def delete_expense_line_item(id, li):
    db.session.query(BudgetExpenses).filter_by(id=li).delete()
    db.session.commit()
    return redirect(request.referrer)

@money.route('/budget/catagory', methods=['GET','POST'])
@login_required
def catagory():
    if request.method == "POST":
        all = request.form.to_dict()
        add_catagory(**all)
        return redirect(request.referrer)
    expsumtotal = db.session.query(func.sum(BudgetExpenses.amount)).filter(BudgetExpenses.userid == current_user.id).scalar()
    incsumtotal = db.session.query(func.sum(BudgetIncome.amount)).filter(BudgetIncome.userid == current_user.id).scalar()
    
    cats = db.session.query(Budgetcats).filter(Budgetcats.userid == current_user.id).all()
    catscntinc = db.session.query(Budgetcats.id, func.count(BudgetIncome.catagory), func.sum(BudgetIncome.amount)).join(BudgetIncome).filter(Budgetcats.userid == current_user.id).group_by(BudgetIncome.catagory).all()
    catscntexp = db.session.query(Budgetcats.id, func.count(BudgetExpenses.catagory), func.sum(BudgetExpenses.amount)).join(BudgetExpenses).filter(Budgetcats.userid == current_user.id).group_by(BudgetExpenses.catagory).all()
    context = {'exptotal':expsumtotal, 'inctotal':incsumtotal, 'cntexp':catscntexp, 'cntinc':catscntinc, 'user':User, 'cats':cats}
    return render_template('money/catagory.html', **context)