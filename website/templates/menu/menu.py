from flask import Blueprint, render_template, request, redirect, url_for
from flask.helpers import flash
from flask_login import login_required
from website.models import *
from datetime import datetime, timedelta
from website import db
from website.templates.menu.process_menu import *
from sqlalchemy.sql import func, extract
import datetime, pdfkit

menu = Blueprint("menu", __name__)

@menu.route("/", methods=['GET'])
@login_required
def menuHome():
    currentyear = datetime.datetime.now().year
    year = currentyear
    for _ in range(2):
        get_holidays(year)
        year += 1
    weeknum = datetime.datetime.now().isocalendar()[1]
    return redirect(url_for('menu.plan', weeknum = weeknum))

@menu.route("/plan/<weeknum>", methods=['GET'])
@login_required
def plan(weeknum):
    cnt = db.session.query(Planner).filter(Planner.date >= datetime.datetime.now()).count()
    if cnt == 0:
        curdow = datetime.datetime.now().isocalendar()[2]
        dateToMonday = abs(0 - curdow)-1
        makedates(datetime.datetime.today() - timedelta(days=dateToMonday),7)
    elif cnt < 28:
        maxweeknum = db.session.query(func.max(Planner.wknum)).first()
        nextweeknum = maxweeknum[0] + 1
        d = str(datetime.datetime.now().year) + f"-W{nextweeknum}"
        r = datetime.datetime.strptime(d + '-1', "%Y-W%W-%w")
        makedates(r,28)
        
    dishlist = Dish.query.order_by(Dish.name).all()
    # plans = Planner.query.filter(Planner.date >= (datetime.datetime.today()- timedelta(days=2))).order_by(Planner.date).limit(60)
    plans = db.session.query(Planner).filter(Planner.wknum == weeknum).order_by(Planner.wknum, Planner.dayofwk).limit(28)
    # items = Recipe.query.order_by(Recipe.dishfk).all()
    plandish = db.session.query(PlanDish).filter(PlanDish.wknum == weeknum).all()
    firstdow = db.session.query(Planner).filter(Planner.dayofwk==0, Planner.wknum == int(weeknum)).first().date.strftime("%B %d, %Y")
    lastdow = db.session.query(Planner).filter(Planner.dayofwk==6, Planner.wknum == int(weeknum)).first().date.strftime("%B %d, %Y")
    holidays = db.session.query(CalHolidays).filter(CalHolidays.wknum == weeknum).filter(extract('year', CalHolidays.date) == datetime.datetime.today().year).all()
    return render_template("menu/menu.html", user=User, dishes=dishlist, plans=plans, plandish=plandish, currentweek=weeknum, firstdow=firstdow, lastdow=lastdow, holidays=holidays)


@menu.route("/<id>", methods=['GET', 'POST'])
@login_required
def menu_single(id):
    if request.method == 'POST':
        listofcats = ['maindish','sidedish','beverage','dessert']
        all = request.form
        for cats in listofcats:
            if cats in all:
                items = request.form.getlist(cats)
                for item in items:
                    if cats == "maindish":
                        if db.session.query(PlanDish).filter(PlanDish.mainidfk == item, PlanDish.planidfk == id).count() == 0:
                            newitem = PlanDish(planidfk = id, dessertidfk = None, drinkidfk=None, sideidfk = None, mainidfk=item, wknum = db.session.query(Planner).filter(Planner.id == id).first().wknum)
                    elif cats == "sidedish":
                        if db.session.query(PlanDish).filter(PlanDish.sideidfk == item, PlanDish.planidfk == id).count() == 0:
                            newitem = PlanDish(planidfk = id, dessertidfk = None, drinkidfk=None, sideidfk = item, mainidfk=None, wknum = db.session.query(Planner).filter(Planner.id == id).first().wknum)
                    elif cats == "beverage":
                        if db.session.query(PlanDish).filter(PlanDish.drinkidfk == item, PlanDish.planidfk == id).count() == 0:
                            newitem = PlanDish(planidfk = id, dessertidfk = None, drinkidfk=item, sideidfk = None, mainidfk=None, wknum = db.session.query(Planner).filter(Planner.id == id).first().wknum)
                    elif cats == "dessert":
                        if db.session.query(PlanDish).filter(PlanDish.dessertidfk == item, PlanDish.planidfk == id).count() == 0:
                            newitem = PlanDish(planidfk = id, dessertidfk = item, drinkidfk=None, sideidfk = None, mainidfk=None, wknum = db.session.query(Planner).filter(Planner.id == id).first().wknum)
                    if 'newitem' in locals():
                        db.session.add(newitem)
                        db.session.commit()
                
    dessertSQ = db.session.query(Catagories.id).filter(Catagories.catagory == "Dessert").subquery()
    sideSQ = db.session.query(Catagories.id).filter(Catagories.catagory == "Side").subquery()
    mainSQ = db.session.query(Catagories.id).filter(Catagories.catagory == "Main").subquery()
    drinkSQ = db.session.query(Catagories.id).filter(Catagories.catagory == "Beverage").subquery()
    wknumSQ = db.session.query(Planner.wknum).filter(Planner.id == id).subquery()
    reciepes = db.session.query(Recipe).all()
    desserts = db.session.query(Dish).join(CatTag,CatTag.dish == Dish.id).filter(CatTag.cat == dessertSQ).all()
    sides = db.session.query(Dish).join(CatTag,CatTag.dish == Dish.id).filter(CatTag.cat == sideSQ).all()
    mains = db.session.query(Dish).join(CatTag,CatTag.dish == Dish.id).filter(CatTag.cat == mainSQ).all()
    drinks = db.session.query(Dish).join(CatTag,CatTag.dish == Dish.id).filter(CatTag.cat == drinkSQ).all()
    planDish = db.session.query(PlanDish).filter(PlanDish.planidfk == id).all()
    dishes = db.session.query(Dish).all()
    plan = db.session.query(Planner).filter(Planner.id == id).first()
    holidays = db.session.query(CalHolidays).filter(CalHolidays.wknum == wknumSQ).filter(extract('year', CalHolidays.date) == datetime.datetime.today().year).all()
    return render_template("menu/plan_single.html", user=User, planDish=planDish, dishes=dishes, reciepes=reciepes, plan=plan, desserts=desserts, sides=sides, mains=mains, drinks=drinks, holidays=holidays)

@menu.route("/next/<id>", methods=['GET'])
@login_required
def menu_next(id):
    curdate = db.session.query(Planner).filter_by(id=id).first().date
    nextdate = curdate + timedelta(days=1)
    newid = db.session.query(Planner).filter(Planner.date == nextdate).first().id
    return redirect(url_for('menu.menu_single', id=newid))

@menu.route("/prev/<id>", methods=['GET'])
@login_required
def menu_prev(id):
    curdate = db.session.query(Planner).filter_by(id=id).first().date
    nextdate = curdate - timedelta(days=1)
    newid = db.session.query(Planner).filter(Planner.date == nextdate).first().id
    return redirect(url_for('menu.menu_single', id=newid))

# Recipe Functions
@menu.route("/recipe", methods=['GET', 'POST'])
@login_required
def recipe():
    dishes = db.session.query(Dish).order_by(Dish.name).all()
    recipes = db.session.query(Recipe).all()
    recs = db.session.query(func.sum(Recipe.carb_total).label('ttlcarbs')).group_by(Recipe.dishfk).all()
    dishcats = db.session.query(CatTag.dish, Catagories.catagory.label('cats')).filter(CatTag.cat != None).join(Catagories,CatTag.cat == Catagories.id).all()
    dishcatscount = len(dishcats)
    dishtags = db.session.query(CatTag.dish, Tags.tag.label('tags')).filter(CatTag.tag != None).join(Tags,CatTag.tag == Tags.id).all()
    dishtagscount = len(dishtags)
    catagories = Catagories.query.order_by(Catagories.catagory).all()
    tags = Tags.query.order_by(Tags.tag).all()
    return render_template("menu/recipe.html", user=User, dishes=dishes, recipes=recipes, recs=recs, dishcats=dishcats, dishtags=dishtags, catagories=catagories, tags=tags, dishtagscount=dishtagscount, dishcatscount=dishcatscount)


@menu.route("/recipe/<id>", methods=['GET'])
@login_required
def recipe_single(id):
    dish = Dish.query.filter_by(id=id).first()
    ings = Recipe.query.filter_by(dishfk=id).all()
    steps = Steps.query.filter_by(dishfk=id).order_by(Steps.step_num).all()
    allnutrition = nutrition_single(ings)
    list_of_catagories = ['Beverages', 'Bread/Bakery', 'Canned/Jarred Goods', 'Dairy', 'Dry/Baking Goods', 'Frozen Foods', 'Meat', 'Produce', 'Cleaners', 'Paper Goods', 'Personal Care', 'Other']
    dishcats = db.session.query(CatTag.id, CatTag.cat, Catagories.catagory.label('cats')).filter_by(dish=id).filter(CatTag.cat != None).join(Catagories,CatTag.cat == Catagories.id).all()
    dishcatscount = len(dishcats)
    dishtags = db.session.query(CatTag.id, CatTag.tag, Tags.tag.label('tag')).filter_by(dish=id).filter(CatTag.tag != None).join(Tags,CatTag.tag == Tags.id).all()
    dishtagscount = len(dishtags)
    catagories = Catagories.query.order_by(Catagories.catagory).all()
    tags = Tags.query.order_by(Tags.tag).all()
    return render_template("menu/recipe-single.html", user=User, dish=dish, recipes=ings, nutrition=allnutrition, steps=steps, shoppingcatagories=list_of_catagories, dishcats=dishcats, dishtags=dishtags, catagories=catagories, tags=tags, dishtagscount=dishtagscount, dishcatscount=dishcatscount)

@menu.route("/deletingIng/<recID>/<dishID>")
@login_required
def deleteIng(recID,dishID):
    Recipe.query.filter_by(id=recID).delete()
    db.session.commit()
    return redirect(url_for('menu.recipe_update', id=dishID))

@menu.route("/deletingStep/<stepID>/<dishID>")
@login_required
def deleteStep(stepID,dishID):
    Steps.query.filter_by(id=stepID).delete()
    db.session.commit()
    return redirect(url_for('menu.recipe_update', id=dishID))

@menu.route("/deletingPlan/<id>")
@login_required
def deletePlan(id):
    Planner.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('menu.menuHome'))


@menu.route("/recipe/delete/<id>", methods=['GET','POST'])
@login_required
def recipe_delete(id):
    db.session.query(Dish).filter(Dish.id == id).delete()
    db.session.commit()
    return redirect(url_for('menu.recipe'))

@menu.route("/recipe/<id>/update", methods=['GET','POST'])
@login_required
def recipe_update(id):
    if request.method == 'POST':
        if request.form.get('sub') == 'maindata':
            multiselectCat = request.form.getlist('cat')
            multiselectTag = request.form.getlist('tag')
            formdata = request.form.to_dict() 
            print(formdata)
            print(multiselectCat)
            print(multiselectTag)
        
            update = Dish.query.filter_by(id=id).first()
            update.numServings = formdata['servings']
            update.servingSize = formdata["servingSize"]
            update.prepTime = formdata["prepTime"]
            update.cookTime = formdata["cooktime"]
            update.cookTemp = formdata["cookTemp"]
            update.origurl = formdata["orgurl"]
            update.name = formdata['name']
            update.description = formdata['description']
            db.session.commit()
        
            for cat in multiselectCat:
                #check to see if the id already exists
                catcnt = CatTag.query.filter_by(cat=cat, dish=id).count()
                if catcnt == 0:
                    newcat = CatTag(dish=id, cat=cat, tag=None)
                    db.session.add(newcat)
                    db.session.commit()
                
            
            for tag in multiselectTag:
                #check to see if the id already exists
                tagcnt = CatTag.query.filter_by(tag=tag, dish=id).count()
                if tagcnt == 0:
                    newtag = CatTag(dish=id, cat=None, tag=tag)
                    db.session.add(newtag)
                    db.session.commit()
            
            return redirect(url_for('menu.recipe_single', id=id))
        if request.form.get('sub') == 'imagedata':
            formdata = request.form.to_dict() 
            print(formdata)
            update = Dish.query.filter_by(id=id).first()

            if formdata['picurl'] == '':
                pic = request.files['picfile']
                pic.seek(0)
            else:
                update.pictureURL = formdata['picurl']
            db.session.commit()
        
        if request.form.get('sub') == 'stepsave':
            num = Steps.query.filter_by(dishfk=id).all()
            
            step = Steps(
                step_text = request.form.get('stepdesc'),
                step_num = len(num)+1,
                dishfk = id
            )
            db.session.add(step)
            db.session.commit()
        if request.form.get('sub') == 'ingsave':
            #info for nutrition
            if request.form.get("notes") == None:
                fullitem = request.form.get("qty")+" "+request.form.get("measurement").title()+" "+request.form.get("ing").title()
            else:
                fullitem = request.form.get("qty")+" "+request.form.get("measurement").title()+" "+request.form.get("ing").title()+", "+request.form.get("notes")
            
            #get nutrition informtion  
            nutrition = get_food_item(fullitem)
            
            #build insert commnd to place data into database
            item = Recipe(
                qty=request.form.get("qty"), 
                measurement= request.form.get("measurement").title(), 
                ing= request.form.get("ing").title(),
                notes=request.form.get("notes"), 
                dishfk=request.form.get("dishid"),
                catagory = request.form.get('catagory'),
                weight = nutrition['weight'],
                fat_total = nutrition['totalFat'],
                fat_sat = nutrition['satFat'],
                fat_trans = nutrition['transFat'],
                cholesterol = nutrition['cholesterol'],
                sodium = nutrition['sodium'],
                potassium = nutrition['potassium'],
                carb_total = nutrition['totalCarb'],
                carb_fiber = nutrition['fiber'],
                carb_sugar = nutrition['sugar'],
                protein = nutrition['protein'],
                servsize = nutrition['weight'],
                calories = nutrition['calories'],
                calories_fat = nutrition['totalFat']*9,
                pictureURL = nutrition['picURL'])
            #add and commit the record to the database
            db.session.add(item)
            db.session.commit()
            
    dish = Dish.query.filter_by(id=id).first()
    ings = Recipe.query.filter_by(dishfk=id).all()
    steps = Steps.query.filter_by(dishfk=id).order_by(Steps.step_num).all()
    dishcatagories = Catagories.query.filter_by(dishfk=id).all()
    dishtags = Tags.query.filter_by(dishfk=id).all()
    catagories = Catagories.query.order_by(Catagories.catagory).all()
    tags = Tags.query.order_by(Tags.tag).all()
    allnutrition = nutrition_single(ings)
    list_of_catagories = ['Beverages', 'Bread/Bakery', 'Canned/Jarred Goods', 'Dairy', 'Dry/Baking Goods', 'Frozen Foods', 'Meat', 'Produce', 'Cleaners', 'Paper Goods', 'Personal Care', 'Other']
    return render_template('menu/recipe-single_update.html', user=User, dish=dish, recipes=ings, steps=steps, nutrition=allnutrition, shoppingcatagories=list_of_catagories, dishcatagories=dishcatagories, dishtags=dishtags, catagories=catagories, tags=tags)


@menu.route("/recipe/new", methods=['GET', 'POST'])
@login_required
def recipe_new():
    if request.method == 'POST':
        newdish = Dish(
            name = request.form.get('dishName'),
            pictureURL = request.form.get('picurl'),
            numServings = request.form.get('servings'),
            servingSize = request.form.get('servingSize'),
            cookTime = request.form.get('cooktime'),
            prepTime = request.form.get('prepTime'),
            cookTemp = request.form.get('cookTemp')
        )
        db.session.add(newdish)
        db.session.commit()
        
        id = db.session.query(Dish).filter_by(name=request.form.get('dishName')).first().id
        return redirect(url_for('menu.recipe_update', id=id))
    
    return render_template("menu/new.html", user=User)


@menu.route("/shopping", methods=['GET', 'POST'])
# @login_required
def shopping():
    if request.method == 'POST':
        if request.form['exportPDF'] == 'exportPDF':
            pdfkit.from_url("http://127.0.0.1:5000"+url_for('views.shopping'), 'shopping.pdf')
    items = db.session.query(Recipe.ing, Recipe.catagory, Recipe.dishfk, func.count(Recipe.ing).label('IngCount')).filter(Recipe.dishfk == Planner.dishfk).group_by(Recipe.ing).order_by(Recipe.ing).all()
    counts = db.session.query(Recipe.catagory, func.count(Recipe.catagory)).filter(Recipe.dishfk == Planner.dishfk).group_by(Recipe.catagory).all()
    return render_template("menu/shopping.html", user=User, items=items, counts=counts)#, dishes=dishlist, plans=plans)

@menu.route("/scrape", methods=['GET','POST'])
@login_required
def scrape():
    if request.method == "POST":
        webstite = request.form.get('website')
        scraper = scrape_recipe(webstite)
        dishid = make_dish(scraper[0][0],scraper[0][1],scraper[0][2])

        dishupdate = db.session.query(Dish).filter_by(id=dishid).first()
        dishupdate.origurl = webstite
        db.session.commit()
        
        for ing in scraper[1][0]:
            nuts = get_food_item(ing)
            if nuts == 0:
                db.session.query(Dish).filter(Dish.id == dishid).delete()
                db.session.commit()
                flash("Problem importing.  Try again",category='error')
                return redirect(url_for('menu.menuHome'))
            make_recipe(nuts,dishid)

        i=1
        for step in scraper[2][0]:
            make_steps(step, dishid, i) 
            i += 1
        return redirect(url_for('menu.recipe_update', id=dishid))
    
    return render_template('menu/scrape.html', user=User)

@menu.route('/<id>/next')
@login_required
def next_week(id):
    if id == '52':
        nextweek = str(1)
    else:
        nextweek = str(int(id)+1)
    
    cnt = db.session.query(Planner).filter(Planner.wknum == nextweek).count()
    
    if cnt != 0:
        return redirect(url_for('menu.plan', weeknum=nextweek))
    else:
        flash('No other weeks are currently available', category='error')
        return redirect(url_for('menu.plan', weeknum=id))
    
@menu.route('/<id>/prev')
@login_required
def prev_week(id):
    if id == '1':
        nextweek = str(52)
    else:
        nextweek = str(int(id)-1)
    
    cnt = db.session.query(Planner).filter(Planner.wknum == nextweek).count()
    
    if cnt != 0:
        return redirect(url_for('menu.plan', weeknum=nextweek))
    else:
        flash('No other weeks are currently available', category='error')
        return redirect(url_for('menu.plan', weeknum=id))
    
@menu.route('/deletecat/<id>/<dishid>')
@login_required
def deletecat(id, dishid):
    db.session.query(CatTag).filter(CatTag.id == id).delete()
    db.session.commit()
    return redirect(url_for('menu.recipe_single', id=dishid))

@menu.route('/deletetag/<id>/<dishid>')
@login_required
def deletetag(id, dishid):
    db.session.query(CatTag).filter(CatTag.id == id).delete()
    db.session.commit()
    return redirect(url_for('menu.recipe_single', id=dishid))

@menu.route('/plandelete/<id>')
@login_required
def plan_delete(id):
    delete_plan(id)
    return redirect(url_for('menu.menu_single', id=id))

@menu.route('/printplan/<weeknum>')
@login_required
def printplan(weeknum):
    dishlist = Dish.query.order_by(Dish.name).all()
    plans = db.session.query(Planner).filter(Planner.wknum == weeknum).order_by(Planner.wknum, Planner.dayofwk).limit(28)
    items = Recipe.query.order_by(Recipe.dishfk).all()
    plandish = db.session.query(PlanDish).filter(PlanDish.wknum == weeknum).all()
    firstdow = db.session.query(Planner).filter(Planner.dayofwk==0, Planner.wknum == int(weeknum)).first().date.strftime("%B %d, %Y")
    lastdow = db.session.query(Planner).filter(Planner.dayofwk==6, Planner.wknum == int(weeknum)).first().date.strftime("%B %d, %Y")
    holidays = db.session.query(CalHolidays).filter(CalHolidays.wknum == weeknum).all()
    
    context = {
        'user' : User,
        'dishes' : dishlist,
        'plans' : plans,
        'items' : items, 
        'plandish' : plandish, 
        'currentweek' : weeknum, 
        'firstdow' : firstdow, 
        'lastdow' : lastdow, 
        'holidays' : holidays
    }
    return render_template("menu/planner_print.html", **context)

@menu.route('/planmove/<id>', methods = ['GET','POST'])
@login_required
def plan_move(id):
    if request.method == 'POST':
        date = request.form.get('moveto')
        newid = move_plan(id, date)
        return redirect(url_for('menu.menu_single', id=newid))
    
@menu.route('/plancopy/<id>', methods = ['GET','POST'])
@login_required
def plan_copy(id):
    if request.method == 'POST':
        date = request.form.get('copyto')
        newid = copy_plan(id, date)
        return redirect(url_for('menu.menu_single', id=newid))