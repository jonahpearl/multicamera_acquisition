import struct
import numpy
import warnings
from tqdm.autonotebook import tqdm


def packIntAsLong(value):
    """Packs a python 4 byte integer to an arduino long
    Parameters
    ----------
    value : int
        A 4 byte integer
    Returns
    -------
    packed : bytes
        A 4 byte long
    """
    return struct.pack("i", value)


def unpackIntAsLong(byte_data):
    """Unpacks an arduino long to a python 4 byte integer
    Parameters
    ----------
    byte_data : bytes
        A 4 byte long array from an arduino

    Returns
    -------
    unpacked : int
        A
    """
    # Ensure that the byte data is exactly 4 bytes
    if len(byte_data) != 4:
        raise ValueError("Exactly 4 bytes are required.")

    # Unpack the bytes to an integer
    return struct.unpack('<i', byte_data)[0]


def wait_for_serial_confirmation(
    arduino, expected_confirmation, seconds_to_wait=5, timeout_duration_s=0.1
):
    confirmation = None
    for i in range(int(seconds_to_wait / timeout_duration_s)):
        confirmation = arduino.readline().decode("utf-8").strip("\r\n")
        if confirmation == expected_confirmation:
            print("Confirmation recieved: {}".format(confirmation))
            break
        else:
            if len(confirmation) > 0:
                warnings.warn(
                    'PySerial: "{}" confirmation expected, got "{}"". Trying again.'.format(
                        expected_confirmation, confirmation
                    )
                )
    if confirmation != expected_confirmation:
        raise ValueError(
            'Confirmation "{}" signal never recieved from Arduino'.format(
                expected_confirmation
            )
        )
    return confirmation
