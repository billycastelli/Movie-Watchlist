### General Watchlist helper functions

def duplicate_movie(cursor, mid, lid):
        cursor.execute("SELECT COUNT(*) FROM movies WHERE mid = %d and lid = %d"%(mid, lid))
        res = cursor.fetchone()
        return res[0] > 0 

