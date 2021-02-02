from flask import Blueprint, render_template, request, flash, url_for, redirect, session
import tmdb
from dbconnector import connect
import watchlist
from wtforms import Form, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
import gc
import datetime

watchlist_blueprint = Blueprint(
    'watchlist_blueprint', __name__, static_folder='static')


@watchlist_blueprint.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@watchlist_blueprint.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@watchlist_blueprint.route('/')
def watchlist_home():
    top_movies = tmdb.get_trending(timeframe='day')
    return render_template("watchlist_home.html", top_movies=top_movies)


@watchlist_blueprint.route('/movie', methods=['GET', 'POST'])
def watchlist_film_view():
    mid = request.args.get("mid", default="")
    movie = tmdb.get_movie(mid)
    wls = []
    if request.method == "POST":
        try:
            lid = int(request.form['list_name'])
        except:
            flash("You must select a choice from your watchlists")
            return redirect(url_for("watchlist_blueprint.watchlist_film_view", mid=mid))
        uid = session['uid']
        connection, curs = connect()
        if duplicate_movie(curs, int(movie.mid), lid):
            flash("%s is already in that list!" % movie.title)
            return redirect(url_for("watchlist_blueprint.watchlist_film_view", mid=mid))
        try:
            curs.execute('INSERT INTO movies(mid, title, poster, release_date, overview, lid, uid) \
                            VALUES("%d", "%s", "%s", "%s", "%s", "%d", "%d")'
                         % (int(movie.mid), movie.title, movie.poster, movie.release_date, movie.overview.encode('ascii', 'ignore').decode('utf8'), lid, uid))
            connection.commit()
            flash("%s added to list" % (str(movie.title)))
            curs.close()
            connection.close()
            return redirect(url_for("watchlist_blueprint.watchlist_film_view", mid=int(movie.mid)))
        except Exception as e:
            print(str(e))
            return render_template("watchlist_single_movie.html", movie=movie, wls=wls)

    try:
        session['logged_in']
        wls = get_watchlists()
        return render_template("watchlist_single_movie.html", movie=movie, wls=wls)
    except Exception as e:
        # flash(str(e))
        return render_template("watchlist_single_movie.html", movie=movie, wls=wls)


@watchlist_blueprint.route('/search')
def watchlist_search():
    title = request.args.get('title')
    if title == "" or None:
        title = "Spider-man"
        flash("No value entered. Here are some recommended movies!")
    results = tmdb.search(str(title))
    size = len(results)
    return render_template("watchlist_search.html", results=results, size=size)


@watchlist_blueprint.route('/login', methods=['GET', 'POST'])
def watchlist_login():
    if request.method == "POST":
        attempted_username = request.form['username']
        attempted_password = request.form['password']
        connection, curs = connect()
        curs.execute('SELECT * \
                            FROM users \
                            WHERE username = "%s"' % (attempted_username))
        userInfo = curs.fetchone()
        if userInfo == None:
            flash("Username not found. Try a different username, or create an account.")
            return render_template("watchlist_login.html")
        uid, username, password = userInfo
        curs.close()
        connection.close()
        gc.collect()
        try:
            if attempted_username == username and sha256_crypt.verify(attempted_password, password):
                session['logged_in'] = True
                session['uid'] = uid
                session['username'] = username
                flash("Welcome %s!" % (username))
                return redirect(url_for("watchlist_blueprint.watchlist_home"))
            else:
                flash("Incorrect password, try again")
                return render_template("watchlist_login.html")
        except Exception as e:
            return str(e)
    return render_template("watchlist_login.html")


@watchlist_blueprint.route('/popular')
def watchlist_popular():
    top_movies = tmdb.get_trending(timeframe='day')
    # return str(top_movies)
    return render_template("watchlist_popular.html", top_movies=top_movies)


@watchlist_blueprint.route('/logout', methods=['GET', 'POST'])
def watchlist_logout():
    session.pop('logged_in', False)
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('watchlist_blueprint.watchlist_home'))


class RegistrationForm(Form):
    '''Child of a WTForm Form object...'''
    username = TextField('Username', [validators.Length(min=3, max=20)])
    password = PasswordField('Password', [validators.Required(),
                                          validators.EqualTo('confirm',
                                                             message="Passwords must match")])
    confirm = PasswordField('Confirm Password')


@watchlist_blueprint.route('/signup', methods=['GET', 'POST'])
def watchlist_signup():
    session.pop('_flashes', None)
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():  # if the form info is valid
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))
            connection, curs = connect()
            # Check if username already exists in database
            curs.execute("SELECT * \
                              FROM users \
                              WHERE username = (%s);", (username,))
            if len(curs.fetchall()) > 0:
                flash("That username is already taken, please try another")
                return render_template('watchlist_signup.html', form=form)
            else:
                curs.execute("INSERT INTO users (username, password) \
                              VALUES (%s, %s);", (username, password))
                connection.commit()
                flash("Account created successfully!")
                curs.execute(
                    'SELECT uid from users where username = "%s";' % (username))
                data = curs.fetchone()
                uid = int(data[0])
                curs.close()
                connection.close()
                gc.collect()
                session['uid'] = uid
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('watchlist_blueprint.watchlist_home'))
            return render_template('watchlist_signup.html', form=form)
        if request.method == "POST" and form.validate() == False:  # if form info is invalid
            flash('Invalid password, please try again')
            return render_template('watchlist_signup.html', form=form)
    except Exception as e:
        return str(e)
    return render_template("watchlist_signup.html")

# Registration End


@watchlist_blueprint.route('/me', methods=['GET', 'POST'])
def watchlist_me():
    return redirect(url_for("watchlist_blueprint.watchlist_mylists"))


@watchlist_blueprint.route('/mylists', methods=['GET', 'POST'])
def watchlist_mylists():
    try:
        session['logged_in']
        lists_info = []
        connection, curs = connect()
        curs.execute('SELECT * \
                      FROM lists \
                      WHERE uid = %d and username = "%s"' % (session["uid"], session['username']))
        listtup = curs.fetchall()
        for tup in listtup:
            tup = list(tup)
            tup[4] = tup[4].strftime("%m-%d-%y")
            lists_info.append(tup)
        curs.close()
        connection.close()
        return render_template("watchlist_mylists.html", lists_info=lists_info)
    except:
        flash("Please login to view your watchlists")
        return redirect(url_for("watchlist_blueprint.watchlist_login"))


@watchlist_blueprint.route('/mylists/<lid>')
def watchlist_list_view(lid):
    connection, curs = connect()
    curs.execute(
        'SELECT watchlist_name, data FROM lists WHERE lid = "%d"' % (int(lid)))
    list_info = curs.fetchone()
    name = list_info[0]
    date = list_info[1].strftime("%m-%d-%y")
    curs.execute('SELECT * FROM movies WHERE lid = "%d"' % (int(lid)))
    movies = curs.fetchall()
    return render_template("watchlist_list_view.html", name=name, movies=movies, size=len(movies), date=date)


@watchlist_blueprint.route('/new_list', methods=['GET', 'POST'])
def watchlist_new_list():
    try:
        if session['logged_in']:
            if request.method == "POST":
                wlname = request.form['wlname']
                connection, curs = connect()
                curs.execute('INSERT INTO lists (uid, username, watchlist_name) \
                            VALUES (%d, "%s", "%s");' %
                             (session["uid"], session["username"], wlname))
                connection.commit()
                flash('"%s" list added!' % (wlname))
                curs.close()
                connection.close()
                return redirect(url_for("watchlist_blueprint.watchlist_mylists"))
            return render_template("watchlist_new_list.html")
        flash("You must login before creating a new list")
        return redirect(url_for("watchlist_blueprint.login"))
    except Exception as e:
        return str(e)


def get_watchlists():
    wls = []
    connection, curs = connect()
    curs.execute('SELECT * \
                  FROM lists \
                  WHERE uid = %d and username = "%s"' % (session["uid"], session['username']))
    tups = curs.fetchall()
    for tup in tups:
        wls.append(tup)
    return wls


def duplicate_movie(cursor, mid, lid):
    cursor.execute(
        "SELECT COUNT(*) FROM movies WHERE mid = %d and lid = %d" % (mid, lid))
    res = cursor.fetchone()
    return res[0] > 0
