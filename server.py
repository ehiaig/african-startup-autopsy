import sys, os
sys.path.append(os.getcwd())

from flask import Flask, render_template, redirect, session, request, url_for, flash
from models.autopsy_model import AutopsyModel
from models.user_model import UserModel
from models.base_model import DBSingleton
from datetime import datetime
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.before_first_request
def initialize_tables():
    connect_db()
    if not AutopsyModel.table_exists():
        AutopsyModel.create_table()
    disconnect_db()

@app.before_request
def connect_db():
    DBSingleton.getInstance().connect()

@app.teardown_request
def disconnect_db(err=None):
    DBSingleton.getInstance().close()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin/register")
def admin_reg():
    return render_template("admin/register.html")

@app.route("/admin/process", methods=['POST'])
def process():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        confirm_passwd = request.form['confirm_password']
        passwd = request.form['password']
        timestamp = datetime.now()

        if passwd == confirm_passwd:
            password = hashlib.md5(passwd.encode()).hexdigest()

        query=UserModel(username=username, email=email, password=password, timestamp=timestamp)
        query.save()
    return render_template("admin/register.html")

@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    error = ''
    try:
        if request.method == 'POST':
            attempted_email = request.form['email']
            attempted_password = request.form['password']

            flash(attempted_email)
            flash(attempted_password)
            if attempted_email == "admin@admin.com" and attempted_password == "admin":
                return redirect(url_for('admin_index'))
            else:
                error = "Invalid credential"
        return render_template("admin/login.html", error=error)

    except Exception as e:
        flash(e)
        return render_template("admin/login.html", error=error)


@app.route("/admin/", methods=['GET', 'POST'])
def admin_index():
    autopsies = AutopsyModel.select()
    return render_template("admin/index.html", autopsies=autopsies)


@app.route("/admin/create", methods=['POST', 'GET'])
def create():
    autopsies = AutopsyModel.select()

    if request.method == 'POST':
        company_name = request.form['startup_name']
        industry = request.form['industry']
        country = request.form['country']
        description = request.form['description']
        year_range = request.form['year_range']
        founder_name = request.form['founder_name']
        why_they_failed = request.form['why_they_failed']
        amount_raised = request.form['amount_raised']
        # company_logo = request.files['company_logo']
        timestamp = datetime.now()

        query = AutopsyModel(company_name=company_name, industry=industry, description=description,
                             year_range=year_range, founder_name=founder_name, why_they_failed=why_they_failed,
                             timestamp=timestamp, country=country, amount_raised=amount_raised)
        query.save()

    return render_template("admin/index.html", autopsies=autopsies)

@app.route("/admin/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    autopsi = AutopsyModel.get(AutopsyModel.id == id)

    return render_template('admin/edit.html', autopsy=autopsi)


app.secret_key = os.environ.get("FLASK_SECRET_KEY")