from src import app
from src.models import User
from src.auth import login_user, logout_user, login_required, current_user
from src.inc import *
# from src.forms import LocalData, LoginForm
from flask import render_template, redirect, url_for, flash, request


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        city, country = request.form['city'], request.form['country']
        df = get_data(city, country)
        graph1JSON, graph2JSON, graph3JSON, graph4JSON = get_graphs(df)
        msg, trigger = get_warning(df, city, country)
        slope_hi, slope_sm, slope_ff, slope_co, slope_o3, slope_no2 = get_graph_stats(df)
        return render_template('index.html', 
            graph1JSON=graph1JSON,  
            graph2JSON=graph2JSON, 
            graph3JSON=graph3JSON, 
            graph4JSON=graph4JSON, 
            msg=msg, 
            trigger=trigger, 
            show_graphs=True,         
            slope_hi=slope_hi, 
            slope_sm=slope_sm, 
            slope_ff=slope_ff, 
            slope_co=slope_co, 
            slope_o3=slope_o3, 
            slope_no2=slope_no2
        )

    return render_template('index.html', msg="Please enter your location to obtain a warning", trigger="secondary", show_graphs=False)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if current_user.is_authenticated:
        df = get_data("Toronto", "Canada")
        graph1JSON, graph2JSON, graph3JSON, graph4JSON = get_graphs(df)

        location = "Toronto, Canada"

        return render_template('submit.html', graph1JSON=graph1JSON,  graph2JSON=graph2JSON, graph3JSON=graph3JSON, graph4JSON=graph4JSON, location=location)
    
    return redirect(url_for('login'))


@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        try:
            lng, lat = float(request.form['longitude']), float(request.form['latitude'])
        except ValueError:
            pass
        op1_checked = request.form.get("check1") != None
        op2_checked = request.form.get("check2") != None
        op3_checked = request.form.get("check3") != None
        op4_checked = request.form.get("check4") != None
        op5_checked = request.form.get("check5") != None
        op6_checked = request.form.get("check6") != None

    base_url = "http://localhost:5000/"
    request_link = base_url + "data/"
    map_token="pk.eyJ1IjoiZGdvYmFsYWsiLCJhIjoiY2t1MHRkajBxMHhvcjJub3dvYnR5aWg0ciJ9.bkwsC3UJDbkeaT8aYrYDHQ"
    return render_template('datasets.html', request_link=request_link, map_token=map_token)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        query = User.query.filter_by(username=username)
        try:
            user = query.one()
            if username == user.username and password == user.password:
                login_user(user)
                flash('Logged in successfully ')
                return redirect(url_for('submit'))
            else:
                flash('Login Unsuccessful.')
        except Exception:
            flash('Login Unsuccessful.')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

    
@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404