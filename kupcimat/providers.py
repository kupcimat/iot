import random
import re
from xml.etree import ElementTree

import serial
import tornado.httpclient

import kupcimat.util


async def random_value_generator():
    return abs(35.0 * random.random())


def serial_reader(command, regex, port, baudrate):
    def callback():
        with serial.Serial(port, baudrate, timeout=5, exclusive=True) as ser:
            ser.write(f"{command}\n".encode())
            response = ser.readline().decode()
            match = re.search(regex, response)
            if match:
                return match.group(1)
            return None

    return kupcimat.util.with_retry(callback, "serial-reader", serial.SerialException)


# TODO extract async http client?
# TODO add timeout for async http client
async def atrea_reader(url, sensor, scale):
    http_client = tornado.httpclient.AsyncHTTPClient()
    try:
        response = await http_client.fetch(url)
        xml_root = ElementTree.fromstring(response.body)
        value = xml_root.find(f".//O[@I='{sensor}']").get("V")
        return float(value) * scale
    finally:
        http_client.close()


mapping = {
    "random-value-generator": random_value_generator,
    "serial-reader": serial_reader,
    "atrea-reader": atrea_reader
}
