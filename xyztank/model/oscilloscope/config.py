# Here goes an instance of OscilloscopeSettings
from picosdk.ps5000a import ps5000a as ps
from settings import Settings
from dict import *

config = Settings(
    channel=channel["A"],
    resolution=resolution["12BIT"],
    coupling_type=coupling["DC"],
    range=range["20V"],
    sampling_frequency=1,
    # n_samples=20000,
    measurement_time=100,
    trigger_source=channel["A"],
    trigger_threshold=1000,  # Threshold in ADC value (int), for tests set to 0
    delay=0,

    # Generator Configuration
    offset_voltage=0,
    Vpp=4_000_000,  # Amplitude = 2 V
    wave_type=wave_type["SQUARE"],
    signal_frequency=1,
    impulse_length=10
)
