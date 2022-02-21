from pyCubeLib import CubeGUI
from time import sleep


def measure_func(cube):
    """
    Simple measure func for MLX90393.
    Does no recalculation to uT.
    """
    has_error, error, reply = cube.i2c_transfer(1, 1, 0x0C, [0x3F])
    if (has_error):
        return True, error, (0, 0, 0)
    sleep(0.5)
    has_error, error, reply = cube.i2c_transfer(9, 1, 0x0C, [0x4F])
    if (has_error):
        return True, error, (0, 0, 0)

    payload_data = reply.get_payload()[1]
    x = (payload_data[3] << 8) + payload_data[4]
    y = (payload_data[5] << 8) + payload_data[6]
    z = (payload_data[7] << 8) + payload_data[8]

    return False, None, (x, y, z)


def init_func(cube):
    """
    Empty init.
    """
    return True

#run the GUI
gui = CubeGUI(measure_func, init_func)
gui.run_app()