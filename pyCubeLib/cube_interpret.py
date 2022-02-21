from pyCubeLib.cube_comm import CubeComm

class CubeInterpret:
    def __init__(self, cube, print_func):
        self.__cube = cube
        self.__print = print_func

    def __print_help(self):
        output_str = "Available commands are:\n"\
                    "status        set_parameter get_parameter relative_pos\n"\
                    "absolute_pos  set_zero      reset_zero    set_coordinate_mode\n"\
                    "move          home          get_gpio      set_gpio\n"\
                    "set_gpio_mode i2c_transfer  spi_transfer\n"
        self.__print(output_str)

    def interpret_command(self, input_string):
        input_string = input_string.strip()
        split = input_string.split(' ', 1)
        cmd = split[0]
        if cmd == "help":
            self.__print_help()
            return False, None, None
        elif cmd == "status":
            return self.__cube.status()
        elif cmd == "relative_pos":
            return self.__cube.relative_pos()
        elif cmd == "absolute_pos":
            return self.__cube.absolute_pos()
        elif cmd == "set_zero":
            return self.__cube.set_zero()
        elif cmd == "reset_zero":
            return self.__cube.reset_zero()
        elif cmd == "home":
            return self.__cube.home()
        elif cmd == "get_parameter":
            data = split[1]
            if len(data) == 0:
                return True, "too few args", None
            return self.__cube.get_parameter(int(data.strip()))

        elif cmd == "set_parameter":
            data = split[1]
            data = data.split()
            if (len(data) != 2):
                return True, "too few args", None
            return self.__cube.set_parameter(int(data[0]), int(data[1]))

        elif cmd == "set_coordinate_mode":
            data = split[1]
            data = data.strip()
            if (data == "cartesian"):
                return self.__cube.set_coordinate_mode(0)
            elif (data == "cylindrical"):
                return self.__cube.set_coordinate_mode(1)
            elif (data == "spherical"):
                return self.__cube.set_coordinate_mode(2)
            return True, "unknown mode", None

        elif cmd == "move":
            data = split[1]
            data = data.split()
            if (len(data) != 3):
                return True, "too few args", None
            return self.__cube.move_to(float(data[0]), float(data[1]), float(data[2]))

        elif cmd == "get_gpio":
            data = split[1]
            if len(data) == 0:
                return True, "too few args", None
            return self.__cube.get_gpio(int(data))

        elif cmd == "set_gpio":
            data = split[1]
            data = data.split()
            if len(data) != 2:
                return True, "too few args", None
            return self.__cube.set_gpio(int(data[0]), bool(data[1]))

        elif cmd == "set_gpio_mode":
            data = split[1]
            data = data.split()
            if len(data) != 2:
                return True, "too few args", None
            return self.__cube.set_gpio_mode(int(data[0]), bool(data[1]))

        elif cmd == "i2c_transfer":
            data = split[1]
            data = data.split()
            if len(data) != 4:
                return True, "too few args", None
            rx_len = int(data[0])
            tx_len = int(data[1])
            addr = bytearray.fromhex(data[2])[0]
            byte_data = list(bytearray.fromhex(data[3]))
            return self.__cube.i2c_transfer(rx_len, tx_len, addr, byte_data)

        elif cmd == "spi_transfer":
            data = split[1]
            data = data.split()
            if len(data) != 4:
                return True, "too few args", None
            cs = int(data[0])
            mode = int(data[1])
            length = int(data[2])
            byte_data = list(bytearray.fromhex(data[3]))
            return self.__cube.spi_transfer(cs, mode, length, byte_data)


        return True, "unknown command", None