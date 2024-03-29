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
        return requests.get(url).json()
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
        movies.append(Movie(movie.get('id'),
                            movie.get('title'),
                            base_img_url + movie.get('poster_path'),
                            movie.get('popularity'),
                            movie.get('release_date'),
                            movie.get('overview')
                            )
                      )
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
            movies.append(Movie(movie.get('id'),
                                movie.get('title'),
                                base_img_url + movie.get('poster_path'),
                                movie.get('popularity'),
                                movie.get('release_date'),
                                movie.get('overview')))
        except:
            pass
    return movies


def get_movie(mid):
    movie_url = api_url + \
        "movie/%s" % (mid) + "?language=en-US&api_key=%s" % (api_key)
    base_img_url = 'https://image.tmdb.org/t/p/w500'
    movie = get_json(movie_url)
    movie = Movie(movie.get('id'),
                  movie.get('title').replace('"', ''),
                  base_img_url + movie.get('poster_path'),
                  movie.get('popularity'),
                  movie.get('release_date').replace('"', ''),
                  movie.get('overview').replace('"', ''))
    return movie
