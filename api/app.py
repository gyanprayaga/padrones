# this takes in the model & feeds it to API
# we can deploy to cloud run :)

import os

from flask import Flask, request
from flask_restful import Resource, Api

# requests for google places API
import requests

# directions
import googlemaps
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# keys & such
GOOGLE_PLACES_API_KEY = 'AIzaSyACLuoDomujgtH1FgRDALg_eUDdwqDr1cg'

gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Risk(Resource):
    def post(self):
        '''
        1. Fetches travel time between origin & destination
        (which we find using the Google Maps API)
        2. Computes the Risk index using our model
        '''
        outing = request.get_json()

        if outing is not None:
            place_id = outing.get('place_id')

            if place_id is not None:
                # make a request to Google Places API
                place_json = requests.get('https://maps.googleapis.com/maps/api/place/details/json?place_id=' + place_id + '&fields=name,type,formatted_address,formatted_phone_number&key=' + GOOGLE_PLACES_API_KEY)
                place = place_json.json()

                if place.get('status') == 'OK':
                    # calculate the transit time based on the specified travel type
                    now = datetime.now()

                    'walking', 'car',

                    directions_result = gmaps.directions("Sydney Town Hall",
                                                         "Parramatta, NSW",
                                                         mode="transit",
                                                         departure_time=now)

                    legs = directions_result.get('legs')
                    duration = legs.get('duration')
                    travel_time = duration.get('value')  # in seconds



                    return {'destination': place, 'travel_time': travel_time}
                else:
                    return {'error': 'invalid_place_id'}, 400
            else:
                return {'error': 'missing_place_id_in_outing'}, 400
        else:
            return {'error': 'missing_outing'}, 400


api.add_resource(HelloWorld, '/')

api.add_resource(Risk, '/Risk')

if __name__ == '__main__':
    app.run(debug=True)
