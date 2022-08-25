from dataclasses import dataclass
from ctypes import c_int16  # , c_float
# TODO Simplify settings' formats.


@dataclass(frozen=True)
class OscilloscopeSettings:
    channel: int  # PS5000A_CHANNEL[...]
    resolution: int  # PS5000A_DEVICE_RESOLUTION[...]
    coupling_type: int  # PS5000A_COUPLING[...]
    range: int  # PS5000A_RANGE[...]
    # TODO Converting from desired measurement time to number of samples (*or give a choice)
    sampling_frequency: float
    n_samples: int  # In future change it to measurment_time
    trigger_source: int  # PS5000A_CHANNEL[...]
    trigger_threshold: float   # mV
    # TODO Converting from time to number of samples
    delay: c_int16  # Number of samples ^
