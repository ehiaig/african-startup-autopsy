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

UPLOAD_FOLDER = './static/uploads'

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
    autopsies = AutopsyModel.select()
    return render_template("index.html", autopsies=autopsies)

@app.route("/startups")
def show_startup():
    autopsies = AutopsyModel.select()
    return render_template("startups.html", autopsies=autopsies)


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

            if attempted_email != "admin@admin.com" and attempted_password != "admin":
                error = "Invalid credential"
            else:
                flash('You have successfully logged in')
                return redirect(url_for('admin_index'))
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
        logo = request.files['company_logo'] # this is a file handler??
        timestamp = datetime.now()

        company_logo = secure_filename(logo.filename)

        logo.save(os.path.join(UPLOAD_FOLDER, company_logo))

        AutopsyModel.create(company_name=company_name, industry=industry, description=description,
                             year_range=year_range, founder_name=founder_name, why_they_failed=why_they_failed,
                             timestamp=timestamp, country=country, amount_raised=amount_raised,company_logo=company_logo)

    return render_template("admin/index.html", autopsies=autopsies)

@app.route("/admin/edit/<int:id>")
def edit(id):
    autopsi = AutopsyModel.get(AutopsyModel.id == id)
    return render_template('admin/edit.html', autopsy=autopsi)

@app.route("/admin/update/<int:id>", methods=['POST', 'GET'])
def update(id):
    autopsy = AutopsyModel.get(AutopsyModel.id == id)
    if request.method == 'POST':
        autopsy.company_name = request.form['startup_name']
        autopsy.industry = request.form['industry']
        autopsy.country = request.form['country']
        autopsy.description = request.form['description']
        autopsy.year_range = request.form['year_range']
        autopsy.founder_name = request.form['founder_name']
        autopsy.why_they_failed = request.form['why_they_failed']
        autopsy.amount_raised = request.form['amount_raised']

        logo = request.files['company_logo'] #write the string representation of your filehandler to the db
        company_logo = secure_filename(logo.filename)
        logo.save(os.path.join(UPLOAD_FOLDER, company_logo))

        autopsy.company_logo = company_logo #assign the url to our db field

        autopsy.save()
    return redirect("admin/")

@app.route("/admin/delete/<int:id>")
def delete(id):
    autopsy = AutopsyModel.get(AutopsyModel.id == id)
    autopsy.delete_instance()
    return redirect('admin/')

@app.route('/layout')
def layout():
    return render_template('admin/layouts.html')

app.secret_key = os.environ.get("FLASK_SECRET_KEY")