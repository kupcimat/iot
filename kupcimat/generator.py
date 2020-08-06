import asyncio
import functools
import logging
import random

import webthing
import yaml

import kupcimat.providers
import kupcimat.util
import kupcimat.webthings
from kupcimat.validator import validate_yaml

MAPPING_SCHEMA_FILE = "mapping-schema.yaml"


def generate_webthings(filename):
    validate_yaml(MAPPING_SCHEMA_FILE, filename)
    with open(filename, "r") as file:
        mapping = yaml.safe_load(file)
        return list(map(generate_webthing, mapping["webthings"]))


def generate_webthing(mapping):
    name, properties = kupcimat.util.unwrap_dict(mapping)
    if "provider" in properties:
        return generate_sensor(name, properties)
    if "receiver" in properties:
        return generate_device(name, properties)


def generate_sensor(name, properties):
    value = webthing.Value(0.0)
    update_task = generate_update_task(
        sensor_id=properties["id"],
        callback=generate_webthing_function(properties["provider"]),
        callback_time=properties["update-interval"],
        value=value
    )

    # TODO can we get rid of duplication here?
    if name == "temperature-sensor":
        logging.debug("action=generate type=temperature-sensor id=%s", properties["id"])
        return kupcimat.webthings.TemperatureSensor(
            uri_id=properties["id"],
            title=properties["title"],
            description=properties.get("description", properties["title"]),
            value=value
        ), update_task
    if name == "humidity-sensor":
        logging.debug("action=generate type=humidity-sensor id=%s", properties["id"])
        return kupcimat.webthings.HumiditySensor(
            uri_id=properties["id"],
            title=properties["title"],
            description=properties.get("description", properties["title"]),
            value=value
        ), update_task
    if name == "power-sensor":
        logging.debug("action=generate type=power-sensor id=%s", properties["id"])
        return kupcimat.webthings.PowerSensor(
            uri_id=properties["id"],
            title=properties["title"],
            description=properties.get("description", properties["title"]),
            value=value
        ), update_task
    return None


def generate_device(name, properties):
    receive_task = generate_receive_task(
        sensor_id=properties["id"],
        callback=generate_webthing_function(properties["receiver"])
    )

    if name == "rgb-light":
        logging.debug("action=generate type=rgb-light id=%s", properties["id"])
        return kupcimat.webthings.RGBLight(
            uri_id=properties["id"],
            title=properties["title"],
            description=properties.get("description", properties["title"]),
            value_receiver=receive_task
        ), None
    if name == "segment-display":
        logging.debug("action=generate type=segment-display id=%s", properties["id"])
        return kupcimat.webthings.SegmentDisplay(
            uri_id=properties["id"],
            title=properties["title"],
            description=properties.get("description", properties["title"]),
            value_receiver=receive_task
        ), None
    return None


def generate_webthing_function(mapping):
    if type(mapping) is str:
        return kupcimat.providers.mapping[mapping]
    if type(mapping) is dict:
        name, properties = kupcimat.util.unwrap_dict(mapping)
        return functools.partial(kupcimat.providers.mapping[name], **properties)
    return None


def generate_update_task(sensor_id, callback, callback_time, value):
    async def update_value():
        try:
            new_value = await asyncio.wait_for(kupcimat.util.wrap_async(callback), timeout=5)
        except asyncio.TimeoutError:
            logging.debug("action=update-value id=%s status=timeout", sensor_id)
        except Exception as e:
            logging.debug("action=update-value id=%s status=error exception=%s", sensor_id, e)
        else:
            value.notify_of_external_update(new_value)
            logging.debug("action=update-value id=%s status=success value=%s", sensor_id, new_value)

    async def periodic_callback():
        while True:
            sleep_time = callback_time + round(0.2 * random.random() * callback_time)
            await update_value()
            await asyncio.sleep(sleep_time)

    return periodic_callback


def generate_receive_task(sensor_id, callback):
    async def receive_value(value):
        try:
            expanded_callback = kupcimat.util.update_partial(callback, functools.partial(expand_template, value=value))
            await asyncio.wait_for(kupcimat.util.wrap_async(expanded_callback), timeout=5)
        except asyncio.TimeoutError:
            logging.debug("action=receive-value id=%s status=timeout", sensor_id)
        except Exception as e:
            logging.debug("action=receive-value id=%s status=error exception=%s", sensor_id, e)
        else:
            logging.debug("action=receive-value id=%s status=success value=%s", sensor_id, value)

    return receive_value


def expand_template(template, value):
    if type(template) is str:
        return template.format(value)
    return template
