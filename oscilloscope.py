import ctypes
from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import assert_pico_ok
from picosdk.errors import PicoSDKCtypesError


class Oscilloscope:
    """A class responsible for managing the oscilloscope."""

    def __init__(self):
        self.chandle = ctypes.c_int16()
        self.channel = None
        self.coupling_type = None
        self.range = None
        self.timeinterval = None
        self.timebase = None
        self.n_samples = None
        self.trigger_source = None
        self.trigger_threshold = None  # TODO Converting from mV to adc
        self.delay = None  # TODO Converting from time to number of samples
        # Do we want our data_buffer to be global? Maybe just put it in runMeasurement method?
        self.data_buffer = None

        self.status = {}
        # TODO Importing resolution from configuration
        self.resolution = ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"]
        # Open the oscilloscope
        # TODO Move it to another method that throws an exception so that you can rerun it.
        self.status["openunit"] = ps.ps5000aOpenUnit(ctypes.byref(self.chandle), None, self.resolution)
        try:
            assert_pico_ok(self.status["openunit"])
        except PicoSDKCtypesError:

            powerstatus = self.status["openunit"]
            # TODO Check for other possible power supply errors
            # PICO_USB3_0_DEVICE_NON_USB3_0_PORT
            if powerstatus == 286:
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(self.chandle, powerstatus)
            # PICO_POWER_SUPPLY_NOT_CONNECTED
            elif powerstatus == 282:
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(self.chandle, powerstatus)
            else:
                raise

            assert_pico_ok(self.status["changePowerSource"])

        # find maximum ADC value
        self.maxADC = ctypes.c_int16()
        self.status["maximumValue"] = ps.ps5000aMaximumValue(self.chandle, ctypes.byref(self.maxADC))
        # TODO Throw an exception
        assert_pico_ok(self.status["maximumValue"])

    def setChannel(self):
        # TODO Importing from config
        self.channel = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"]
        self.coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        self.range = ps.PS5000A_RANGE["PS5000A_2V"]
        self.status["setChannel"] = ps.ps5000aSetChannel(self.chandle, self.channel, 1, self.coupling_type,
                                                         self.range, 0)
        # TODO Throw an exception
        assert_pico_ok(self.status["setChannel"])

        # TODO Converting from sampling interval to timebase
        # TODO Converting from desired measurement time to number of samples
        self.timebase = 8
        self.n_samples = 2000
        self.timeinterval = ctypes.c_float()
        # None in arguments works as a NULL pointer
        self.status["getTimebase2"] = ps.ps5000aGetTimebase2(self.chandle, self.timebase, self.n_samples,
                                                             ctypes.byref(self.timeinterval), None, 0)
        # TODO Add setting trigger delay (perhaps in trigger setting method).
        self.data_buffer = (ctypes.c_int16 * self.n_samples)()
        self.status["setDataBuffer"] = ps.ps5000aSetDataBuffer(self.chandle, self.channel,
                                                               ctypes.byref(self.data_buffer),
                                                               self.n_samples, 0, 0)
        assert_pico_ok(self.status["setDataBuffer"])

    def setMeasTrigger(self):
        self.status["trigger"] = ps.ps5000aSetSimpleTrigger(self.chandle, 1, self.trigger_source,
                                                            self.trigger_threshold, 2, self.delay, 0)
        assert_pico_ok(self.status["trigger"])

    def runMeasurement(self):
        self.status["runBlock"] = ps.ps5000aRunBlock(self.chandle, 0, self.n_samples, self.timebase, None, 0, None,
                                                     None)
        assert_pico_ok(self.status["runBlock"])

        is_ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)

        while is_ready.value == check.value:
            self.status["isReady"] = ps.ps5000aIsReady(self.chandle, ctypes.byref(is_ready))

        overflow = ctypes.c_int16()
        c_samples = ctypes.c_int32(self.n_samples)
        self.status["getValues"] = ps.ps5000aGetValues(self.chandle, 0, ctypes.byref(c_samples), 0, 0, 0,
                                                       ctypes.byref(overflow))
        assert_pico_ok(self.status["getvalues"])

    def setGenerator(self):
        # TODO Mock Implement
        pass
