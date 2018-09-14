import json
import urllib2
import random

api_key = 'XXXXXXXXXXXXX'
api_url = 'https://api.themoviedb.org/3/'

class Movie:
    def __init__(self, title, poster, popularity, release_date, overview):
        self.title = title
        self.poster = poster
        self.popularity = popularity
        self.release_date = release_date
        self.overview = overview
        self.myRating = 0


def get_json(url):
    '''Returns json text from a URL'''
    response = None
    try:
        response = urllib2.urlopen(url)
        json_text = response.read().decode(encoding = 'utf-8')
        return json.loads(json_text)
    finally:
        if response != None:
            response.close()

def get_trending(timeframe = 'week', media_type = 'movie', count=10):
    trending_url = api_url + '%s/%s/%s?api_key=%s'%('trending', media_type, timeframe, api_key)
    base_img_url = 'https://image.tmdb.org/t/p/w500'
    json = get_json(trending_url)
    movies = []
    for movie in json['results']:
        movies.append(Movie(movie['title'],
                            base_img_url + movie['poster_path'],
                            movie['popularity'],
                            movie['release_date'],
                            movie['overview']))
    return movies

