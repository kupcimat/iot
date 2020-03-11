import asyncio
import functools
import logging
import random

import webthing
import yaml

import kupcimat.providers
import kupcimat.util
import kupcimat.webthings


def generate_webthings(filename):
    # TODO error handling / mapping validation
    with open(filename, "r") as file:
        mapping = yaml.safe_load(file)
        return list(map(generate_webthing, mapping["webthings"]))


def generate_webthing(mapping):
    # TODO error handling / mapping validation
    (name, properties), = mapping.items()
    value = webthing.Value(0.0)
    update_task = generate_update_task(
        sensor_id=properties["id"],
        callback=generate_webthing_provider(properties["provider"]),
        callback_time=properties["update-interval"],
        value=value
    )

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


def generate_webthing_provider(mapping):
    # TODO error handling / mapping validation
    if type(mapping) is str:
        return kupcimat.providers.mapping[mapping]
    if type(mapping) is dict:
        (name, properties), = mapping.items()
        return functools.partial(kupcimat.providers.mapping[name], **properties)
    return None


def generate_update_task(sensor_id, callback, callback_time, value):
    async def update_value():
        try:
            new_value = await asyncio.wait_for(execute_callback(callback), timeout=5)
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


async def execute_callback(callback):
    if asyncio.iscoroutinefunction(kupcimat.util.unwrap_partial(callback)):
        return await callback()
    return await asyncio.get_running_loop().run_in_executor(executor=None, func=callback)
