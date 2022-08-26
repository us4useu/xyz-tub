# Here goes an instance of OscilloscopeSettings
from picosdk.ps5000a import ps5000a as ps
from oscilloscopesettings import OscilloscopeSettings


oscilloscope_settings = OscilloscopeSettings(
    channel=ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
    resolution=ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"],
    coupling_type=ps.PS5000A_COUPLING["PS5000A_DC"],
    range=ps.PS5000A_RANGE["PS5000A_20V"],
    sampling_frequency=10,
    n_samples=20000,
    trigger_source=ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
    trigger_threshold=0,  # Threshold in ADC value (int), for tests set to 0
    delay=0,

    # Generator Configuration
    offset_voltage=0,
    Vpp=5_000_000,
    wave_type=1,
    signal_frequency=1
)
