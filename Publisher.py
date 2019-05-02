###############################################################################
# (c) 2005-2015 Copyright, Real-Time Innovations.  All rights reserved.       #
# No duplications, whole or partial, manual or electronic, may be made        #
# without express written permission.  Any such copies, or revisions thereof, #
# must display this notice unaltered.                                         #
# This code contains trade secrets of Real-Time Innovations, Inc.             #
###############################################################################

"""Samples's writer."""

from time import sleep
import datetime
import rticonnextdds_connector as rti
import random
import configparser
import threading
import math

class Publisher(object):

    def __init__(self):
        self.busses = []

    def add_bus(self, bus_object):
        self.busses.append(bus_object)

    def run_all(self):
        threads = list()
        for bus in self.busses: 
            one_thread = threading.Thread(target=bus.run_bus_service)
            threads.append(one_thread)
            print("Thread {} initialized".format(bus.vehicle))
        
        sleep(2)
        print("All busses have started. Waiting for them to terminate...")
        for thread in threads:
            thread.start()


class Bus(object):

    def __init__(self, bus_route, vehicle, number_of_stops, time_between_stops):
        self.initial_time_between_stops = time_between_stops
        self.bus_route = bus_route
        self.vehicle = vehicle
        self.number_of_stops = number_of_stops
        self.time_between_stops = time_between_stops
        self.stop_number = 0
        
        self.traffics = self.assign_traffic(number_of_stops)
        self.accidents = self.assign_accident(number_of_stops)

        self.connector = rti.Connector("MyParticipantLibrary::Zero", "Bus.xml")
        self.position_publisher = self.connector.getOutput("Publisher::BusPositionPublisher")
        self.accident_publisher = self.connector.getOutput("Publisher::BusAccidentPublisher")

    
    def assign_traffic(self, number_of_stops):
        traffic_condition = []
        [traffic_condition.append("heavy") for i in range(math.ceil(number_of_stops * 3 * 10 / 100))]
        [traffic_condition.append("light") for i in range(math.ceil(number_of_stops * 3 * 25 / 100))]
        [traffic_condition.append("normal") for i in range(math.ceil(number_of_stops * 3 * 65 / 100))]
        random.shuffle(traffic_condition)
        return traffic_condition
    
    def assign_accident(self, number_of_stops):
        accident_stop_num = []
        [accident_stop_num.append(random.randint(1, number_of_stops)) for i in range(math.ceil(number_of_stops * 3 * 10 / 100))]
        return accident_stop_num

    def generate_update(self, accident_status=False):
        if accident_status==True:
            self.timestamp = str(datetime.datetime.now().time().strftime("%H:%M:%S"))
            self.time_between_stops += 10
        else:
            self.timestamp = str(datetime.datetime.now().time().strftime("%H:%M:%S"))
            self.traffic_condition = self.traffics.pop()

            if self.traffic_condition == "heavy":
                self.time_between_stops = self.time_between_stops + (self.time_between_stops * 50/100)
            elif self.traffic_condition == "light":
                self.time_between_stops = self.time_between_stops - (self.time_between_stops * 25/100)

            if self.stop_number == self.number_of_stops:
                self.stop_number = 1
            else:
                self.stop_number += 1


    def publish_position(self, accident_status=False):
        self.generate_update()
        self.position_publisher.instance.setString("timestamp", self.timestamp)
        self.position_publisher.instance.setString("route", self.bus_route)
        self.position_publisher.instance.setString("vehicle", self.vehicle)
        self.position_publisher.instance.setNumber("stopNumber", self.stop_number)
        self.position_publisher.instance.setNumber("numStops", self.number_of_stops)
        self.position_publisher.instance.setString("trafficConditions", self.traffic_condition)
        self.position_publisher.instance.setNumber("fillInRatio", random.randint(1, 100))

        if accident_status==True:
            self.position_publisher.instance.setNumber("timeBetweenStops", self.time_between_stops+10)
        else:
            self.position_publisher.instance.setNumber("timeBetweenStops", self.time_between_stops)

        self.position_publisher.write()

        return "{} published a position message at stop #{} on route {} at {}".format(self.vehicle, self.stop_number, self.bus_route, self.timestamp)
    

    def publish_accident(self):
        self.generate_update(accident_status=True)
        self.accident_publisher.instance.setString("timestamp", self.timestamp)
        self.accident_publisher.instance.setString("route", self.bus_route)
        self.accident_publisher.instance.setString("vehicle", self.vehicle)
        self.accident_publisher.instance.setNumber("stopNumber", self.stop_number)
        self.accident_publisher.write()

        return "{} published an accident message at stop #{} on route {} at {}".format(self.vehicle, self.stop_number, self.bus_route, self.timestamp) 


    def run_bus_service(self):
        for i in range(3):
            for i in range(self.number_of_stops):
                #reset
                self.time_between_stops = self.initial_time_between_stops
                try:
                    #bus_stop_with_accident returns the stop number where an accident occurs
                    bus_stop_with_accident = self.accidents[-1]

                    if self.stop_number == bus_stop_with_accident:
                        position_response = self.publish_position(accident_status=True)
                        accident_response = self.publish_accident()
                        print(position_response)
                        print(accident_response)
                    else:
                        position_response = self.publish_position()
                        print(position_response)
                    sleep(self.time_between_stops)
                except:
                    print("error occured. No accident detected")





if __name__ == "__main__":

    print("Launching publishers...")

    publisher = Publisher()

    config = configparser.ConfigParser()
    config.read('properties.ini')
    routes = config['DEFAULT']['ROUTES'].split(",")
    

    for route in routes:
        num_stops = int(config[route]['NUM_STOPS'])
        time_between_stops = int(config[route]['TIME_BETWEEN_STOPS'])
        route_busses = config[route]['VEHICLES'].split(",")
        for bus_number in range(len(route_busses)):
            publisher.add_bus(Bus(route, route_busses[bus_number], num_stops, time_between_stops))


    sleep(2)

    publisher.run_all()