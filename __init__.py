from flask import Flask, render_template, request, flash, url_for, redirect, session #,g (check it out, alternative to session)
from Player import Player
import tmdb
from dbconnect import connect

from wtforms import Form, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc


app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("main.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/mlb/input', methods = ['GET', 'POST'])
def input():
    if request.method == "POST":
        playerName = request.form['playerName']
        playerName = playerName.replace(" ", "_")
        return redirect(url_for('stat', username=playerName))
    return render_template("mlbenter.html")


@app.route('/mlb/stats/<username>', methods = ['POST', 'GET'])
def stat(username):
    playerName = username.replace("_", " ")
    try:
        p = Player(playerName)
    except:
        return "Error"
    tups, cols, totals = p.getStats()
    name = p.getName()
    return render_template("mlbstats.html", info = tups, cols = cols,
            name = name, totals = totals, stat=8, username=playerName)

#----------------------------------------------------
# Begin Watchlist code

@app.route('/watchlist')
def watchlist_home():
    top_movies = tmdb.get_trending(timeframe = 'day')
    return render_template("watchlist_home.html", top_movies = top_movies)

@app.route('/watchlist/movie/<mid>')
def watchlist_film_view(mid):
    movie = tmdb.get_movie(mid)
    return render_template("watchlist_single_movie.html", movie=movie)

@app.route('/watchlist/search/')
def watchlist_search():
    title = request.args.get('title')
    if title == "" or None:
        title = "Spider-man"
        flash("No value entered. Here are some recommended movies!")
    results = tmdb.search(str(title))
    size = len(results)
    return render_template("watchlist_search.html", results=results, size = size)

@app.route('/watchlist/login', methods = ['GET', 'POST'])
def watchlist_login():
    if request.method == "POST":
        attempted_username = request.form['username']
        attempted_password = request.form['password']
        curs, connection = connect()
        
        data = curs.execute('SELECT * \
                            FROM users \
                            WHERE username = "%s"'%(attempted_username))
        if int(data) == 0:
            flash("Username not found. Try a different username, or create an account.")
            return render_template("watchlist_login.html")
        userInfo = curs.fetchone()
        uid, username, password = userInfo
        curs.close()
        connection.close()
        gc.collect()
        try:
            if attempted_username == username and sha256_crypt.verify(attempted_password, password):
                session['logged_in'] = True
                session['uid'] = uid
                session['username'] = username
                flash("Welcome %s!"%(username))
                return redirect(url_for("watchlist_home"))
            else:
                flash("Incorrect password, try again")
                return render_template("watchlist_login.html")
        except Exception as e:
            return str(e)
    return render_template("watchlist_login.html")

@app.route('/watchlist/popular')
def watchlist_popular():
    top_movies = tmdb.get_trending(timeframe = 'day')
    #return str(top_movies)
    return render_template("watchlist_popular.html", top_movies = top_movies)


@app.route('/watchlist/logout', methods = ['GET', 'POST'])
def watchlist_logout():
    session.pop('logged_in', False)
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('watchlist_home'))

###### Registration Begin

class RegistrationForm(Form):
    '''Child of a WTForm Form object...'''
    username = TextField('Username', [validators.Length(min=3, max=20)])
    password = PasswordField('Password', [validators.Required(),
                                          validators.EqualTo('confirm',
                                          message = "Passwords must match")])
    confirm = PasswordField('Confirm Password')

@app.route('/watchlist/signup', methods = ['GET', 'POST'])
def watchlist_signup():
    session.pop('_flashes', None)
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate(): #if the form info is valid
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))
            curs, connection = connect()
            #Check if username already exists in database
            count = curs.execute("SELECT * \
                              FROM users \
                              WHERE username = (%s);", (thwart(username),))
            if int(count) > 0:
                flash("That username is already taken, please try another")
                return render_template('watchlist_signup.html', form=form)
            else:
                curs.execute("INSERT INTO users (username, password) \
                              VALUES (%s, %s);", (thwart(username), thwart(password)))
                connection.commit()
                flash("Account created successfully!")
                curs.execute('SELECT uid from users where username = "%s";'%(username))
                data = curs.fetchone()
                uid = int(data[0])
                curs.close()
                connection.close()
                gc.collect()
                session['uid'] = uid
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('watchlist_home'))
            return render_template('watchlist_signup.html', form=form)
        if request.method == "POST" and form.validate() == False: # if form info is invalid 
            flash('Invalid password, please try again')
            return render_template('watchlist_signup.html', form=form)
    except Exception as e:
        return str(e)
    return render_template("watchlist_signup.html")

###### Registration End

@app.route('/watchlist/mylists', methods = ['GET', 'POST'])
def watchlist_mylists():
    return render_template("watchlist_mylists.html")

@app.route('/watchlist/me', methods = ['GET', 'POST'])
def watchlist_me():
    return render_template("watchlist_me.html")


@app.route('/watchlist/new_list', methods = ['GET', 'POST'])
def watchlist_new_list():
    return render_template("watchlist_new_list.html")

if __name__ == "__main__":
    app.run(debug=True)

