from flask import Flask, request, render_template, redirect, session, flash, jsonify
from models import db, connect_db, User, Favorite
from forms import SignUpForm, LoginForm
from secret import API_SECRET_KEY
import requests
import os
# DATE MANIPULATION MODULES TO USE FOR API REQUEST PARAMS
from datetime import date
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.app_context().push() 

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///GamesDB"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "gamin123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

@app.route('/')
def homepage():
    """Redirect to games page"""

    return redirect('/games')

# /* **************************MAIN ROUTES FOR DISPLAYING GAMES BY DIFFERENT CATEGORIES(Goes until line 312)************************* */
@app.route('/games')
def games_page():
    """Homepage for presenting a list of games"""
# Clears the session. Gets current date and five months prior, for use in sorting api data by date. Api request with prefered params saved to BASE_URL
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    # ONCE YOU INPUT USER STUFF FOR SESSION REMEMBER AT THE END OF THIS LIST COMPREHENSION ADD if key != "user thing", hopefully should remove all session stuff except for the a logged in user.
    current_date = date.today()
    five_months = current_date + relativedelta(months=-5)
    BASE_URL = f"https://rawg.io/api/games?dates={five_months},{current_date}&ordering=-added&page_size=40"
    
# Requests api data for a list of games, sorted by being added in the last five months 
    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})

# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates 
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page
  
    return render_template('games.html', results=results, next_page=next_page, previous_page=previous_page)

@app.route('/games/upcoming')
def games_upcoming_page():
    """Homepage for presenting a list of most anticipated games"""
# Clears the session. Gets current date and six months ahead, for use in sorting api data by date. Api request with prefered params saved to BASE_URL
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    current_date = date.today()
    six_months = current_date + relativedelta(months=+6)
    BASE_URL = f"https://rawg.io/api/games?dates={current_date},{six_months}&ordering=-added&page_size=40"
    
# Requests api data for a list of games, sorted by being released in the next six months 
    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})

# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates 
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page
    session['six_months'] = six_months
  
    return render_template('games.html', results=results, next_page=next_page, previous_page=previous_page, six_months=six_months)

@app.route('/games/new')
def games_new_page():
    """Homepage for presenting a list of newly released games"""
# Clears the session. Gets current date and one month prior, for use in sorting api data by date. Api request with prefered params saved to BASE_URL
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    current_date = date.today()
    one_month = current_date + relativedelta(months=-1)
    BASE_URL = f"https://rawg.io/api/games?dates={one_month},{current_date}&ordering=-added&page_size=40"
    
# Requests api data for a list of games, sorted by being added in the month 
    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})

# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates 
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page
    session['one_month'] = one_month
  
    return render_template('games.html', results=results, next_page=next_page, previous_page=previous_page, one_month=one_month)    

@app.route('/games/next_page')
def next_page():
    """Next page pagination for standard games"""
# Adds next page of whatever games page currently in use to session, for use in pagination. Then pops it out, adding a new updated one after.
    next_page = session.get('next_page')
    one_month = session.get('one_month')
    six_months = session.get('six_months')
    resp = requests.get(next_page, params = {"key": API_SECRET_KEY})
    session.pop('next_page')
    
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('games.html', results=results, next_page=next_page, previous_page=previous_page, one_month=one_month, six_months=six_months)

@app.route('/games/previous_page')
def previous_page():
    """Previous page pagination for standard games"""
# Adds previous page of whatever games page currently in use to session, for use in pagination. Then pops it out, adding a new updated one after.
    previous_page = session.get('previous_page')
    one_month = session.get('one_month')
    six_months = session.get('six_months')
    resp = requests.get(previous_page, params = {"key": API_SECRET_KEY})
    session.pop('previous_page')
# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates     
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('games.html', results=results, next_page=next_page, previous_page=previous_page, one_month=one_month, six_months=six_months)

@app.route('/games/<int:id>')
def game_info(id):
    """Game info page"""
# Requests all data about a selected game
    resp = requests.get(f"https://api.rawg.io/api/games/{id}", params = {"key": API_SECRET_KEY})
# Saves relative data from api. data holds all the data needed for presenting things through Jinja on my HTML template 
    data = resp.json()

    return render_template('gameinfo.html', data=data)

@app.route('/category/next_page')
def next_category_page():
    """Next page pagination for categorized games"""
# Route for allowing all category pages to click to the next relative page. Gets api value(url) for next page from session and passes it in as a request url for pagination 
    next_page = session.get('next_page')
    slug = session.get('slug')
    resp = requests.get(next_page, params = {"key": API_SECRET_KEY})
    session.pop('next_page')
# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates   
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('category.html', results=results, next_page=next_page, previous_page=previous_page, slug=slug.upper())

@app.route('/category/previous_page')
def previous_category_page():
    """Previous page pagination for categorized games"""
# Route for allowing all category pages to click to the previous relative page. Gets api value(url) for previous page from session and passes it in as a request url for pagination 
    previous_page = session.get('previous_page')
    slug = session.get('slug')
    resp = requests.get(previous_page, params = {"key": API_SECRET_KEY})
    session.pop('previous_page')
# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates 
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('category.html', results=results, next_page=next_page, previous_page=previous_page, slug=slug.upper())    

@app.route('/genres')
def genres_page():
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    """Page for presenting a list of genres"""
    resp = requests.get("https://rawg.io/api/genres?page_size=40", params = {"key": API_SECRET_KEY})
# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates     
    data = resp.json()
    results = data["results"]
    # import pdb
    # pdb.set_trace()

    return render_template('genres.html', results=results)

@app.route('/genres/<slug>')
def genre_games_page(slug):
    """Page for presenting a list of games by a specific genre"""
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    session['slug'] = slug
    BASE_URL = f"https://rawg.io/api/games?genres={slug}&ordering=-added&page_size=40"
# Requests a list of games by genre using the api genre id
    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})
    
# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates.
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page
  
    return render_template('category.html', results=results, next_page=next_page, previous_page=previous_page, slug=slug.upper())

@app.route('/platforms')
def platforms_page():
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    """Page for presenting a list of platforms"""
    resp = requests.get("https://rawg.io/api/platforms?page_size=40", params = {"key": API_SECRET_KEY})
# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates.    
    data = resp.json()
    results = data["results"]
    
    return render_template('platforms.html', results=results)

@app.route('/platforms/<slug>')
def platform_games_page(slug):
    """Page for presenting a list of games by a specific platform"""
    [session.pop(key) for key in list(session.keys()) if key != "username"]
# An annoying part of the api is that I have to request games by platform by the platform id instead of name. So this extracts the platform and name seperately to be used in the request and the jinja template.
    plat_dict = eval(slug)
    id = plat_dict['id']
    session['id'] = id
    slug = plat_dict['name']
    session['slug'] = slug
    BASE_URL = f"https://rawg.io/api/games?platforms={id}&page_size=40"

# Requests a list of games by platform using the api platform id
    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})

# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates.
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page
  
    return render_template('category.html', results=results, next_page=next_page, previous_page=previous_page, slug=slug.upper())

@app.route('/search')
def search():
    """Handles search bar input for api search request"""
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    search = request.args.get('search')
    BASE_URL = f"https://rawg.io/api/games?search={search}&page_size=40"

    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})

    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('search.html', results=results, next_page=next_page, previous_page=previous_page)

@app.route('/search/next_page')
def search_next_page():
    """Next page pagination for standard games"""
# Adds next page of search result to session, for use in pagination. Then pops it out, adding a new updated one after.
    next_page = session.get('next_page')
    resp = requests.get(next_page, params = {"key": API_SECRET_KEY})
    session.pop('next_page')
    
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('search.html', results=results, next_page=next_page, previous_page=previous_page)

@app.route('/search/previous_page')
def search_previous_page():
    """Previous page pagination for standard games"""
# Adds previous page of search result to session, for use in pagination. Then pops it out, adding a new updated one after.
    previous_page = session.get('previous_page')
    resp = requests.get(previous_page, params = {"key": API_SECRET_KEY})
    session.pop('previous_page')
# Saves relative data from api. results holds all the data needed for presenting things through Jinja on my HTML templates     
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('search.html', results=results, next_page=next_page, previous_page=previous_page)

# /* **************************USER ROUTES************************* */

@app.route('/register', methods=['GET','POST'])
def register():
    """Route for registering user"""

    form = SignUpForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        image_url = form.image_url.data or None

        user = User.register(username, password, image_url)

        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        # on a successfull login, redirect to main page
        return redirect('/')
        
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login_route():

    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect('/')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username')

    return redirect('/')

@app.route('/users/<username>')
def user_page(username):
    if "username" in session and username == session['username']:
        user = User.query.get(username)
        favorite = user.favorites

        return render_template('user.html', user=user, favorite=favorite)

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Handle form submission for deleting an existing user"""

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect("/")

@app.route('/games/<int:id>/<username>/favorite', methods=["POST"])
def add_fav(id, username):
    """Favorites a game"""
    user = User.query.get_or_404(username)
    game_id = request.form.get('game_id')
    name = request.form.get('name')
    background_image = request.form.get('background_image')

    favorite = Favorite(username=session['username'], game_id=game_id, name=name, background_image=background_image)
    db.session.add(favorite)
    db.session.commit()

    return redirect(f'/users/{user.username}')

@app.route('/games/<int:id>/<username>/delete', methods=["POST"])
def delete_fav(id, username):
    """Deletes a favorite"""
    favorite = Favorite.query.get(id)
    user = User.query.get_or_404(username)
    
    db.session.delete(favorite)
    db.session.commit()

    return redirect(f'/users/{user.username}')