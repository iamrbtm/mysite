from website import db
from website.models import *
from datetime import datetime, timedelta
import requests, json
from sqlalchemy.sql import and_
from recipe_scrapers import scrape_me

def delete_plan(id):
    try:
        db.session.query(PlanDish).filter(PlanDish.planidfk == id).delete()
        db.session.commit()
        return True 
    except BaseException as error:
        print(f'An exception occurred: {error}')
        return False
    
def move_plan(id, date):
    newid = db.session.query(Planner.id, Planner.wknum).filter(Planner.date == datetime.strptime(date, "%Y-%m-%d")).first()
    records = db.session.query(PlanDish).filter(PlanDish.planidfk == id).all()
    
    for record in records:
        record.planidfk = newid.id
        record.wknum = newid.wknum
        db.session.commit()
    return newid.id

def new_plan(id, date):
    pass

def copy_plan(id, date):
    newid = db.session.query(Planner.id, Planner.wknum).filter(Planner.date == datetime.strptime(date, "%Y-%m-%d")).first()
    records = db.session.query(PlanDish).filter(PlanDish.planidfk == id).all()
    
    for record in records:
        new = PlanDish(
            wknum = newid.wknum,
            planidfk = newid.id,
            mainidfk = record.mainidfk,
            sideidfk = record.sideidfk,
            drinkidfk = record.drinkidfk,
            dessertidfk = record.dessertidfk,
            notes = record.notes
        )
        db.session.add(new)
        db.session.commit()
    return newid.id

def makedates(startdate, howmany=7):
    """ Use this to create more dates in the Planner table.  When the table has less than a count of 60. This program will run adding more dates to the table.

    Args:
        howmany (int): [how many new dates do you want added.  Default is 60 days]
        startdate ([type]): [the day you want the sustem to add going forward.]
    """
    date = startdate
    for _ in range(howmany):
        plan = Planner(date = date, wknum=date.isocalendar()[1], dayofwk=date.weekday())
        db.session.add(plan)
        db.session.commit()
        date = date + timedelta(days=1)
        
def get_holidays(year=datetime.now().year):
    key = db.session.query(APIKeys).filter(APIKeys.name == "calendarific").first().key
    url = f'https://calendarific.com/api/v2/holidays?api_key={key}&country=US&year={year}'
    
    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    fulljson = json.loads(response.text)
    
    for item in fulljson['response']['holidays']:
        if "National" in item['type'][0]:
            date = datetime.strptime(item['date']['iso'],"%Y-%m-%d")
            newdate = CalHolidays(
                date = date,
                holiday = item['name'],
                national = True,
                personal = False,
                wknum = date.isocalendar()[1],
            )
            cnt = db.session.query(CalHolidays).filter(and_(CalHolidays.holiday == newdate.holiday, CalHolidays.date == newdate.date)).count()
            if cnt == 0:
                db.session.add(newdate)
                db.session.commit()
    return True

def scrape_recipe(website):
    scraper = scrape_me(website,wild_mode=True)

    title = scraper.title()
    
    try:
        if scraper.cook_time() == 0 or scraper.cook_time() == None:
            cooktime = 0
        else:
            cooktime = scraper.cook_time()
    except: cooktime = 0
        
    try:
        if scraper.prep_time() == 0 or scraper.prep_time() == None:
            preptime = 0
        else: 
            preptime = scraper.prep_time()
    except: preptime = 0
    
    try:
        yeild = int(''.join(i for i in scraper.yields() if i.isdigit()))
        if yeild == 0 or yeild == None:
            yeild = 1
    except: yeild = 1
    
    ings = scraper.ingredients()
    inst=scraper.instructions().split('\n')
    img = scraper.image()
    
        
    return [[title, img, yeild, cooktime, preptime], [ings], [inst]]


def make_dish(title, img, yeild):
    newdish = Dish(
        name = title,
        pictureURL = img,
        numServings = yeild,
    )
    db.session.add(newdish)
    db.session.commit()
    
    newid = db.session.query(Dish).filter(Dish.name == title).first().id
    
    return newid

def make_recipe(nutrition, dishid):
    newrec = Recipe(
        dishfk = dishid,
        qty = nutrition['servingqty'],
        measurement = nutrition['servingunit'],
        ing = nutrition['foodname'],
        fat_total = nutrition['totalFat'],
        weight = nutrition['weight'],
        fat_sat = nutrition['satFat'],
        fat_trans = nutrition['transFat'],
        cholesterol = nutrition['cholesterol'],
        sodium = nutrition['sodium'],
        potassium = nutrition['potassium'],
        carb_total = nutrition['totalCarb'],
        carb_fiber = nutrition['fiber'],
        carb_sugar = nutrition['sugar'],
        protein = nutrition['protein'],
        calories = nutrition['calories'],
        pictureURL = nutrition['picURL'],
    )
    db.session.add(newrec)
    db.session.commit()

def make_steps(step, dishid, i):
    newstep = Steps(
        dishfk=dishid,
        step_num = i,
        step_text = step
    )
    db.session.add(newstep)
    db.session.commit()
    
def get_food_item(item):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"    

    payload='query='+item
    headers = {
    'x-app-id': '9b92ba02',
    'x-app-key': 'a8e4036769b4268c11f0fb1a50e7ec3c',
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    fulljson = json.loads(response.text)
    if 'message' in fulljson:
        if fulljson['message'] == "We couldn't match any of your foods":
            return 0
    
    # return json.dumps(fulljson)
    with open('fulljson.json','w') as jsonfull:
        jsonfull.write(json.dumps(fulljson))
    
    nutrition = parse_results(fulljson)
    
    with open('nutrition.json','w') as jsonfile:
        jsonfile.write(json.dumps(nutrition))
    return nutrition

def parse_results(fulljson):
    full_nutrition = {}
        
    full_nutrition['foodname'] = fulljson['foods'][0]['food_name']
    full_nutrition['servingqty'] = fulljson['foods'][0]['serving_qty']
    full_nutrition['servingunit'] = fulljson['foods'][0]['serving_unit']
    #weight
    if 'serving_weight_grams' not in fulljson['foods'][0]: full_nutrition['weight'] = 0
    elif fulljson['foods'][0]['serving_weight_grams'] is None: full_nutrition['weight'] = 0
    else: full_nutrition['weight'] = round(fulljson['foods'][0]['serving_weight_grams'],1)
    
    #calories
    if 'nf_calories' not in fulljson['foods'][0]: full_nutrition['calories'] = 0
    elif fulljson['foods'][0]['nf_calories'] is None: full_nutrition['calories'] = 0
    else: full_nutrition['calories'] = round(fulljson['foods'][0]['nf_calories'],1)
    
    #calories from fat
    if 'nf_total_fat' not in fulljson['foods'][0]: full_nutrition['calFat'] = 0
    elif fulljson['foods'][0]['nf_total_fat'] is None: full_nutrition['calFat'] = 0
    else: full_nutrition['calFat'] = round((fulljson['foods'][0]['nf_total_fat'])*9,1)
    
    #total fat
    if 'nf_total_fat' not in fulljson['foods'][0]: full_nutrition['totalFat'] = 0
    elif fulljson['foods'][0]['nf_total_fat'] is None: full_nutrition['totalFat'] = 0
    else: full_nutrition['totalFat'] = round(fulljson['foods'][0]['nf_total_fat'],1)
    
    #Saturated fat
    if 'nf_saturated_fat' not in fulljson['foods'][0]: full_nutrition['satFat'] = 0
    elif fulljson['foods'][0]['nf_saturated_fat'] is None: full_nutrition['satFat'] = 0
    else: full_nutrition['satFat'] = round(fulljson['foods'][0]['nf_saturated_fat'],1)
    
    #trans fat
    if 'nf_trans_fatty_acid' not in fulljson['foods'][0]: full_nutrition['transFat'] = 0
    elif fulljson['foods'][0]['nf_trans_fatty_acid'] is None: full_nutrition['cholesterol'] = 0
    else: full_nutrition['transFat'] = round(fulljson['foods'][0]['nf_trans_fatty_acid'],1)
    
    #cholesterol
    if 'nf_cholesterol' not in fulljson['foods'][0]: full_nutrition['cholesterol'] = 0
    elif fulljson['foods'][0]['nf_cholesterol'] is None: full_nutrition['cholesterol'] = 0
    else: full_nutrition['cholesterol'] = round(fulljson['foods'][0]['nf_cholesterol'],1)
    
    #sodium
    if 'nf_sodium' not in fulljson['foods'][0]: full_nutrition['sodium'] = 0
    elif fulljson['foods'][0]['nf_sodium'] is None: full_nutrition['sodium'] = 0
    else: full_nutrition['sodium'] = round(fulljson['foods'][0]['nf_sodium'],1)
    
    #Total Carbs
    if 'nf_total_carbohydrate' not in fulljson['foods'][0]: full_nutrition['totalCarb'] = 0
    elif fulljson['foods'][0]['nf_total_carbohydrate'] is None: full_nutrition['totalCarb'] = 0
    else: full_nutrition['totalCarb'] = round(fulljson['foods'][0]['nf_total_carbohydrate'],1)
    
    #Fiber
    if 'nf_dietary_fiber' not in fulljson['foods'][0]: full_nutrition['fiber'] = 0
    elif fulljson['foods'][0]['nf_dietary_fiber'] is None: full_nutrition['fiber'] = 0
    else: full_nutrition['fiber'] = round(fulljson['foods'][0]['nf_dietary_fiber'],1)
    
    #sugar
    if 'nf_sugars' not in fulljson['foods'][0]: full_nutrition['sugar'] = 0
    elif fulljson['foods'][0]['nf_sugars'] is None: full_nutrition['sugar'] = 0
    else: full_nutrition['sugar'] = round(fulljson['foods'][0]['nf_sugars'],1)
    
    #protein
    if 'nf_protein' not in fulljson['foods'][0]: full_nutrition['protein'] = 0
    elif fulljson['foods'][0]['nf_protein'] is None: full_nutrition['protein'] = 0
    else: full_nutrition['protein'] = round(fulljson['foods'][0]['nf_protein'],1)
    
    #potassium
    if 'nf_potassium' not in fulljson['foods'][0]: full_nutrition['potassium'] = 0
    elif fulljson['foods'][0]['nf_potassium'] is None: full_nutrition['potassium'] = 0
    else: full_nutrition['potassium'] = round(fulljson['foods'][0]['nf_potassium'],1)
    
    full_nutrition['picURL'] = fulljson['foods'][0]['photo']['thumb']
    
    return full_nutrition

def nutrition_single(ings):
    allnutrition = {}
    weight = 0
    fat_total = 0
    fat_sat = 0
    fat_trans = 0
    cholesterol = 0
    sodium = 0
    potassium = 0
    carb_total = 0
    carb_fiber = 0
    carb_sugar = 0
    protein = 0
    calories = 0
    calories_fat = 0
    
    for ing in ings:
        weight = weight + round(ing.weight)
        fat_total = fat_total + round(ing.fat_total)
        fat_sat = fat_sat + round(ing.fat_sat)
        fat_trans = fat_trans + round(ing.fat_trans)
        cholesterol = cholesterol + round(ing.cholesterol)
        sodium = sodium + round(ing.sodium)
        potassium = potassium + round(ing.potassium)
        carb_total = carb_total + round(ing.carb_total)
        carb_fiber = carb_fiber + round(ing.carb_fiber)
        carb_sugar = carb_sugar + round(ing.carb_sugar)
        protein = protein + round(ing.protein)
        calories = calories + round(ing.calories)
        calories_fat= round(fat_total*9)
    
    allnutrition['fat_total'] = fat_total
    allnutrition['weight'] = weight
    allnutrition['fat_sat'] = fat_sat
    allnutrition['fat_trans'] = fat_trans
    allnutrition['cholesterol'] = cholesterol
    allnutrition['sodium'] = sodium
    allnutrition['potassium'] = potassium
    allnutrition['carb_total'] = carb_total
    allnutrition['carb_fiber'] = carb_fiber
    allnutrition['carb_sugar'] = carb_sugar
    allnutrition['protein'] = protein
    allnutrition['calories'] = calories
    allnutrition['calories_fat'] = calories_fat
    
    return allnutrition
