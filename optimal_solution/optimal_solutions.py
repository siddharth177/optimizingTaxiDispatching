# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 08:56:02 2022

@author: siddh
"""


import pandas as pd
import numpy as np
import gurobipy
from gurobipy import tuplelist
from geopy.distance import great_circle
import math
import itertools
import random
import os
import shutil
from matplotlib import pyplot as plt
import math

EAV_range = 200.0 #miles
avg_speed_NYC = 13.0 #mph
power_consumption_rate = 0.3 #kWh/mi
need_charging = 0.2 #SOC<20% range
charge_upto = 0.8*EAV_range #charge upto 80%

max_pickup_time = 30.0 #minutes
max_pickup_dist = max_pickup_time*avg_speed_NYC/60 #miles
max_wait_time = 15.0
charging_power = 50.0 #kW

customer_csv = pd.read_csv('customer_trip_data.csv')
customer_id = customer_csv["customer_id"]
pickup_longitude = customer_csv["pickup_longitude"]
pickup_lattitude = customer_csv["pickup_lattitude"]
dropoff_longitude = customer_csv["dropoff_longitude"]
dropoff_lattitude = customer_csv["dropoff_lattitude"]
waiting_time = customer_csv["customer_waiting_time(mins)"]
print(customer_id, pickup_longitude, pickup_lattitude, dropoff_longitude, dropoff_lattitude, waiting_time)

taxi_csv = pd.read_csv('taxi_data.csv')
taxi_longitude = taxi_csv["taxi_longitude"]
taxi_lattitude = taxi_csv["taxi_lattitude"]
taxi_soc = taxi_csv["soc"]

charging_csv = pd.read_csv('charging_data.csv')
charging_longitude = charging_csv["charging_longitude"]
charging_lattitude = charging_csv["charging_lattitude"]

pickup_GPS = []
dropoff_GPS = []
trip_distance = []
trip_time = []

charging_GPS= []
charging_distance = []
for j in range(len(pickup_longitude)):
  pickup_GPS[j] = (pickup_lattitude, pickup_lattitude)
  dropoff_GPS[j] = (dropoff_lattitude, dropoff_longitude)
  charging_GPS[j] = (charging_lattitude, charging_longitude)
  trip_distance[j] = 1.4413*great_circle(pickup_GPS, dropoff_GPS).miles + 0.1383 #miles
  charging_distance[j] = 1.4413*great_circle(dropoff_GPS, charging_GPS).miles + 0.1383 #miles

taxi_GPS = []
pickup_distance = [[0 for j in range(pickup_lattitude)] for i in range(taxi_lattitude)]
pickup_time = [[0 for j in range(pickup_lattitude)] for i in range(taxi_lattitude)]
for i in range(len(taxi_lattitude)):
  taxi_GPS[i] = (taxi_lattitude, taxi_longitude)
  for j in range(len(pickup_lattitude)):
    pickup_distance[i][j] = 1.4413*great_circle(taxi_GPS, pickup_GPS).miles + 0.1383 #miles
    pickup_time[i][j] = pickup_distance[i][j]/avg_speed_NYC

model = Model()
model.setParam('OutputFlag', 0)