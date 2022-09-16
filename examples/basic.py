from xyztank.model import *
import numpy as np

tank = Tank(
    name="small_aquarium",
    dimensions=(
        200e-3,  # OX [m]
        100e-3,  # OY [m]
        200e-3   # OZ [m]
    ),
    position=(10e-3, 7e-3, -200e-3)  # xyz
)

plan = MeasurementPlan(
    name="Example",
    tank=tank,
    min_position=(20e-3, 10e-3, -120e-3),  # xyz
    max_position=(120e-3, 50e-3, -20e-3),  # xyz
    grid_precision=(1e-3, 1e-3, 1e-3),
    grid=None

)
