import ctypes
from math import log2
from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import assert_pico_ok, mV2adc, adc2mV
from picosdk.errors import PicoSDKCtypesError
from config import oscilloscope_settings as os


# TODO Exceptions
# TODO Logging


class Oscilloscope:
    """A class responsible for managing the oscilloscope."""

    def __init__(self):
        # This attribute is assigned a value later.
        self.chandle = ctypes.c_int16()
        self.status = dict()

        # Open the oscilloscope
        # TODO Move it to another method that throws an exception so that you can rerun it.
        self.status["openunit"] = ps.ps5000aOpenUnit(ctypes.byref(self.chandle), None, os.resolution)
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
        assert_pico_ok(self.status["maximumValue"])

    def setChannel(self):
        self.status["setChannel"] = ps.ps5000aSetChannel(self.chandle, os.channel, 1, os.coupling_type,
                                                         os.range, 0)
        assert_pico_ok(self.status["setChannel"])

        self.timeinterval = ctypes.c_float()
        self.status["getTimebase2"] = ps.ps5000aGetTimebase2(self.chandle, os.timebase, os.n_samples,
                                                             ctypes.byref(self.timeinterval), None, 0)

        # Do we want our data_buffer to be global? Maybe just put it in runMeasurement method?
        # Buffer has to be much longer than the expected received signal!
        self.data_buffer = (ctypes.c_int16 * os.n_samples)()
        self.status["setDataBuffer"] = ps.ps5000aSetDataBuffer(self.chandle, os.channel,
                                                               ctypes.byref(self.data_buffer),
                                                               os.n_samples, 0, 0)
        assert_pico_ok(self.status["setDataBuffer"])

    def setMeasTrigger(self):
        self.status["trigger"] = ps.ps5000aSetSimpleTrigger(self.chandle, 1, os.trigger_source,
                                                            int(mV2adc(os.trigger_threshold, os.range, self.maxADC)), 2,
                                                            os.delay, 0)
        assert_pico_ok(self.status["trigger"])

    def runMeasurement(self):
        self.status["runBlock"] = ps.ps5000aRunBlock(self.chandle, 0, os.n_samples, os.timebase, None, 0, None,
                                                     None)
        assert_pico_ok(self.status["runBlock"])

        is_ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)

        while is_ready.value == check.value:
            self.status["isReady"] = ps.ps5000aIsReady(self.chandle, ctypes.byref(is_ready))

        overflow = ctypes.c_int16()
        c_samples = ctypes.c_int32(os.n_samples)
        self.status["getValues"] = ps.ps5000aGetValues(self.chandle, 0, ctypes.byref(c_samples), 0, 0, 0,
                                                       ctypes.byref(overflow))
        assert_pico_ok(self.status["getValues"])

    def setGenerator(self):
        # TODO Mock Implement
        pass

        # Sampling frequency in MHz

    # Based on picoscope5000a programming guide.
    # noinspection PyMethodMayBeStatic
    def _returnTimeBaseFormula(self, resolution: int):

        def _14bitFormula(sampling_frequency: float):
            if sampling_frequency == 125.0:
                return 3
            else:
                return 125 / sampling_frequency + 2

        def _12bitFormula(sampling_frequency: float):
            if sampling_frequency in [125, 250, 500]:
                return log2(500 / sampling_frequency) + 1
            else:
                return 62.5 / sampling_frequency + 3

        def _8bitFormula(sampling_frequency: float):
            if sampling_frequency in [250, 500, 1000]:
                return log2(1000 / sampling_frequency)
            else:
                return 125 / sampling_frequency + 2

        formulas = {ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_8BIT"]: _8bitFormula,
                    ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"]: _12bitFormula,
                    ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_14BIT"]: _14bitFormula
                    }

        return formulas[resolution]

    # Returns integer timebase parameter that will allow to set desired sampling frequency
    # on the oscilloscope.
    def findTimebase(self, sampling_frequency: float) -> int:
        formula = self._returnTimeBaseFormula(os.resolution)
        return int(formula(sampling_frequency))
