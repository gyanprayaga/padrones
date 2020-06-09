# this takes in the model & feeds it to API
# we can deploy to cloud run :)

import os

from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

# requests for google places API
import requests

# directions
import googlemaps
from datetime import datetime

# for reading CSV
import csv

# for flooring numbers
import math

app = Flask(__name__)
CORS(app)
api = Api(app)

# keys & such
GOOGLE_PLACES_API_KEY = 'AIzaSyACLuoDomujgtH1FgRDALg_eUDdwqDr1cg'

NEIGHBORHOOD_RISK_URL = 'https://firebasestorage.googleapis.com/v0/b/onvozzy.appspot.com/o/files%2Flac_zips_risk_min.csv?alt=media&token=c581fcdc-ae66-4729-aa26-9e477ebce083'

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

        if request.headers.get('Authorization') != 'romkey_eats_padrones_123':
            return {'error': 'unauthorized'}, 401

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
                place_json = requests.get('https://maps.googleapis.com/maps/api/place/details/json?place_id=' + place_id + '&fields=name,type,formatted_address,address_component,formatted_phone_number&key=' + GOOGLE_PLACES_API_KEY)
                place = place_json.json()

                if place.get('status') == 'OK':
                    # calculate the transit time based on the specified travel type
                    now = datetime.now()

                    # the destination address
                    destination = place['result'].get('formatted_address')

                    # TODO: get the destination zip code
                    dest_address_components = place['result'].get('address_components')
                    destination_zip_code = None

                    for component in dest_address_components:
                        types = component.get('types')
                        if "postal_code" in types:
                            destination_zip_code = component.get('long_name')

                    # TODO: we get postal code from address components

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

                    #
                    # Calculate the Risk
                    #
                    # Weighting system (for reference)
                    weights = {
                        'transport': 10,
                        'neighborhood': 20,
                        'activity': 30,
                        'persona': 40,
                    }

                    # get my neighborhood

                    # assemble model
                    risk_factors = {
                        "origin_zip_code": zip_code, # TODO: convert zip code to int ?
                        "destination_zip_code": destination_zip_code,
                        "transport_type": transport_type,
                        "trip_duration": travel_time,
                        "activity": outing.get('activity'),
                        "health_conditions": person.get('conditions'),
                        "age_group": person.get('age_group')
                    }

                    # print('Received risk factors', risk_factors)

                    # get the CSV data
                    zips_and_risk = {}

                    response = requests.get(NEIGHBORHOOD_RISK_URL)
                    if response.status_code != 200:
                        return {'error': 'error_getting_csv'}, 400
                        # print('Failed to get data:', response.status_code)
                    else:
                        wrapper = csv.reader(response.text.strip().split('\n'))

                        # get the rows (skip the header)
                        for record in wrapper:
                            if record[0] == 'ZIP Code':
                                continue

                            zip_code = str(record[0])
                            zips_and_risk[zip_code] = record[1]

                    # print(neighborhood_risk_data)

                    # print(neighborhood_risk_data)
                    #


                    neighborhood_risk_pts = {
                        'Very high risk': 20,
                        'High risk': 15,
                        'Medium risk': 10,
                        'Low risk': 5
                    }

                    personal_risk_pts = {
                        'age': {
                            '0-30': 0,
                            '31-50': 2,
                            '51-64': 5,
                            '65+': 10
                        },
                        'conditions': {
                            'diabetes': 10,
                            'hypertension': 10,
                            'heart_or_lung_disease': 10
                        }
                    }

                    transport_risk_pts = {
                        'driving': 2,
                        'bicycling': 2,
                        'walking': 2,
                        'transit': 10
                    }

                    activities_risk_pts = {
                        'walking': 0,
                        'running': 0,
                        'high_contact_sport': 18,
                        'low_contact_sport': 6,
                        'park': 6,
                        'barbecue': 6,
                        'restaurant_outdoor': 8,
                        'crowded_outdoor': 12,
                        'playground': 18,
                        'swimming': 21,
                        'shopping': 15,
                        'grocery': 9,
                        'worship_center': 24,
                        'hair_salon': 18,
                        'library': 8,
                        'museum': 8,
                        'dinner_party': 12,
                        'restaurant_indoor': 15,
                        'bar': 30,
                        'doctor': 12,
                        'crowded_indoor': 28
                    }

                    # start calculating
                    my_risk = {}

                    my_flags = []

                    # sets the neighborhood risk
                    zip_code = risk_factors['origin_zip_code'].strip()
                    if zip_code in zips_and_risk:
                        risk_level_text = zips_and_risk[zip_code]
                        my_risk['neighborhood'] = neighborhood_risk_pts.get(risk_level_text)
                    else:
                        return {'error': 'zip_code_not_in_LA'}, 400

                    # set the age risk
                    age_band = risk_factors['age_group']
                    if age_band in personal_risk_pts.get('age'):
                        my_risk['age'] = personal_risk_pts['age'][age_band]
                    else:
                        return {'error': 'invalid_age_band'}, 400

                    # set the activity risk
                    activity = risk_factors['activity']
                    if activity in activities_risk_pts:
                        my_risk['activity'] = activities_risk_pts.get(activity)
                    else:
                        return {'error': 'invalid_activity'}, 400

                    # tallies & sets the conditions
                    conditions = risk_factors['health_conditions']
                    my_risk['conditions'] = 0
                    for condition in conditions:
                        if condition in personal_risk_pts['conditions']:
                            condition_risk = personal_risk_pts['conditions'].get(condition)
                            my_risk['conditions'] += condition_risk
                        else:
                            return {'error': 'invalid_condition'}, 400

                    # sets the transport risk
                    transport = risk_factors['transport_type']
                    if transport == 'transit':
                        trip_duration_fiveminchunks = int(risk_factors["trip_duration"]/300)
                        transport_risk_score = transport_risk_pts['transit'] + trip_duration_fiveminchunks

                        my_risk['transport'] = transport_risk_score
                    elif transport_risk_pts.get(transport):
                        # just assign based on object
                        my_risk['transport'] = transport_risk_pts[transport]
                    else:
                        return {'error': 'invalid_transport_type'}, 400

                    print(my_risk)

                    # risky business
                    my_total_risk = my_risk['neighborhood'] + my_risk['age'] + my_risk['conditions'] + my_risk['activity'] + my_risk['transport']
                    print('my risk: ', my_total_risk) # raw risk

                    # risk level (1-5)
                    risk_level = math.ceil(my_total_risk / 20)

                    # add a new person risk
                    my_risk['persona'] = my_risk['age'] + my_risk['conditions']
                    print('my person risk', my_risk['persona'])

                    risks_to_flag = ['persona', 'transport', 'activity']

                    for risk_type in risks_to_flag:
                        risk_threshold = .75 * weights[risk_type]
                        print('risk threshold for ' + risk_type + ':', risk_threshold)

                        if my_risk[risk_type] >= risk_threshold:
                            # uh oh, over risk threshold lets call a flag
                            my_flags.append(risk_type)

                    return {'raw_risk': my_total_risk, 'risk_level': risk_level, 'flags': my_flags}
                else:
                    return {'error': 'invalid_place_id'}, 400
            else:
                return {'error': 'missing_place_id_in_outing'}, 400
        else:
            return {'error': 'missing_outing_or_person'}, 400


api.add_resource(HelloWorld, '/')

api.add_resource(Risk, '/Risk')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
