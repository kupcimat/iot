import random
import re

import serial

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


mapping = {
    "random-value-generator": random_value_generator,
    "serial-reader": serial_reader
}
