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
        payload = request.get_json()

        outing = payload.get('outing')
        person = payload.get('person')

        if outing and person:
            place_id = outing.get('place_id')
            origin_obj = person.get('origin')
            transport_type = outing.get('transport')

            if transport_type is None:
                return {'error': 'missing_transport_type'}, 400

            if origin_obj is not None and origin_obj.get('lat') and origin_obj.get('lng'):
                # get the zip code from the lat lng tuple
                origin_lat = origin_obj.get('lat')
                origin_lng = origin_obj.get('lng')
                reverse_geocode_result = gmaps.reverse_geocode((origin_lat, origin_lng))

                first_result = reverse_geocode_result[0]
                address_components = first_result.get('address_components')

                zip_code = None

                for component in address_components:
                    types = component.get('types')
                    if "postal_code" in types:
                        zip_code = component.get('long_name')

                # TODO: we get postal code from address components
            else:
                return {'error': 'missing person.origin[lat, lng]'}, 400

            if place_id is not None:
                # make a request to Google Places API
                place_json = requests.get('https://maps.googleapis.com/maps/api/place/details/json?place_id=' + place_id + '&fields=name,type,formatted_address,formatted_phone_number&key=' + GOOGLE_PLACES_API_KEY)
                place = place_json.json()

                if place.get('status') == 'OK':
                    # calculate the transit time based on the specified travel type
                    now = datetime.now()

                    # the destination address
                    destination = place['result'].get('formatted_address')

                    # make the origin lat, lng string
                    origin = str(origin_obj.get('lat')) + ',' + str(origin_obj.get('lng'))

                    # TODO: do this direction calculation for roundtrip, since that encapsulates the total risk

                    directions_result = gmaps.directions(origin,
                                                         destination,
                                                         mode=transport_type,
                                                         departure_time=now)

                    # print(directions_result)

                    legs = directions_result[0].get('legs')[0]  # assume this is one-leg trip
                    duration = legs.get('duration')
                    travel_time = duration.get('value')  # in seconds

                    # assemble model
                    for_model = {
                        "origin_zip_code": zip_code, # TODO: convert zip code to int ?
                        "transport_type": transport_type,
                        "trip_duration": travel_time,
                        "risk_factors": person.get('conditions'),
                        "age_group": person.get('age_group')
                    }

                    return {'feed_to_model': for_model}
                else:
                    return {'error': 'invalid_place_id'}, 400
            else:
                return {'error': 'missing_place_id_in_outing'}, 400
        else:
            return {'error': 'missing_outing_or_person'}, 400


api.add_resource(HelloWorld, '/')

api.add_resource(Risk, '/Risk')

if __name__ == '__main__':
    app.run(debug=True)
