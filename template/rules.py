
from att_event_engine.when import When
from att_event_engine.resources import Sensor, Actuator, Device, Gateway, Parameter
from att_event_engine.timer import Timer
import att_event_engine.factory as factory



battery = factory.Sensor(name="battery")


@When([battery], lambda: battery.current.value < 20)
def battery_low():
    battery.connection.pushNotification("battery is low")

