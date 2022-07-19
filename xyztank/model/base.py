import logging
import time
import importlib
import sys
import math
import threading
import numpy as np
from enum import Enum
from dataclasses import dataclass
import pickle
from typing import Tuple

from xyztank.model import *
from xyztank.logging import get_logger


@dataclass(frozen=True)
class Tank:
    name: str
    dimensions: Tuple[float, float, float]


@dataclass(frozen=True)
class MeasurementPlan:
    name: str
    tank: Tank
    grid: Tuple[np.ndarray, np.ndarray, np.ndarray]


class XyzSystemState(Enum):
    STOPPED = 0
    RUNNING = 1


@dataclass(frozen=True)
class MeasurementProgress:
    data: np.ndarray
    percent: int


@dataclass(frozen=True)
class MeasurementResult:
     plan: MeasurementPlan
     date: int
     data: np.ndarray


class XyzSystem:

    def __init__(self):
        self.log = get_logger(type(self).__name__)
        self.measurement_plan = None  # Current measurement plan
        self.measurement_progress = None
        self.measurement_thread = None
        self.state = XyzSystemState.STOPPED

    def run_settings(self, settings_path: str):
        """
        Load settings from the path, configure the system and run measurement.

        :param settings_path: path to the settings file
        """
        settings = self._load_settings(settings_path)
        self.run_measurement(settings.plan)

    def run_measurement(self, plan: MeasurementPlan):
        """
        Configure the system and run measurement.

        :param plan: measurement plan to run
        """
        self.configure_measurement(plan)
        return self.start_measurement()

    def configure_measurement(self, plan: MeasurementPlan):
        """
        Configure measurement plan for this system.

        :param plan: measurement plan to configure
        """
        self.log.info(f"Configuring measurement")
        if self.state == XyzSystemState.RUNNING:
            raise ValueError("The system is busy.")
        self.measurement_plan = plan

    def start_measurement(self):
        """
        Start the currently configured measurement.
        """
        self.log.info(f"Starting measurement")
        self._set_to_running()
        self.measurement_thread = threading.Thread(target=self._acquire_data)
        self.measurement_thread.start()

    def stop_measurement(self):
        """
        Stop measurement currently in progress.
        """
        self.log.info(f"Stopping the current measurement")
        self._set_state_to_stopped()

    def save_measurement(self, path):
        """
        Saves the last measurement to given output file.

        :param path: path to the output file
        """
        progress = self.measurement_progress
        if progress is None:
            self.log.error("So far no measurement has been performed, "
                           "run some measurement plan first.")
        elif progress.percent != 100:
            self.log.warn("Note: attempting to save partially acquired data,"
                          f"current progress: {progress.percent}")
        plan = self.measurement_plan
        result = MeasurementResult(
            plan=plan,
            date=time.time_ns() // 1000,
            data=progress.data
        )
        pickle.dump(result, open(path, "wb"))
        self.log.info(f"Saved measurement to {path}")

    def get_progress(self) -> MeasurementProgress:
        """
        Returns current progress in executing the measurement plan.
        """
        return self.measurement_progress

    def exit(self):
        """
        Stop any measurement that is currently running in the system
        then close the system.
        """
        if self.state == XyzSystemState.RUNNING:
            self.stop_measurement()
        self.log.info("Closed the handle to the system.")

    def _acquire_data(self):
        grid_x, grid_y, grid_z = self.measurement_plan.grid
        # the last axis == 2: pressure +/- values
        result_shape = (len(grid_x), len(grid_y), len(grid_z), 2)
        result = np.zeros(result_shape, dtype=np.float32)
        result = result.flatten()
        n_values = len(result.flatten())
        part_size = int(math.ceil(n_values/100))

        for i in range(100):
            if self.state == XyzSystemState.STOPPED:
                # Someone stopped the measurement, exit.
                return
            result[i*part_size:(i+1)*part_size] = i
            self.measurement_progress = MeasurementProgress(
                data=result.reshape(result_shape), percent=i)
            if i % 10 == 0:
                self.log.info(f"Measurement in progress: "
                              f"{self.measurement_progress.percent} %")
            time.sleep(0.1)
        self._set_state_to_stopped()
        self.measurement_progress = MeasurementProgress(
            data=result.reshape(result_shape), percent=100)
        self.log.info("Measurement finished.")

    def _set_to_running(self):
        if self.state == XyzSystemState.RUNNING:
            raise ValueError("The system is already busy.")
        self.state = XyzSystemState.RUNNING

    def _set_state_to_stopped(self):
        if self.state != XyzSystemState.RUNNING:
            self.log.warn("There is no measurement currently running.")
        self.state = XyzSystemState.STOPPED

    def _load_settings(self, path: str):
        module_name = "xyztank_settings"
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module


