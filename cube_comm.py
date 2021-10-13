from dataclasses import dataclass
import serial
import cube_pb2


@dataclass
class Reply:
    id: int
    error: int
    mode: int
    position: tuple
    payload: any = None


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
        packet = []
        header_found = 0
        packet_length = 0
        reading_data = False
        reading_data_length = False
        for i in range(len(data)):
            if not (reading_data or reading_data_length):
                if header_found == 3:
                    msg_type = data[i]
                    reading_data_length = True
                    if (msg_type != 0x02):
                        return (True, "cube_comm: wrong reply", None)
                    continue
                if data[i] != 0x55:
                    header_found = 0
                    continue
                if data[i] == 0x55:
                    header_found += 1
                    continue
            if reading_data_length:
                packet_length = data[i]
                reading_data = True
                reading_data_length = False
                continue
            if reading_data:
                if packet_length == 0:
                    return (True, "cube_comm: no data", None)
                packet.append(data[i])
                packet_length -= 1
        if (packet_length == 0 and not len(packet) == 0):
            return (False, None, packet)
        return (True, "cube_comm: lost data", None)

    
    def __decode_receive(self, received):
        has_error, error, packet = self.__read_packet(received)
        if has_error:
            return (True, error, None)
        msg = cube_pb2.reply_msg().FromString(bytearray(packet))
        payload = None
        position = (msg.stat.pos.a, msg.stat.pos.b, msg.stat.pos.c)
        if msg.HasField('data'):
            payload = (msg.data.length, msg.data.data)
        elif msg.HasField('gpio_status'):
            payload = gpio_status
        elif msg.HasField('param_value'):
            payload = msg.param_value
        reply = Reply(msg.id, msg.stat.error, msg.stat.mode, position, payload)
        return (has_error, error, reply)

    
    def __send_simple_command(self, command):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.inst = command

        data = msg.SerializeToString()
        self.__send_data(0x01, data)

        data_in = self.__receive_data()
        return self.__decode_receive(data_in)

    def __send_msg(self, msg):
        data = msg.SerializeToString()
        self.__send_data(0x01, data)
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
        msg.inst = cube_pb2.move_to
        msg.pos.a = a
        msg.pos.b = b
        msg.pos.c = c
        return self.__send_msg(msg)
        
    
    def set_coordinate_mode(self, mode):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.inst = cube_pb2.set_coordinate_mode
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
        msg.inst = cube_pb2.spi_transfer
        msg.spi.cs = cs
        msg.spi.length = length
        msg.spi.data = bytes(data + ([0] * (64 - length)))
        return self.__send_msg(msg)
    
    def i2c_transfer(self, rx_len, tx_len, addr, data):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.inst = cube_pb2.i2c_transfer
        msg.i2c.rx_length = rx_len
        msg.i2c.tx_length = tx_len
        msg.i2c.address = addr
        msg.i2c.data = bytes(data + ([0] * (64 - rx_len)))
        return self.__send_msg(msg)
    
    def set_gpio_mode(self, index, mode):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.inst = cube_pb2.set_gpio_mode
        msg.gpio.index = index
        msg.gpio.value = mode
        return self.__send_msg(msg)
    
    def set_gpio(self, index, value):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.inst = cube_pb2.set_gpio
        msg.gpio.index = index
        msg.gpio.value = value
        return self.__send_msg(msg)
    
    def get_gpio(self, index):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.inst = cube_pb2.get_gpio
        msg.gpio.index = index
        msg.gpio.value = False
        return self.__send_msg(msg)
    
    def set_parameter(self, id, value):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.inst = cube_pb2.set_parameter
        msg.param.id = id
        msg.param.value = value
        return self.__send_msg(msg)
    
    def get_parameter(self, id):
        msg = cube_pb2.command_msg()
        msg.id = self.__get_id()
        msg.inst = cube_pb2.get_parameter
        msg.param.id = id
        msg.param.value = 0
        return self.__send_msg(msg)