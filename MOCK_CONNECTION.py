import pytrinamic
from pytrinamic.connections import ConnectionManager
from pytrinamic.modules import TMCM1276
import time
import sys



def check_connection():
    try:
        myInterface.get_status()
        print("Connection is active.")
    except Exception as e:
        print("Connection is not active.")

def change_speed(speed, motor):
    motor.max_velocity = speed

def convert_to_motor_turns(distance_cm, motor):
    pitch_mm = 2.5 # Passo del motore in millimetri
    turns = int(distance_cm * 10 / pitch_mm) # Calcola il numero di rotazioni del motore
    return turns

def move_distance(distance_cm, motor1, motor2):
    turns = convert_to_motor_turns(distance_cm, motor1)
    target_position1 = motor1.actual_position + turns * 360 # Calcola la posizione di destinazione del motore 1 in gradi
    target_position2 = motor2.actual_position + turns * 360 # Calcola la posizione di destinazione del motore 2 in gradi

    # Sposta entrambi i motori alla posizione di destinazione
    motor1.move_to(target_position1)
    motor2.move_to(target_position2)

    # Aspetta che entrambi i motori raggiungano la posizione di destinazione
    while not (motor1.get_position_reached() and motor2.get_position_reached()):
        time.sleep(0.1)  # Piccolo ritardo per evitare loop intensivi
    check_connection()

    print("Preparing parameters")
    motor1.max_acceleration = 5000
    motor2.max_acceleration = 5000

    print("Actual Position (Motor 1) = {}".format(motor1.actual_position))
    print("Actual Position (Motor 2) = {}".format(motor2.actual_position))

    time.sleep(1)

def one_motor_move(distance, motor):
    turns = convert_to_motor_turns(distance, motor)
    target_position=motor.actual_position + turns * 360
    motor.move_to(target_position)
    while not (motor.get_position_reached()):
        time.sleep(0.1)  # Piccolo ritardo per evitare loop intensivi
    check_connection()

    print("Preparing parameters")
    motor1.max_acceleration = 5000
    motor2.max_acceleration = 5000

    print("Actual Position (Motor 1) = {}".format(motor1.actual_position))
    print("Actual Position (Motor 2) = {}".format(motor2.actual_position))

    time.sleep(1)

pytrinamic.show_info()

connectionManager = ConnectionManager("--interface pcan_tmcl")
myInterface = connectionManager.connect()
module1 = TMCM1276(myInterface, module_id=1)
module2 = TMCM1276(myInterface, module_id=4)

motor1 = module1.motors[0]
motor2 = module2.motors[0]
check_connection()
one_motor_move(10, motor2)