### General Watchlist helper functions

def duplicate_movie(cursor, mid, lid):
        cursor.execute("SELECT COUNT(*) FROM movies WHERE mid = %d and lid = %d"%(mid, lid))
        res = cursor.fetchone()
        return res[0] > 0 

def get_watchlists():
    wls = []
    curs, connection = connect()
    curs.execute('SELECT * \
                  FROM lists2 \
                  WHERE uid = %d and username = "%s"'%(session["uid"], session['username']))
    tups = curs.fetchall()
    for tup in tups:
        wls.append(tup)
    return wls