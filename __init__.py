from flask import Flask, render_template, request, flash, url_for, redirect, session
from Player import Player
import tmdb
from dbconnect import connect

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("main.html")

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
    return render_template("mlbstats.html", info = tups, cols = cols, name = name, totals = totals, stat=8, username=playerName)

@app.route('/watchlist')
def watchlist_home():
    top_movies = tmdb.get_trending(timeframe = 'day')
    return render_template("watchlist_home.html", top_movies = top_movies)

@app.route('/watchlist/signup', methods = ['GET', 'POST'])
def watchlist_signup():
    try:
        c = connect()
        return "hello"
    except:
        return "not working"
    return render_template("watchlist_signup.html")

@app.route('/watchlist/login', methods = ['GET', 'POST'])
def watchlist_login():
    if request.method == "POST":
        attempted_username = request.form['username']
        attempted_password = request.form['password']
        if attempted_username == "admin" and \
            attempted_password == "password":
            return redirect(url_for('watchlist_home'))
        else:
            return attempted_username
    return render_template("watchlist_login.html")

if __name__ == "__main__":
    app.run(debug=True)

