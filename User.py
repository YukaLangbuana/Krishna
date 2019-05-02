from time import sleep
import datetime
import rticonnextdds_connector as rti

class User(object):

    def __init__(self, bus_route, departure, destination):
        self.bus_route = bus_route
        self.departure = departure
        self.destination = destination

    def get_on_bus(self):
        self.timestamp = str(datetime.datetime.now().time().strftime("%H:%M:%S"))


if __name__=='__main__':
    connector = rti.Connector("MyParticipantLibrary::Zero", "Bus.xml")
    operator = connector.getInput("Subscriber::BusSubscriber")

    user = User("EXPRESS1", 1, 4)
    status = True
    on_board_status = False
    current_vehicle = 0

    print("Waiting for the bus..")
    while status:
        operator.take()
        numOfSamples = operator.samples.getLength()
        for j in range(0, numOfSamples):
                if operator.infos.isValid(j):
                        bus_route = operator.samples.getString(j, "route")
                        vehicle = operator.samples.getString(j, "vehicle")
                        stop_number = int(operator.samples.getNumber(j, "stopNumber"))
                        timestamp = operator.samples.getString(j, "timestamp")
                        traffic_condition = operator.samples.getString(j, "trafficConditions")
                        stops_left = int(operator.samples.getNumber(j, "numStops")) - stop_number

                        if (stop_number==user.departure) and (bus_route==user.bus_route) and (not on_board_status):
                            on_board_status = True
                            current_vehicle = vehicle
                            print("Getting on {} at {}, {}, {} stops left".format(vehicle, timestamp, traffic_condition, stops_left))
                        elif (stop_number!=user.destination) and (current_vehicle==vehicle) and (bus_route==user.bus_route) and (on_board_status):
                            print("Arriving at stop #{}, at {}, {}, {} stops left".format(stop_number, timestamp, traffic_condition, stops_left))
                        elif (stop_number==user.destination) and (on_board_status):
                            print("Arriving at destination by {} at {}".format(vehicle, timestamp))
                            status = False
                            break
        sleep(1)