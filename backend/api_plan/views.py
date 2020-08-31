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
import numpy as np

from ..wsgi import db

class PlanView(APIView):
    def post(self, request):
        raw_data = request.body.decode('utf-8')
        data = json.loads(raw_data)

        uid = data['uid']

        db_ptr = db.collection(u'users').document(u'App').collection(u'info').document(uid)
        data = db_ptr.get().to_dict()
        try:
            gender = data['gender']
            height = float(data['height'])
            weight = float(data['weight'])
            goal = float(data['goal'])
            interval = 7 / float(data['days'])
            time = float(data['time'])
        except:
            response = HttpResponse(json.dumps({"status":"wrong user data"}), content_type='application/json', status=400)
            return response

        print("\ngender: {} height: {} weight: {} goal: {} interval: {} time: {}\n".format(gender, height, weight, goal, interval, time))
        
        methd_two = cal_MET(uid, gender, height, weight, goal, 60, "two")
        methd_four = cal_MET(uid, gender, height, weight, goal, 120, "four")
        methd_six = cal_MET(uid, gender, height, weight, goal, 180, "six")
        plans = [["Two", methd_two], ["Four", methd_four], ["Six", methd_six]]
        
        dic = {}
        
        dic['now'] = BMI(height, weight)
        dic['goal'] = BMI(height, goal)

        for plan in plans:
            met = plan[1] * interval / time

            speed = 0.5682 * met + 4.2182 
            
            dic[plan[0]] = speed * 0.6
            
        response = HttpResponse(json.dumps(dic), content_type='application/json', status=status.HTTP_200_OK)
        return response
    
    def get(self, request):
        # raw_data = request.body.decode('utf-8')
        # data = json.loads(raw_data)

        response = HttpResponse(json.dumps({"status":"ok"}), content_type='application/json', status=status.HTTP_200_OK)
        return response
    
    def put(self, request):
        # raw_data = request.body.decode('utf-8')
        # data = json.loads(raw_data)

        response = HttpResponse(json.dumps({"status":"ok"}), content_type='application/json', status=status.HTTP_200_OK)
        return response
    
    def delete(self, request):
        # raw_data = request.body.decode('utf-8')
        # data = json.loads(raw_data)

        response = HttpResponse(json.dumps({"status":"ok"}), content_type='application/json', status=status.HTTP_200_OK)
        return response



# PLANNNNNNNNN
def BMI(height, weight):
    return weight / (height / 100) ** 2


def coeff(weight, gender):

    if gender == 'Male':
        value = 0.0459 * np.exp(0.4997 * weight)
    elif gender == "Female":
        value = 0.0135 * np.exp(0.9739 * weight)
    else:
        value = None

    return value


def MET(weight, exercising_time):
    value = weight * exercising_time * 0.0035
    return value


def cal_MET(uid, gender, height, weight_now, weight_goal, time, name):
    # CONST_1 = 21.7404
    # CONST_2 = 22.3778
    # CONST_3 = 87.1398

    h = float(height)
    w = float(weight_now)
    g = float(weight_goal)
    t = int(time)

    bmi_now = BMI(h, w)
    bmi_goal = BMI(h, g)

    # # Poly
    # c = CONST_1 * (np.log(CONST_2 - bmi_now) - np.log(bmi_now + CONST_3))
    # methd = (CONST_1 * (np.log(CONST_2 - bmi_goal) - np.log(bmi_goal + CONST_3)) - c) / t

    # Exp
    if gender == 'M':
        c = np.exp(-0.279 * bmi_now)
        methd = 24 * (np.exp(-0.279 * bmi_goal) - c) / (t * 1.07e-4 * 0.279)
    else:
        c = np.exp(-0.52 * bmi_now)
        methd = 24 * (np.exp(-0.52 * bmi_goal) - c) / (t * 3.06e-7 * 0.52)

    db_ptr = db.collection(u'users').document(u'App').collection(u'info').document(uid).collection(u'prediction').document('data')
    if name == "two":
        db_ptr.set({
            "methd_" + name : methd,
            "const_" + name : c
        })
    else:
        db_ptr.update({
            "methd_" + name : methd,
            "const_" + name : c
        })

    # print("bmi: {} goal:{} constant: {} METh/d: {}".format(bmi_now, bmi_goal, c, methd))

    return methd


if __name__ == "__main__":
    print("**************************************************\n"
          "MET 는 체중 1kg 이 1분 동안 사용하는 산소 소비량 mL을 의미한다.\n"
          "1 MET는 3.5mL이며 TV 시청과 수면이 1MET 활동이다.\n"
          "70kg 인 사람이 10분 TV를 시청하면 얼마의 에너지를 소비할까?\n"
          "3.5(mL) X 1(MET) X 70(kg) X 10(min) = 2350mL\n"
          "산소 1L는 5kcal 를 소모하니 12.24kcal를 소비하는 셈이다.\n"
          "\n"
          "[운동 예시]\n"
          "5.0km/h : 4 MET\n"
          "8.0km/h : 8 MET\n"
          "10.0km/h : 10 MET\n"
          "**************************************************\n")
    gender = input("성별(M/W): ")
    height = input("키(cm): ")
    weight = input("현재 체중(kg): ")
    goal = input("목표 체중(kg): ")
    interval = float(input("며칠에 한 번 운동: "))
    time = float(input("운동 가능 시간: "))

    methd_two = cal_MET(height, weight, goal, 60)
    methd_four = cal_MET(height, weight, goal, 120)
    methd_six = cal_MET(height, weight, goal, 180)
    plans = [["Two ", methd_two], ["Four", methd_four], ["Six ", methd_six]]

    print("")
    for plan in plans:
        met = plan[1] * interval / time
        if met < 8:
            speed = "Jog"
        elif met < 9:
            speed = "5 mph"
        elif met < 10:
            speed = "5.2 mph"
        elif met < 11:
            speed = "6 mph"
        elif met < 11.5:
            speed = "6.7 mph"
        elif met < 12.5:
            speed = "7 mph"
        elif met < 13.5:
            speed = "7.5 mph"
        elif met < 14:
            speed = "8 mph"
        elif met < 15:
            speed = "8.6 mph"
        elif met < 16:
            speed = "9 mph"
        elif met < 18:
            speed = "10 mph"
        else:
            speed = "10.9 mph"
        print(plan[0] + ' month plan: {} {} hours every {} days ({} MET)'.format(speed, time, interval, met))