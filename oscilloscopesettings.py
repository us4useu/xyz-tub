from dataclasses import dataclass
from ctypes import c_int16  # , c_float
# TODO Simplify settings' formats.


@dataclass(frozen=True)
class OscilloscopeSettings:
    channel: int  # PS5000A_CHANNEL[...]
    resolution: int  # PS5000A_DEVICE_RESOLUTION[...]
    coupling_type: int  # PS5000A_COUPLING[...]
    range: int  # PS5000A_RANGE[...]
    # time_interval: c_float  # ctypes.c_float()
    # TODO Converting from sampling interval to timebase
    # TODO Converting from desired measurement time to number of samples
    timebase: int  # int
    n_samples: int  # In future change it to measurment_time
    trigger_source: int  # PS5000A_CHANNEL[...]
    # TODO Converting from mV to adc
    trigger_threshold: c_int16   # ADC value, probably'd like to change it to voltage
    # TODO Converting from time to number of samples
    delay: c_int16  # Number of samples ^
