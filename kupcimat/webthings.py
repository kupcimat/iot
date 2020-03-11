from webthing import Property, Thing


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
