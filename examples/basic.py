from xyztank.model import *
import numpy as np

tank = Tank(
    name="small_aquarium",
    dimensions=(
        200e-3,  # OX [m]
        100e-3,  # OY [m]
        200e-3   # OZ [m]
    )
)

plan = MeasurementPlan(
    name="Example",
    tank=tank,
    grid=(
        np.arange(-50e-3, 50e-3, 1e-3),  # OX [m]
        np.arange(-20e-3, 20e-3, 1e-3),  # OY [m]
        np.arange(-50e-3, 50e-3, 1e-3),  # OZ [m]
    )
)