import sys, os
sys.path.append(os.getcwd())

from flask import Flask, render_template, redirect, session, request, url_for, flash
from models.autopsy_model import Autopsy
from models.user_model import UserModel
from models.category_model import Category
from models.country_model import Country
from models.subcription_model import Subscription
from models.base_model import DBSingleton
from datetime import datetime
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'

@app.before_first_request
def initialize_tables():
    connect_db()

    tables = [Category, Country, Autopsy, UserModel, Subscription]

    for table in tables:
        if not table.table_exists():
            table.create_table()

    disconnect_db()

@app.before_request
def connect_db():
    DBSingleton.getInstance().connect()

@app.teardown_request
def disconnect_db(error=None):
    DBSingleton.getInstance().close()


######## FrontPage Handler ########

@app.route("/")
def index():
    autopsies = Autopsy.select()
    categories = Category.select()
    countries = Country.select()
    return render_template("index.html", autopsies=autopsies, categories=categories, countries=countries)

@app.route("/startups/<int:id>")
def show_startup(id):
    autopsy = Autopsy.get(Autopsy.id == id)
    return render_template("startups.html", autopsy=autopsy)

@app.route('/submit')
def submit_startup():
    return render_template("submit.html")

@app.route('/faq')
def faq():
    return render_template("faq.html")

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        subscriber_email = request.form['email']
        subscription_date = datetime.now()
        Subscription.create(email=subscriber_email, subscription_date=subscription_date)

        return render_template("submit.html")
        # flash('Thanks for your interest, we will be in touch shortly', category='info')

    return render_template("submit.html")

######## Admin Handler ########

@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():

    if 'user' in session:
        return redirect(url_for('admin_index'))

    if request.method == 'POST':
        attempted_email = request.form['email']
        attempted_password = hash_password(request.form['password'])

        try:
            user = UserModel \
                .select() \
                .where(UserModel.email == attempted_email) \
                .where(UserModel.password == attempted_password)\
                .get()

            # flash('Welcome back {}'.format(user.username), category='info')

            session['user'] = {
                'username': user.username,
                'email': user.email
            }

            return redirect(url_for('admin_index'))

        except Exception as exception:
            flash('Wrong credentials. Error: {}'.format(exception), category='danger')

    return render_template("admin/submit.html")


@app.route("/admin/register", methods=['POST', 'GET'])
def admin_reg():
    users = UserModel.select()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        confirm_passwd = request.form['confirm_passwd']
        passwd = request.form['passwd']
        date_created = datetime.now()

        for user in users:
            if email == user.email:
                flash("Try another email")
                return render_template("admin/register.html")

        if passwd != confirm_passwd:
            flash("Both passwords don\'t match")
        password = hash_password(passwd)

        query = UserModel(username=username, email=email, password=password, date_created=date_created)
        query.save()
        return redirect(url_for('admin_login'))

    return render_template("admin/register.html")


def hash_password(passwd):
    return hashlib.sha256(passwd.encode()).hexdigest()


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('admin_login'))


@app.route("/admin/", methods=['GET', 'POST'])
def admin_index():
    if 'user' in session:
        autopsies = Autopsy.select()
        categories = Category.select()
        countries = Country.select()

        return render_template("admin/index.html", autopsies=autopsies, categories=categories, countries=countries)

    return redirect(url_for('admin_login'))

######## Subscriber List Handler ########

@app.route("/admin/subscribers/", methods=['GET', 'POST'])
def subscriber_list():
    if 'user' in session:
        subscribers=Subscription.select()
        return render_template('admin/subscribers/index.html', subscribers=subscribers)
    return redirect(url_for('admin_login'))

@app.route("/admin/subscribers/delete/<int:id>")
def delete_subscriber(id):
    subscriber = Subscription.get(Subscription.id == id)
    subscriber.delete_instance()
    return redirect('admin/subscribers/')


######## AUTOPSY CRUD Handler ########

@app.route("/admin/create", methods=['POST', 'GET'])
def create():
    autopsies = Autopsy.select()
    categories = Category.select()
    countries = Country.select()

    if request.method == 'POST':
        company_name = request.form['startup_name']
        industry = request.form['industry']
        country = request.form['country']
        description = request.form['description']
        year_range = request.form['year_range']
        founder_name = request.form['founder_name']
        why_they_failed = request.form['why_they_failed']
        amount_raised = request.form['amount_raised']
        logo = request.files['company_logo'] # this is a file handler
        date_created = datetime.now()

        company_logo = secure_filename(logo.filename)

        logo.save(os.path.join(UPLOAD_FOLDER, company_logo))

        Autopsy.create(company_name=company_name, industry=industry, description=description,
                        year_range=year_range, founder_name=founder_name,why_they_failed=why_they_failed,
                       date_created=date_created, country=country, amount_raised=amount_raised,company_logo=company_logo)

    return render_template("admin/index.html", autopsies=autopsies, categories=categories, countries=countries)

@app.route("/admin/edit/<int:id>")
def edit(id):
    autopsi = Autopsy.get(Autopsy.id == id)
    return render_template('admin/edit.html', autopsy=autopsi)


@app.route("/admin/update/<int:id>", methods=['POST', 'GET'])
def update(id):
    autopsy = Autopsy.get(Autopsy.id == id)
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
    autopsy = Autopsy.get(Autopsy.id == id)
    autopsy.delete_instance()
    return redirect('admin/')

@app.route('/layout')
def layout():
    return render_template('admin/layouts.html')


######## Category Handler ########

@app.route("/admin/category/")
def category():
    if 'user' in session:
        categories = Category.select()
        return render_template("admin/category/index.html", categories=categories)

    return redirect(url_for('admin_login'))

@app.route("/admin/category/create", methods=['POST', 'GET'])
def create_category():
    categories = Category.select()

    if request.method == 'POST':
        title = request.form['name']
        slug = request.form['slug']
        date_created = datetime.now()

        Category.create(name=title, slug=slug, date_created=date_created)

    return render_template("admin/category/index.html", categories=categories)


@app.route("/admin/category/edit/<int:id>")
def category_edit(id):
    category = Category.get(Category.id == id)
    return render_template('admin/category/edit.html', category=category)

@app.route("/admin/category/update/<int:id>", methods=['POST', 'GET'] )
def category_update(id):
    category = Category.get(Category.id == id)
    if request.method == 'POST':
        category.name = request.form['name']
        category.slug = request.form['slug']

        category.save()
    return render_template("admin/category/")

@app.route("/admin/category/delete/<int:id>")
def category_delete(id):
    category = Category.get(Category.id == id)
    category.delete_instance()
    return redirect('admin/category/')


######## Country Handler ########

@app.route("/admin/country/")
def country():
    if 'user' in session:
        countries = Country.select()
        return render_template("admin/country/index.html", countries=countries)

    return redirect(url_for('admin_login'))

@app.route("/admin/country/create", methods=['POST', 'GET'])
def create_country():
    countries = Country.select()

    if request.method == 'POST':
        title = request.form['name']
        slug = request.form['slug']
        date_created = datetime.now()

        Country.create(name=title, slug=slug, date_created=date_created)

    return render_template("admin/country/index.html", countries=countries)


@app.route("/admin/country/edit/<int:id>")
def country_edit(id):
    country = Country.get(Country.id == id)
    return render_template('admin/country/edit.html', country=country)

@app.route("/admin/country/update/<int:id>", methods=['POST', 'GET'] )
def country_update(id):
    country = Country.get(Country.id == id)
    if request.method == 'POST':
        country.name = request.form['name']
        country.slug = request.form['slug']

        country.save()
    return render_template("admin/country/")

@app.route("/admin/country/delete/<int:id>")
def country_delete(id):
    country = Country.get(Country.id == id)
    country.delete_instance()
    return redirect('admin/country/')

app.secret_key = os.environ.get("FLASK_SECRET_KEY")