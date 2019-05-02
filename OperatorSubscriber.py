from time import sleep
import rticonnextdds_connector as rti

connector = rti.Connector("MyParticipantLibrary::Zero", "Bus.xml")
position_subscription = connector.getInput("Subscriber::BusPositionSubscriber")
accident_subscription = connector.getInput("Subscriber::BusAccidentSubscriber")

print("MessageType {: >10}{: >18}{: >15}{: >15}{: >15}{: >20}{: >10}{: >15}".format("Route", "Vehicle", "Traffic", "Stop#", "#Stops", "TimeBetweenStops", "Fill%", "Timestamp"))

while True:
        position_subscription.take()
        accident_subscription.take()
        num_of_busses_positions = position_subscription.samples.getLength()
        num_of_accidents = accident_subscription.samples.getLength()

        if num_of_accidents > 0:
                for j in range(0, num_of_accidents):
                        if accident_subscription.infos.isValid(j):
                                bus_route = accident_subscription.samples.getString(j, "route")
                                vehicle = accident_subscription.samples.getString(j, "vehicle")
                                stop_number = accident_subscription.samples.getNumber(j, "stopNumber")
                                timestamp = accident_subscription.samples.getString(j, "timestamp")
                                print("Accident {: >15}{: >15}{: >30}{: >60}".format(bus_route, vehicle, int(stop_number), timestamp))
        
        if num_of_busses_positions > 0:
                for j in range(0, num_of_busses_positions):
                        if position_subscription.infos.isValid(j):
                                bus_route = position_subscription.samples.getString(j, "route")
                                vehicle = position_subscription.samples.getString(j, "vehicle")
                                traffic_condition = position_subscription.samples.getString(j, "trafficConditions")
                                stop_number = position_subscription.samples.getNumber(j, "stopNumber")
                                number_of_stops = position_subscription.samples.getNumber(j, "numStops")
                                time_at_each_stop = position_subscription.samples.getNumber(j, "timeBetweenStops")
                                fill_in_ratio = position_subscription.samples.getNumber(j, "fillInRatio")
                                timestamp = position_subscription.samples.getString(j, "timestamp")
                                print("Position {: >15}{: >15}{: >15}{: >15}{: >15}{: >15}{: >15}{: >15}".format(bus_route, vehicle, traffic_condition, int(stop_number), int(number_of_stops), time_at_each_stop, int(fill_in_ratio), timestamp))
        
        
        sleep(1)