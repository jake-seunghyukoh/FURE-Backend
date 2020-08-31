from django.shortcuts import render
from django.db import models
from django.http import FileResponse
from django.http import HttpResponse


# rest_framework
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import json
import os
import sys
import urllib.request

from ..wsgi import Auth_Key


class WeatherView(APIView):
    def post(self, request):
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data)
        
        '"coord":{"lon":126.52,"lat":33.51}'
        
        coord = data['coord']
        lon = coord['lon']
        lat = coord['lat']

        url = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&lang=kr&units=metric'.format(lat, lon, Auth_Key)
        print(url)
        weather_api_request = urllib.request.Request(url)
        response = urllib.request.urlopen(weather_api_request)
        data_weather = json.loads(response.read())

        # response = HttpResponse(json.dumps(data_weather), content_type='application/json', status=status.HTTP_200_OK)
        # return response
        # data_weather = {"coord":{"lon":126.52,"lat":33.51},"weather":[{"id":803,"main":"Clouds","description":"튼구름","icon":"04n"}],"base":"stations","main":{"temp":27,"feels_like":33.32,"temp_min":27,"temp_max":27,"pressure":1011,"humidity":94},"visibility":10000,"wind":{"speed":1,"deg":50},"clouds":{"all":75},"dt":1598724281,"sys":{"type":1,"id":8087,"country":"KR","sunrise":1598735205,"sunset":1598781769},"timezone":32400,"id":1846266,"name":"Jeju City","cod":200}

        json_resp = {
            "weather_main": data_weather['weather'][0]['main'],
            "weather_description": data_weather['weather'][0]['description'],
            "weather_icon": data_weather['weather'][0]['icon'],
            "temp": (data_weather['main']['temp']),
            "humidity": data_weather['main']['humidity'],
            "wind_speed": data_weather['wind']['speed'],
            "wind_deg": data_weather['wind']['deg'],
            "cloud": data_weather['clouds']['all']
        }

        response = HttpResponse(json.dumps(json_resp), content_type='application/json', status=status.HTTP_200_OK)
        return response