# Here goes an instance of OscilloscopeSettings
from picosdk.ps5000a import ps5000a as ps
from oscilloscopesettings import OscilloscopeSettings

# TODO Use keywords while initializing. dataclass - kw_only?
oscilloscope_settings = OscilloscopeSettings(
    ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
    ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"],
    ps.PS5000A_COUPLING["PS5000A_DC"],
    ps.PS5000A_RANGE["PS5000A_2V"],
    8,
    2000,
    ps.PS5000A_CHANNEL["PS5000A_EXTERNAL"],
    0,  # Threshold in ADC value (int), for tests set to 0
    0
)
