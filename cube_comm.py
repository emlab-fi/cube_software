from dataclasses import dataclass
import serial
import cube_pb2


@dataclass
class Reply:
    id: int
    error: int
    mode: int
    position: tuple(int, int, int)
    playload: any = None


class CubeComm:
    def __init__(self, id_start):
        self.__port = None
        self.__id = id_start
    
    def __get_id(self):
        self.__id += 1
        return self.__id

    def __send_data(self, msg_type, data):
        msg_out = [0x55, 0x55, 0x55, msg_type, len(data)]
        msg_out.extend(data)
        self.__port.write(msg_out)

    def __receive_data(self):
        receive = []
        while (len(receive) == 0):
            receive = self.__port.read(300)
        return receive

    def __read_packet(self, data):
        found = []
        header_found = 0
        data_length = 0
        reading_data = False
        for i in range(len(data)):
            if not reading_data:
                if header_found == 3:
                    data_length = data[i]
                    reading_data = True
                    continue
                if data[i] != 0x55:
                    header_found = 0
                    continue
                if data[i] == 0x55:
                    header_found += 1
                    continue
            if reading_data:
                if data_length == 0:
                    return (found, True)
                found.append(data[i])
                data_length -= 1
        if (data_length == 0):
            return (found, True)
        return (found, False)

    
    def __decode_receive(self, received):
        data, found_end = self.__readPacket(received)
        if not found_end:
            return (True, "Data read error", [])
        msg = protocols_pb2.Return_msg().FromString(bytearray(data))
        has_error, error = self.__decodeStatus(msg, command)
        data_out = [None, None]
        if msg.HasField('position'):
            data_out[0] = (msg.position.x, msg.position.y, msg.position.z)
        if msg.HasField('measurement'):
            data_out[1] = (msg.measurement.x, msg.measurement.y, msg.measurement.z)
        return (has_error, error, tuple(data_out))

    
    def __send_simple_command(self, command):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.command = command

        data = msg.SerializeToString()
        self.__send_data(data)

        data_in = self.__receive_data()
        return self.__decode_receive(data_in)

    def __send_msg(self, msg):
        data = msg.SerializeToString()
        self.__send_data(data)
        data_in = self.__receive_data()
        return self.__decode_receive(data_in)
    
    def set_serial_port(self, port):
        self.__port = port

    def status(self):
        return self.__send_simple_command(cube_pb2.status_i)

    def absolute_pos(self):
        return self.__send_simple_command(cube_pb2.get_abs_pos)
    
    def relative_pos(self):
        return self.__send_simple_command(cube_pb2.get_rel_pos)
    
    def set_zero(self):
        return self.__send_simple_command(cube_pb2.set_zero_pos)
    
    def reset_zero(self):
        return self.__send_simple_command(cube_pb2.reset_zero_pos)

    def home(self):
        return self.__send_simple_command(cube_pb2.home)

    def move_to(self, a, b, c):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.command = cube_pb2.move_to
        msg.pos.a = a
        msg.pos.b = b
        msg.pos.c = c
        return self.__send_msg(msg)
        
    
    def set_coordinate_mode(self, mode):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.command = cube_pb2.set_coordinate_mode
        if (mode == 0):
            msg.mode = cube_pb2.cartesian
        if (mode == 1):
            msg.mode = cube_pb2.cylindrical
        if (mode == 3):
            msg.mode = cube_pb2.spherical
        return self.__send_msg(msg)
    
    def spi_transfer(self, cs, mode, length, data):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.command = cube_pb2.spi_transfer
        msg.spi.cs = cs
        msg.spi.length = length
        msg.spi.data = data
        return self.__send_msg(msg)
    
    def i2c_transfer(self, rx_len, tx_len, addr, data):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.command = cube_pb2.i2c_transfer
        msg.i2c.rx_length = rx_len
        msg.i2c.tx_length = tx_len
        msg.i2c.address = addr
        msg.i2c.data = data
        return self.__send_msg(msg)
    
    def set_gpio_mode(self, index, mode):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.command = cube_pb2.set_gpio_mode
        msg.gpio.index = index
        msg.gpio.value = mode
        return self.__send_msg(msg)
    
    def set_gpio(self, index, value):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.command = cube_pb2.set_gpio
        msg.gpio.index = index
        msg.gpio.value = value
        return self.__send_msg(msg)
    
    def get_gpio(self, index):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.command = cube_pb2.get_gpio
        msg.gpio.index = index
        msg.gpio.value = False
        return self.__send_msg(msg)
    
    def set_parameter(self, id, value):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.command = cube_pb2.set_parameter
        msg.param.id = id
        msg.param.value = value
        return self.__send_msg(msg)
    
    def get_parameter(self, id):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.command = cube_pb2.get_parameter
        msg.param.id = id
        msg.param.value = 0
        return self.__send_msg(msg)