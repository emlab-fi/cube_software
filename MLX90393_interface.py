from pyCubeLib import CubeGUI
from time import sleep


def measure_func(cube):
    """
    Simple measure func for MLX90393.
    """
    error, reply = cube.i2c_transfer(1, 1, 0x0C, [0x3F])
    if error:
        return error, (0, 0, 0)
    sleep(0.5)
    error, reply = cube.i2c_transfer(9, 1, 0x0C, [0x4F])
    if error:
        return error, (0, 0, 0)

    payload_data = reply.get_payload()[1]
    x = (payload_data[3] << 8) + payload_data[4]
    y = (payload_data[5] << 8) + payload_data[6]
    z = (payload_data[7] << 8) + payload_data[8]

    x_ut = (x - 2**15) * 0.3
    y_ut = (y - 2**15) * 0.3
    z_ut = (z - 2**15) * 0.484

    return None, (x_ut, y_ut, z_ut)


def init_func(cube):
    """
    Init MLX90393 to some sensible config
    """
    error, reply = cube.i2c_transfer(3, 2, 0x0C, [0x50, 0x00])
    if error:
        print(error)
        return False
    first_reg = reply.get_payload()[1]
    if (first_reg[0] & 0x10):
        print("sensor error")
        return False

    manufacturer_data = first_reg[1]

    registers = [
        #gain 7, hallconf 0xC
        [0x60, manufacturer_data, 0x7C, 0x00],
        #tcmp_en 1, forced i2c mode
        [0x60, 0x64, 0x0F, 0x04],
        #osr 1, dig_filt 7, res 1
        [0x60, 0x02, 0xBE, 0x08]
    ]

    for register in registers:
        error, reply = cube.i2c_transfer(1, 4, 0x0C, register)
        if error:
            print(error)
            return False
        status = reply.get_payload()[1]
        if (status & 0x10):
            print("sensor error")
            return False

    return True

#run the GUI
gui = CubeGUI(measure_func, init_func)
gui.run_app()
