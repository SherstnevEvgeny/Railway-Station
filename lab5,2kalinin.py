#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 11:31:44 2021

@author: swalk
"""

import simpy 
import numpy as np
import random
import matplotlib.pyplot as plt


class Order:
    def __init__(self):
        self.ordID = int()
        #self.ordTYPE = bool()
        self.ordLEN = 0.0
    

def generate_interval_car(a_c):
    return np.random.exponential(1/a_c)

def generate_interval_truck(a_t):
    return np.random.exponential(1/a_t)

def generate_interval_mixed(a_m):
    return np.random.exponential(1/a_m)

def company_run_car(env, ca, avg_c, mi):
    i = 0
    while True:
        i += 1
        tmp = Order()
        tmp.ordID = i
        tmp.ordLEN = 0.25
        #tmp.ordLEN = 0.25
        yield env.timeout(generate_interval_car(avg_c))
        
        
        env.process(car_order(env, tmp, ca, mi))
        
        
        
def company_run_truck(env, tr, avg_t, mi):
    i = 0
    while True:
        i += 1
        tmp = Order()
        tmp.ordID = i
        tmp.ordLEN = 1.0
        #tmp.ordLEN = 0.7
        yield env.timeout(generate_interval_truck(avg_t))
        
        
        env.process(truck_order(env, tmp, tr, mi))
        
def company_run_mixed(env, mi, avg_m):
    i = 0
    while True:
        i += 1
        tmp = Order()
        tmp.ordID = i
        tmp.ordLEN = random.choice([0.5, 1, 1.15, 1.5])
        yield env.timeout(generate_interval_mixed(avg_m))
        
        env.process(mixed_order(env, tmp, mi))

car_queue = []
truck_queue = []
mixed_queue = []

def car_order(env, temp, c, m):
    flag = 0
    #yield env.timeout(generate_interval_car())
    with c.request() as request1:
        with m.request() as request2:
            # request1 = c.request()
            # request2 = m.request()
            t_carrive = env.now
            print(env.now, temp.ordID, 'PASSENGER TRAIN arrived, approx time - {}'.format(temp.ordLEN))
            k = yield request1 | request2
            print(env.now, temp.ordID, 'PASSENGER TRAIN is delivering')
            t_cend = env.now
            if(request1.triggered == True and request2.triggered == False) or (request1.triggered == True and request2.triggered == True):
                m.release(request2)
                flag = 1
            else:
                flag = 2
                c.release(request1)
            yield env.timeout(temp.ordLEN)
            print(env.now, temp.ordID, 'PASSENGER TRAIN complete', flag)
            #t_cend = env.now
            # if(request1.triggered == True and request2.triggered == False) or (request1.triggered == True and request2.triggered == True):
            #     request2.cancel()
            #     car_queue.append(t_cend - t_carrive)
            # else:
            #     request1.cancel()
            #     mixed_queue.append(t_cend - t_carrive) 
            if flag == 1:
                car_queue.append(t_cend - t_carrive)
            else:
                mixed_queue.append(t_cend - t_carrive)
        
def truck_order(env, temp, t, m):
    #with t.request() | m.request() as request:
    flag = 0
    with t.request() as request1:
        with m.request() as request2:
            #request = t.request() | m.request()
            # request1 = t.request()
            # request2 = m.request()
            t_tarrive = env.now
            print(env.now, temp.ordID, 'TRUCK TRAIN arrived, approx time - {}'.format(temp.ordLEN))
            yield request1 | request2
            print(env.now, temp.ordID, 'TRUCK TRAIN is delivering')
            t_tend = env.now
            if(request1.triggered == True and request2.triggered == False) or (request1.triggered == True and request2.triggered == True):
                m.release(request2)
                flag = 1
            else:
                flag = 2
                t.release(request1)
            yield env.timeout(temp.ordLEN)
            print(env.now, temp.ordID, 'TRUCK TRAIN complete')
            #t_tend = env.now
            # if(request1.triggered == True and request2.triggered == False) or (request1.triggered == True and request2.triggered == True):
            #     truck_queue.append(t_tend - t_tarrive)
            # else:
            #     mixed_queue.append(t_tend - t_tarrive) 
            if flag == 1:
                truck_queue.append(t_tend - t_tarrive)
            else:
                mixed_queue.append(t_tend - t_tarrive) 


def mixed_order(env, temp, m):
    with m.request() as request:
        t_marrive = env.now
        print(env.now, temp.ordID, 'MIXED TRAIN  arrived, approx time - {}'.format(temp.ordLEN))
        yield request
        print(env.now, temp.ordID, 'MIXED TRAIN is delivering')
        t_mend = env.now
        yield env.timeout(temp.ordLEN)
        print(env.now, temp.ordID, 'MIXED TRAIN complete')
        #t_mend = env.now
        mixed_queue.append(t_mend - t_marrive)   
        


obs_times_car = []
obs_times_truck = []
obs_times_mixed = []
q_length_car = []
q_length_truck = []
q_length_mixed = []

def observe_car(env, cars):
    while True:
        obs_times_car.append(env.now)
        q_length_car.append(len(cars.queue))
        yield env.timeout(1)
        

def observe_truck(env, trucks):
    while True:
        obs_times_truck.append(env.now)
        q_length_truck.append(len(trucks.queue))
        yield env.timeout(1)

def observe_mixed(env, mixed):
    while True:
        obs_times_mixed.append(env.now)
        q_length_mixed.append(len(mixed.queue))
        yield env.timeout(1)
        
        
n_cars = int(input('Input the number of cars: '))

avg_cars = int(input('Input the average number of PASSANGER trains per hour: '))

n_trucks = int(input('Input number of trucks: '))

avg_trucks = int(input('Input the average number of TRUCK trains per hour: '))

n_mixed = int(input('Input the number of mixed platforms: '))

avg_mixed = int(input('Input the average number of MIXED trains per hour: '))

min_quanity = int(input('Input quanity of hours for test: '))



env = simpy.Environment()

car = simpy.Resource(env, capacity=n_cars)

truck = simpy.Resource(env, capacity=n_trucks)

mixed = simpy.Resource(env, capacity=n_mixed)

env.process(company_run_car(env, car, avg_cars, mixed))

env.process(company_run_truck(env, truck, avg_trucks, mixed))

env.process(company_run_mixed(env, mixed, avg_mixed))

env.process(observe_car(env, car))

env.process(observe_truck(env, truck))

env.process(observe_mixed(env, mixed))

env.run(until=min_quanity)

# plt.figure()
# plt.hist([car_queue, truck_queue, mixed_queue], label=['cars', 'trucks', 'mixed'])
# #plt.hist(truck_queue, label='trucks')
# plt.legend(loc='upper right')
# plt.xlabel('Waiting time (min)')
# plt.ylabel('Number of Customers')

plt.figure()
plt.step(obs_times_car, q_length_car, where='post')
plt.xlabel('time period(min)')
plt.ylabel('queue length')
plt.title('Passenger queue length dynamic')

plt.figure()
plt.step(obs_times_truck, q_length_truck, where='post')
plt.xlabel('time period(min)')
plt.ylabel('queue length')
plt.title('Truck queue length dynamic')

plt.figure()
plt.step(obs_times_mixed, q_length_mixed, where='post')
plt.xlabel('time period(min)')
plt.ylabel('queue length')
plt.title('Mixed queue length dynamic')


# print(np.random.exponential(1./3.0, 10))

#Aprint(s)