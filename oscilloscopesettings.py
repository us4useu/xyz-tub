from dataclasses import dataclass
from ctypes import c_int16, c_int32, c_uint32, c_float
# TODO Simplify settings' formats.A


@dataclass(frozen=True, kw_only=True)
class OscilloscopeSettings:
    channel: int  # PS5000A_CHANNEL[...]
    resolution: int  # PS5000A_DEVICE_RESOLUTION[...]
    coupling_type: int  # PS5000A_COUPLING[...]
    range: int  # PS5000A_RANGE[...]
    # TODO Converting from desired measurement time to number of samples (*or give a choice)
    sampling_frequency: float  # MHz / MSa/s
    n_samples: int  # In future change it to measurment_time
    # buffer_length: int # ?
    # signal_length: int # ?
    trigger_source: int  # PS5000A_CHANNEL[...]
    trigger_threshold: float   # mV
    # TODO Converting from time to number of samples
    delay: int  # Number of samples ^

    # Generator Configuration
    offset_voltage: int  # uV / microVolts
    Vpp: int  # uV / microVolts; max 4Vpp
    wave_type: int  # PS5000A_WAVE_TYPE
    signal_frequency: float  # kHz - presumption

