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
    return render_template("productivity/productivity.html", user=User)

