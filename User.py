from time import sleep
import datetime
import rticonnextdds_connector as rti
import sys

class User(object):

    def __init__(self, bus_route, departure, destination):
        self.bus_route = bus_route
        self.departure = departure
        self.destination = destination

    def get_on_bus(self):
        self.timestamp = str(datetime.datetime.now().time().strftime("%H:%M:%S"))


if __name__=='__main__':
    connector = rti.Connector("MyParticipantLibrary::Zero", "Bus.xml")
    position_subscription = connector.getInput("Subscriber::P2464_EECS_YUKALANGBUANA_POS")
    accident_subscription = connector.getInput("Subscriber::P2464_EECS_YUKALANGBUANA_ACC")

    user = User(str(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    status = True
    on_board_status = False
    current_vehicle = 0

    print("Waiting for the bus..")
    while status:
        position_subscription.take()
        num_of_busses_positions = position_subscription.samples.getLength()

        for j in range(0, num_of_busses_positions):
                if position_subscription.infos.isValid(j):
                        bus_route = position_subscription.samples.getString(j, "route")
                        vehicle = position_subscription.samples.getString(j, "vehicle")
                        stop_number = int(position_subscription.samples.getNumber(j, "stopNumber"))
                        time_between_stops = int(position_subscription.samples.getNumber(j, "timeBetweenStops"))
                        timestamp = position_subscription.samples.getString(j, "timestamp")
                        traffic_condition = position_subscription.samples.getString(j, "trafficConditions")
                        if user.destination < stop_number:
                            stops_left = user.destination - stop_number + int(position_subscription.samples.getNumber(j, "numStops"))
                        else:
                            stops_left = user.destination - stop_number

                        if (stop_number==user.departure) and (bus_route==user.bus_route) and (not on_board_status):
                            on_board_status = True
                            current_vehicle = vehicle
                            if time_between_stops > 10:
                                print("Getting on {} at {}, {}, accident, {} stops left".format(vehicle, timestamp, traffic_condition, stops_left))
                                pass
                            else:
                                print("Getting on {} at {}, {}, {} stops left".format(vehicle, timestamp, traffic_condition, stops_left))
                        elif (stop_number!=user.destination) and (current_vehicle==vehicle) and (on_board_status):
                            if time_between_stops > 10:
                                print("Arriving at stop #{}, at {}, {}, accident, {} stops left".format(stop_number, timestamp, traffic_condition, stops_left))
                            else:
                                print("Arriving at stop #{}, at {}, {}, {} stops left".format(stop_number, timestamp, traffic_condition, stops_left))
                        elif (stop_number==user.destination) and (current_vehicle==vehicle) and (on_board_status):
                            print("Arriving at destination by {} at {}".format(vehicle, timestamp))
                            status = False
                            break
        sleep(1)