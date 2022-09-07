from dataclasses import dataclass
from ctypes import c_int16, c_int32, c_uint32, c_float
# TODO Simplify settings' formats.A
# TODO Checking if config values are sensible.
# It's possible to use @property decorator.
# https://stackoverflow.com/questions/70686205/how-to-limit-values-in-dataclass-attribute


@dataclass(frozen=True, kw_only=True)
class OscilloscopeSettings:
    channel: int  # PS5000A_CHANNEL[...]
    resolution: int  # PS5000A_DEVICE_RESOLUTION[...]
    coupling_type: int  # PS5000A_COUPLING[...]
    range: int  # PS5000A_RANGE[...]
    # TODO Converting from desired measurement time to number of samples (*or give a choice)
    sampling_frequency: float  # MHz / MSa/s
    n_samples: int  # In future change it to measurment_time
    # measurement_time: float # ms
    # buffer_length: int # ?
    trigger_source: int  # PS5000A_CHANNEL[...]
    trigger_threshold: float   # mV
    # delay: int  # Number of samples ^
    delay: float  # ms

    # Generator Configuration
    offset_voltage: int  # uV / microVolts
    Vpp: int  # uV / microVolts; max 4Vpp
    wave_type: int  # PS5000A_WAVE_TYPE
    signal_frequency: float  # kHz - presumption
    impulse_length: float  # seconds
