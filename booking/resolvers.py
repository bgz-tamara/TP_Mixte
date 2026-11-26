import json
import os
import requests
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

MOVIE_URL = os.environ.get("MOVIE_URL", "http://localhost:3001")
SCHEDULE_URL = os.environ.get("SCHEDULE_URL", "http://localhost:3002")

MOVIE_QUERY = """
query($id: String!) {
    movie_with_id(_id: $id) { id title director rating }
}
"""

def load_bookings():
    with open('{}/data/bookings.json'.format("."), "r") as file:
        return json.load(file)['bookings']

def write_bookings(bookings):
    with open('{}/data/bookings.json'.format("."), "w") as file:
        json.dump({'bookings': bookings}, file, indent=4)

# l'utilisateur concerné ou un administrateur
def check_permission(userid):
    verify_jwt_in_request()
    if get_jwt_identity() != userid and not get_jwt().get("admin", False):
        raise Exception("Missing permission")

def find_booking(bookings, userid):
    for booking in bookings:
        if booking['userid'] == userid:
            return booking

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
    booking = find_booking(load_bookings(), _userid)
    if not booking:
        raise Exception("No bookings for this user found")
    return booking

def booking_with_userid_date_movie(_,info,_userid,_date,_movieid):
    check_permission(_userid)
    day = find_date(find_booking(load_bookings(), _userid), _date)
    if not day:
        raise Exception("Booking not found")
    return {'date': _date, 'movies': [m for m in day['movies'] if m == _movieid]}


def resolve_movies_in_date(day, info):
    return [get_movie(movieid) or {'id': movieid} for movieid in day['movies']]


def add_booking(_,info,_userid,_date,_movieid):
    check_permission(_userid)
    if not movie_is_scheduled(_date, _movieid):
        raise Exception("Movie is not scheduled")

    bookings = load_bookings()
    booking = find_booking(bookings, _userid)
    if not booking:
        booking = {'userid': _userid, 'dates': []}
        bookings.append(booking)
    day = find_date(booking, _date)
    if not day:
        day = {'date': _date, 'movies': []}
        booking['dates'].append(day)
    if _movieid in day['movies']:
        raise Exception("Booking already exists")
    day['movies'].append(_movieid)
    write_bookings(bookings)
    return booking

def delete_booking(_,info,_userid,_date,_movieid):
    check_permission(_userid)
    bookings = load_bookings()
    booking = find_booking(bookings, _userid)
    day = find_date(booking, _date)
    if not day or _movieid not in day['movies']:
        raise Exception("Booking not found")
    day['movies'].remove(_movieid)
    if not day['movies']:
        booking['dates'].remove(day)
    if not booking['dates']:
        bookings.remove(booking)
    write_bookings(bookings)
    return booking
