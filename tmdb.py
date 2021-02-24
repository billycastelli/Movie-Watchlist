import json
import os
import requests
import random

api_key = os.environ["TMDB_API_KEY"]
api_url = os.environ["TMDB_API_URL"]


class Movie:
    def __init__(self, mid, title, poster, popularity, release_date, overview):
        self.mid = mid
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
        #response = urllib2.urlopen(url)
        #json_text = response.read().decode(encoding = 'utf-8')
        return requests.get(url).json()
        return json.loads(json_text)
    finally:
        if response != None:
            response.close()


def get_trending(timeframe='week', media_type='movie', count=20):
    trending_url = api_url + \
        '%s/%s/%s?api_key=%s' % ('trending', media_type, timeframe, api_key)
    base_img_url = 'https://image.tmdb.org/t/p/w500'
    json = get_json(trending_url)
    movies = []
    for movie in json['results']:
        movies.append(Movie(movie['id'],
                            movie['title'],
                            base_img_url + movie['poster_path'],
                            movie['popularity'],
                            movie['release_date'],
                            movie['overview']))
    return movies


def search(title):
    title = "+".join(title.split())
    base_img_url = 'https://image.tmdb.org/t/p/w500'
    movies = []
    search_url = api_url + \
        'search/movie?api_key=%s&language=en-US&query=%s' % (api_key, title)
    json = get_json(search_url)
    for movie in json['results']:
        try:
            movies.append(Movie(movie['id'],
                                movie['title'],
                                base_img_url + movie['poster_path'],
                                movie['popularity'],
                                movie['release_date'],
                                movie['overview']))
        except:
            pass
    return movies


def get_movie(mid):
    movie_url = api_url + \
        "movie/%s" % (mid) + "?language=en-US&api_key=%s" % (api_key)
    print(movie_url)
    base_img_url = 'https://image.tmdb.org/t/p/w500'
    movie = get_json(movie_url)
    movie = Movie(movie['id'],
                  movie['title'].replace('"', ''),
                  base_img_url + movie['poster_path'],
                  movie['popularity'],
                  movie['release_date'].replace('"', ''),
                  movie['overview'].replace('"', ''))
    return movie
