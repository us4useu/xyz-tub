import ctypes
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
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
        self.maxADC = ctypes.c_int16()

        self.openConnection()
        self.disableAllChannels()
        self.findMaxADCVal()

    def findMaxADCVal(self):
        self.status["maximumValue"] = ps.ps5000aMaximumValue(self.chandle, ctypes.byref(self.maxADC))
        assert_pico_ok(self.status["maximumValue"])

    def openConnection(self):
        self.status["openunit"] = ps.ps5000aOpenUnit(ctypes.byref(self.chandle), None, os.resolution)
        try:
            assert_pico_ok(self.status["openunit"])
        except PicoSDKCtypesError:
            powerstatus = self.status["openunit"]
            # TODO Check for other possible power supply errors
            # PICO_USB3_0_DEVICE_NON_USB3_0_PORT
            # Should the user be able to choose the power source?
            if powerstatus == 286:
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(self.chandle, powerstatus)
            # PICO_POWER_SUPPLY_NOT_CONNECTED
            elif powerstatus == 282:
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(self.chandle, powerstatus)
            else:
                raise

            assert_pico_ok(self.status["changePowerSource"])

    def setChannel(self):
        self.status["setChannel"] = ps.ps5000aSetChannel(self.chandle, os.channel, 1, os.coupling_type,
                                                         os.range, 0)
        assert_pico_ok(self.status["setChannel"])

        self.verify_timeinterval = ctypes.c_float()  # ns
        self.verify_n_samples = ctypes.c_int32()
        self.status["getTimebase2"] = ps.ps5000aGetTimebase2(self.chandle, self.findTimebase(os.sampling_frequency),
                                                             os.n_samples, ctypes.byref(self.verify_timeinterval),
                                                             ctypes.byref(self.verify_n_samples), 0)
        # Test
        # print(f"Verified frequency: {1 / (self.verify_timeinterval.value / 1000)} MHz")
        # print(f"Desired frequency: {os.sampling_frequency} MHz")
        # print(f"Verified samples: {self.verify_n_samples.value}")  # What's that value exactly?
        # print(f"Desired samples: {os.n_samples} ")

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
                                                            int(os.delay / (self.verify_timeinterval.value / 1000000)),
                                                            0)
        assert_pico_ok(self.status["trigger"])

    def runMeasurement(self):
        self.status["runBlock"] = ps.ps5000aRunBlock(self.chandle, 0, os.n_samples,
                                                     self.findTimebase(os.sampling_frequency), None, 0, None,
                                                     None)
        assert_pico_ok(self.status["runBlock"])

    # Instead of executing this function one might consider modifying it and using as a callback function,
    # which is executed when the data is ready. Morea in ps5000aBlockCallbackExample.py
    def getData(self):
        is_ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)

        while is_ready.value == check.value:
            self.status["isReady"] = ps.ps5000aIsReady(self.chandle, ctypes.byref(is_ready))

        overflow = ctypes.c_int16()
        c_samples = ctypes.c_int32(os.n_samples)
        self.status["getValues"] = ps.ps5000aGetValues(self.chandle, 0, ctypes.byref(c_samples), 0, 0, 0,
                                                       ctypes.byref(overflow))
        assert_pico_ok(self.status["getValues"])

    def plotData(self):
        samples = adc2mV(self.data_buffer, os.range, self.maxADC)
        time = np.linspace(0, (os.n_samples - 1) * 1 / (os.sampling_frequency / 1000), os.n_samples)
        plt.plot(time, samples[:])
        plt.xlabel('Time [ns]')
        plt.ylabel('Voltage [mV]')
        plt.show()

        # Test
        # print(f"Output Samples: {len(samples)}")

    # Generator methods seem to work.
    # However, after starting and stopping the generator (only setting is fine),
    # there is still some constant noisy voltage left on generator output,
    # lower than the generated one. I have no idea where it's from, for now,
    # I'd reccommend setting adequate trigger threshold values, close to triggering
    # signal's peak.

    # UPDATE: Try just setting signal's amplitude to 0.
    def setGenerator(self):
        # enums describing generator's settings missing in picosdk. Need to use numerical values.
        # ctypes.c_uint32(-1) - PS5000A_SHOT_SWEEP_TRIGGER_CONTINUOUS_RUN - not available as enum.
        self.status["setGenerator"] = ps.ps5000aSetSigGenBuiltInV2(self.chandle, os.offset_voltage, os.Vpp, ctypes.c_int32(os.wave_type), os.signal_frequency * 1000, os.signal_frequency * 1000, 0, 1, ctypes.c_int32(0), 0, ctypes.c_uint32(-1), 0, ctypes.c_int32(2), ctypes.c_int32(4), 0)
        assert_pico_ok(self.status["setGenerator"])

    def startGenerator(self):
        self.status["startGenerator"] = ps.ps5000aSigGenSoftwareControl(self.chandle, 1)
        assert_pico_ok(self.status["startGenerator"])

    def stopGenerator(self):
        self.status["stopGenerator"] = ps.ps5000aSigGenSoftwareControl(self.chandle, 0)
        assert_pico_ok(self.status["stopGenerator"])

    def generateImpulse(self):
        self.startGenerator()
        sleep(os.impulse_length)
        self.stopGenerator()

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

    def disableAllChannels(self):
        self.status["setChannel"] = ps.ps5000aSetChannel(self.chandle, ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"], 0,
                                                         os.coupling_type,
                                                         os.range, 0)
        assert_pico_ok(self.status["setChannel"])
        self.status["setChannel"] = ps.ps5000aSetChannel(self.chandle, ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"], 0,
                                                         os.coupling_type,
                                                         os.range, 0)
        assert_pico_ok(self.status["setChannel"])
        self.status["setChannel"] = ps.ps5000aSetChannel(self.chandle, ps.PS5000A_CHANNEL["PS5000A_CHANNEL_C"], 0,
                                                         os.coupling_type,
                                                         os.range, 0)
        assert_pico_ok(self.status["setChannel"])
        self.status["setChannel"] = ps.ps5000aSetChannel(self.chandle, ps.PS5000A_CHANNEL["PS5000A_CHANNEL_D"], 0,
                                                         os.coupling_type,
                                                         os.range, 0)
        assert_pico_ok(self.status["setChannel"])
