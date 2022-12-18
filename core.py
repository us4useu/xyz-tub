import ctypes
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
from math import log2
from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import assert_pico_ok, mV2adc, adc2mV
from picosdk.errors import PicoSDKCtypesError, PicoError
from config import oscilloscope_settings as os
from logging_ import get_logger
from dict import channel, resolution

# TODO Consider using some @exception_handler decorator to handle exceptions.


class Oscilloscope:
    """A class responsible for managing the oscilloscope."""

    def __init__(self):
        # This attribute is assigned a value later.
        self.log = get_logger(type(self).__name__)
        self.chandle = ctypes.c_int16()
        self.status = dict()
        self.maxADC = ctypes.c_int16()

        self.open_connection()
        self.disable_channel(['all'])
        self.find_max_adc_val()

    def find_max_adc_val(self):
        self.status["maximumValue"] = ps.ps5000aMaximumValue(self.chandle, ctypes.byref(self.maxADC))
        assert_pico_ok(self.status["maximumValue"])

    def open_connection(self):
        self.status["openunit"] = ps.ps5000aOpenUnit(ctypes.byref(self.chandle), None, os.resolution)
        try:
            assert_pico_ok(self.status["openunit"])
        except PicoSDKCtypesError:
            powerstatus = self.status["openunit"]
            # TODO Check for other possible power supply errors
            # PICO_USB3_0_DEVICE_NON_USB3_0_PORT
            # Should the user be able to choose the power source?
            if powerstatus == 286:
                self.log.debug("Device connected to USB 2.0 port, oscilloscope expects USB 3.0.")
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(self.chandle, powerstatus)
            # PICO_POWER_SUPPLY_NOT_CONNECTED
            elif powerstatus == 282:
                self.log.warning("Power supply unit not connected." +
                                 " Only A and B channels and no generator will be available.")
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(self.chandle, powerstatus)
            elif powerstatus == 3:
                self.log.exception("Oscilloscope is not connected!")
                raise
            else:
                self.log.exception("Encountered unexpected picosdk exception.")
                raise
            try:
                assert_pico_ok(self.status["changePowerSource"])
            except PicoError:
                self.log.exception("Error changing power source (or related settings).")
                raise
            else:
                self.log.info("Connection with the oscilloscope established.")
        else:
            self.log.info("Connection with the oscilloscope established.")

    def set_channel(self):
        self.status["setChannel"] = ps.ps5000aSetChannel(self.chandle, os.channel, 1, os.coupling_type,
                                                         os.range, 0)
        try:
            assert_pico_ok(self.status["setChannel"])
        except PicoError:
            self.log.exception(f"Erorr setting channel:")
            raise
        else:
            self.log.info("Oscilloscope channel set with config parameters.")

        self.n_samples = int(1000 * os.measurement_time * os.sampling_frequency)
        self.verify_timeinterval = ctypes.c_float()  # ns
        self.verify_n_samples = ctypes.c_int32()
        self.status["getTimebase2"] = ps.ps5000aGetTimebase2(self.chandle, self.find_timebase(os.sampling_frequency),
                                                             self.n_samples, ctypes.byref(self.verify_timeinterval),
                                                             ctypes.byref(self.verify_n_samples), 0)
        self.log.info(f"Desired sampling frequency: {os.sampling_frequency} Msa/s")
        self.log.info(f"Verified sampling frequency: {1 / (self.verify_timeinterval.value / 1000)} MSa/s")
        # Test
        # print(f"Verified frequency: {1 / (self.verify_timeinterval.value / 1000)} MHz")
        # print(f"Desired frequency: {os.sampling_frequency} MHz")
        # print(f"Verified samples: {self.verify_n_samples.value}")  # What's that value exactly?

        # Do we want our data_buffer to be global? Maybe just put it in runMeasurement method?
        # Buffer has to be much longer than the expected received signal!
        self.data_buffer = (ctypes.c_int16 * self.n_samples)()
        self.status["setDataBuffer"] = ps.ps5000aSetDataBuffer(self.chandle, os.channel,
                                                               ctypes.byref(self.data_buffer),
                                                               self.n_samples, 0, 0)
        try:
            assert_pico_ok(self.status["setDataBuffer"])
        except PicoError:
            self.log.exception(f"Error setting data buffer:")
        else:
            self.log.info("Data buffer is set.")

    def set_meas_trigger(self):
        self.status["trigger"] = ps.ps5000aSetSimpleTrigger(self.chandle, 1, os.trigger_source,
                                                            int(mV2adc(os.trigger_threshold, os.range, self.maxADC)), 2,
                                                            int(os.delay / (self.verify_timeinterval.value / 1000000)),
                                                            0)
        try:
            assert_pico_ok(self.status["trigger"])
        except PicoError:
            self.log.exception("Error setting mearument trigger.")
            raise
        else:
            self.log.info("Mesurement trigger set with config parameters.")

    def run_measurement(self):
        self.status["runBlock"] = ps.ps5000aRunBlock(self.chandle, 0, self.n_samples,
                                                     self.find_timebase(os.sampling_frequency), None, 0, None,
                                                     None)
        try:
            assert_pico_ok(self.status["runBlock"])
        except PicoError:
            self.log.exception("Error starting measurment.")
            raise
        else:
            self.log.info("Measurement started. Oscilloscope is waiting for trigger.")

    # Instead of executing this function one might consider modifying it and using as a callback function,
    # which is executed when the data is ready. Morea in ps5000aBlockCallbackExample.py
    def get_data(self):
        is_ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)

        while is_ready.value == check.value:
            self.status["isReady"] = ps.ps5000aIsReady(self.chandle, ctypes.byref(is_ready))

        self.log.info("Measurement data ready to be acquired.")
        overflow = ctypes.c_int16()
        c_samples = ctypes.c_int32(self.n_samples)
        self.status["getValues"] = ps.ps5000aGetValues(self.chandle, 0, ctypes.byref(c_samples), 0, 0, 0,
                                                       ctypes.byref(overflow))
        try:
            assert_pico_ok(self.status["getValues"])
        except PicoError:
            self.log.exception("Exception acquiring data to the computer.")
        else:
            self.log.info("Measurement data acquired to the computer.")

    def plot_data(self):
        samples = adc2mV(self.data_buffer, os.range, self.maxADC)
        time = np.linspace(0, (self.n_samples - 1) * 1 / (os.sampling_frequency / 1000), self.n_samples)
        plt.plot(time, samples[:])
        plt.xlabel('Time [ns]')
        plt.ylabel('Voltage [mV]')
        plt.show()

        # Test:
        # print(f"Desired samples: {self.n_samples} ")
        # print(f"Output Samples: {len(samples)}")
        # print(f"Desired measurement time: {os.measurement_time} ms")
        # print(f"Desired impulse length: {os.impulse_length} ms")

    # Generator methods seem to work.
    # However, after starting and stopping the generator (only setting is fine),
    # there is still some constant noisy voltage left on generator output,
    # lower than the generated one. I have no idea where it's from, for now,
    # I'd reccommend setting adequate trigger threshold values, close to triggering
    # signal's peak.

    # UPDATE: Try just setting signal's amplitude to 0.
    def set_generator(self):
        # enums describing generator's settings missing in picosdk. Need to use numerical values.
        # ctypes.c_uint32(-1) - PS5000A_SHOT_SWEEP_TRIGGER_CONTINUOUS_RUN - not available as enum.
        self.status["setGenerator"] = ps.ps5000aSetSigGenBuiltInV2(self.chandle, os.offset_voltage, os.Vpp,
                                                                   ctypes.c_int32(os.wave_type),
                                                                   os.signal_frequency * 1000,
                                                                   os.signal_frequency * 1000,
                                                                   0, 1, ctypes.c_int32(0), 0,
                                                                   ctypes.c_uint32(-1), 0,
                                                                   ctypes.c_int32(2), ctypes.c_int32(4), 0)
        try:
            assert_pico_ok(self.status["setGenerator"])
        except PicoError:
            self.log.exception("Error setting the generator.")
            raise
        else:
            self.log.info("Generator set with config parameters.")

    def start_generator(self):
        self.status["startGenerator"] = ps.ps5000aSigGenSoftwareControl(self.chandle, 1)
        try:
            assert_pico_ok(self.status["startGenerator"])
        except PicoError:
            self.log.exception("Error starting the generator")
            raise
        else:
            self.log.info("Generator started.")

    def stop_generator(self):
        self.status["stopGenerator"] = ps.ps5000aSigGenSoftwareControl(self.chandle, 0)
        try:
            assert_pico_ok(self.status["stopGenerator"])
        except PicoError:
            self.log.exception("Error stopping the generator")
            raise
        else:
            self.log.info("Generator stopped.")

    def generate_impulse(self):
        self.start_generator()
        sleep(os.impulse_length / 1000)
        self.stop_generator()

    # Based on picoscope5000a programming guide.
    # noinspection PyMethodMayBeStatic
    def _return_timebase_formula(self, res: int):

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

        formulas = {resolution["8BIT"]: _8bitFormula,
                    resolution["12BIT"]: _12bitFormula,
                    resolution["14BIT"]: _14bitFormula
                    }

        # formulas = {resolution["8BIT"]: lambda sf: 3 if sf == 125.0 else 125/sf+2,
        #             resolution["12BIT"]: lambda sf: log2(500/sf)+1 if sf in [125, 250, 500] else 62.5/sf+3,
        #             resolution["14BIT"]: lambda sf: log2(1000/sf) if sf in [250, 500, 1000] else 125/sf+2
        #             }

        return formulas[res]

    # Returns integer timebase parameter that will allow to set desired sampling frequency
    # on the oscilloscope.
    def find_timebase(self, sampling_frequency: float) -> int:
        formula = self._return_timebase_formula(os.resolution)
        return int(formula(sampling_frequency))

    def disable_channel(self, channels: list[str]):
        if channels[0] == 'all':
            channels = ['A', 'B', 'C', 'D']
        for ch in channels:
            try:
                self.status["setChannel"] = ps.ps5000aSetChannel(self.chandle,
                                                                 channel[ch],
                                                                 0, os.coupling_type, os.range, 0)
                assert_pico_ok(self.status["setChannel"])
            except PicoError:
                self.log.exception(f"Exception disabling oscilloscope channel {ch}.")
                raise
            else:
                self.log.info(f"Disabled channel {ch}.")
