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
