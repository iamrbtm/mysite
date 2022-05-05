from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from website.models import *
from datetime import datetime, timedelta
from website import db
from sqlalchemy.sql import func

prod = Blueprint("prod", __name__)

# Productivity
@prod.route("/", methods=["GET", "POST"])
@login_required
def productivity():
    from website.templates.productivity.productivity_forms import Project_Form
    
    form = Project_Form()
    
    query = db.engine.execute('select * from task_log')
    return render_template("productivity/productivity.html", user=User, query=query, form=form)

