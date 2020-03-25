from webthing import Property, Thing, Value

import kupcimat.util


def create_value_forwarder(value_receiver, value_converter=None):
    def value_forwarder(value):
        kupcimat.util.execute_async(value_receiver(value))

    def value_forwarder_with_converter(value):
        kupcimat.util.execute_async(value_receiver(value_converter(value)))

    if value_converter is None:
        return value_forwarder
    return value_forwarder_with_converter


class TemperatureSensor(Thing):
    """A generic temperature sensor."""

    def __init__(self, uri_id, title, description, value):
        Thing.__init__(self, uri_id, title, ["TemperatureSensor"], description)

        self.add_property(
            Property(thing=self,
                     name="temperature",
                     value=value,
                     metadata={
                         "title": "Temperature",
                         "description": "The current temperature in °C",
                         "@type": "TemperatureProperty",
                         "type": "number",
                         "unit": "degree celsius",
                         "readOnly": True
                     }))


class MultiLevelSensor(Thing):
    """A generic multi-level sensor for properties within range 0-100 percent."""

    def __init__(self, uri_id, title, description, value, property_title, property_description):
        Thing.__init__(self, uri_id, title, ["MultiLevelSensor"], description)

        self.add_property(
            Property(thing=self,
                     name="temperature",
                     value=value,
                     metadata={
                         "title": property_title,
                         "description": property_description,
                         "@type": "LevelProperty",
                         "type": "number",
                         "unit": "percent",
                         "minimum": 0,
                         "maximum": 100,
                         "readOnly": True
                     }))


class HumiditySensor(MultiLevelSensor):
    """A generic humidity sensor."""

    def __init__(self, uri_id, title, description, value):
        MultiLevelSensor.__init__(self, uri_id, title, description, value, "Humidity", "The current humidity in %")


class PowerSensor(MultiLevelSensor):
    """A generic power sensor."""

    def __init__(self, uri_id, title, description, value):
        MultiLevelSensor.__init__(self, uri_id, title, description, value, "Power", "The current power in %")


class RGBLight(Thing):
    """A generic RGB light."""

    def __init__(self, uri_id, title, description, value_receiver):
        Thing.__init__(self, uri_id, title, ["Light"], description)

        self.add_property(
            Property(thing=self,
                     name="switch",
                     value=Value(
                         False,
                         create_value_forwarder(value_receiver, lambda x: 0xffffff if x else 0x000000)
                     ),
                     metadata={
                         "title": "Switch",
                         "description": "Light on/off switch",
                         "@type": "OnOffProperty",
                         "type": "boolean",
                         "readOnly": False
                     }))
        self.add_property(
            Property(thing=self,
                     name="color",
                     value=Value(
                         "#ffffff",
                         # TODO use hex value directly as arduino input?
                         create_value_forwarder(value_receiver, lambda x: int(x[1:], 16))  # convert #0000ff to 255
                     ),
                     metadata={
                         "title": "Color",
                         "description": "Light rgb color",
                         "@type": "ColorProperty",
                         "type": "string",
                         "readOnly": False
                     }))


class SegmentDisplay(Thing):
    """A generic 7-segment display."""

    def __init__(self, uri_id, title, description, value_receiver):
        Thing.__init__(self, uri_id, title, ["MultiLevelSwitch"], description)

        self.add_property(
            Property(thing=self,
                     name="switch",
                     value=Value(
                         False,
                         create_value_forwarder(value_receiver, lambda x: 1 if x else 0)
                     ),
                     metadata={
                         "title": "Switch",
                         "description": "Display on/off switch",
                         "@type": "OnOffProperty",
                         "type": "boolean",
                         "readOnly": False
                     }))
        self.add_property(
            Property(thing=self,
                     name="digit",
                     value=Value(
                         0,
                         create_value_forwarder(value_receiver)
                     ),
                     metadata={
                         "title": "Digit",
                         "description": "Display digit",
                         "@type": "LevelProperty",
                         "type": "integer",
                         "minimum": 0,
                         "maximum": 19,
                         "readOnly": False
                     }))
