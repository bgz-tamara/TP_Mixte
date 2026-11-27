import json
import os
import requests
from threading import Lock
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from pymongo import MongoClient

MOVIE_URL = os.environ.get("MOVIE_URL", "http://localhost:3001")
SCHEDULE_URL = os.environ.get("SCHEDULE_URL", "http://localhost:3002")

MOVIE_QUERY = """
query($id: String!) {
    movie_with_id(_id: $id) { id title director rating }
}
"""

client = MongoClient("mongodb://root:example@mongo:27017/")
db = client["movies"]

collection = db["bookings"]
if collection.count_documents({}) == 0:
    with open('./data/bookings.json', 'r') as file:
        bookings = json.load(file)["bookings"]
        collection.insert_many(bookings)
# un seul document par utilisateur
collection.create_index("userid", unique=True)

# une seule modification de réservation à la fois
booking_lock = Lock()

def load_bookings():
    collection = db["bookings"]
    bookings = list(collection.find({}, {"_id": 0}))
    return bookings

def load_booking(userid):
    return db["bookings"].find_one({'userid': userid}, {"_id": 0})

# enregistre la réservation d'un seul utilisateur, ou la supprime si elle est vide
def save_booking(booking):
    key = {'userid': booking['userid']}
    if booking['dates']:
        db["bookings"].replace_one(key, booking, upsert=True)
    else:
        db["bookings"].delete_one(key)

# l'utilisateur concerné ou un administrateur
def check_permission(userid):
    verify_jwt_in_request()
    if get_jwt_identity() != userid and not get_jwt().get("admin", False):
        raise Exception("Missing permission")

def find_date(booking, date):
    if booking:
        for day in booking['dates']:
            if day['date'] == date:
                return day

def get_movie(movieid):
    try:
        r = requests.post(f"{MOVIE_URL}/graphql",
                          json={"query": MOVIE_QUERY, "variables": {"id": movieid}})
    except requests.exceptions.RequestException:
        raise Exception("Movie service is not available")
    return (r.json().get("data") or {}).get("movie_with_id")

def movie_is_scheduled(date, movieid):
    try:
        r = requests.get(f"{SCHEDULE_URL}/schedules/{date}/{movieid}")
    except requests.exceptions.RequestException:
        raise Exception("Schedule service is not available")
    return r.status_code == 200


def all_bookings(_,info):
    return load_bookings()

def booking_with_userid(_,info,_userid):
    check_permission(_userid)
    booking = load_booking(_userid)
    if not booking:
        raise Exception("No bookings for this user found")
    return booking

def booking_with_userid_date_movie(_,info,_userid,_date,_movieid):
    check_permission(_userid)
    day = find_date(load_booking(_userid), _date)
    if not day:
        raise Exception("Booking not found")
    return {'date': _date, 'movies': [m for m in day['movies'] if m == _movieid]}


def resolve_movies_in_date(day, info):
    return [get_movie(movieid) or {'id': movieid} for movieid in day['movies']]


def add_booking(_,info,_userid,_date,_movieid):
    check_permission(_userid)
    if not movie_is_scheduled(_date, _movieid):
        raise Exception("Movie is not scheduled")

    with booking_lock:
        booking = load_booking(_userid) or {'userid': _userid, 'dates': []}
        day = find_date(booking, _date)
        if not day:
            day = {'date': _date, 'movies': []}
            booking['dates'].append(day)
        if _movieid in day['movies']:
            raise Exception("Booking already exists")
        day['movies'].append(_movieid)
        save_booking(booking)
    return booking

def delete_booking(_,info,_userid,_date,_movieid):
    check_permission(_userid)
    with booking_lock:
        booking = load_booking(_userid)
        day = find_date(booking, _date)
        if not day or _movieid not in day['movies']:
            raise Exception("Booking not found")
        day['movies'].remove(_movieid)
        if not day['movies']:
            booking['dates'].remove(day)
        save_booking(booking)
    return booking
