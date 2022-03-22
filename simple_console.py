from pyCubeLib import CubeComm
import serial
import cmd
import sys

class CubeConsole(cmd.Cmd):
    prompt = ">> "
    ruler = "-"
    intro = "Cube Movement Control. Type help or ? for help."
    doc_header = "Commands (type help <command> for more info):"
    cube = ""


    def __init__(self, cube):
        super().__init__()
        self.cube = cube

    def default(self, line):
        print("!!! Unknown command:", line)

    def emptyline(self):
        return

    def do_exit(self, args):
        """exit the console"""
        return True
    
    def do_EOF(self, args):
        """exit the console"""
        print("EOF")
        return True

    def do_home(self, args):
        """Home the machine"""
        error, ret = self.cube.home()
        if error:
            print("!!! Comms error:", error)
            return
        if ret.error != 0:
            print("!!! Cube error:", ret.error)
            return
        print("Homed successfully!")

    def do_move(self, args):
        """Move to coordinate.\nSyntax: move X Y Z"""
        split_args = args.split()
        if (len(split_args) != 3):
            print("!!! Wrong arguments!")
            return
        coord = list(map(float, split_args))
        error, ret = self.cube.move_to(coord[0], coord[1], coord[2])
        if error:
            print("!!! Comms error:", error)
            return
        if ret.error != 0:
            print("!!! Cube error:", ret.error)
            return
        print("Moved to:", coord)


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("Missing COM port path")
        exit(1)
    serial_port = None
    try:
        serial_port = serial.Serial(sys.argv[1], 115200, timeout = 0.1)
    except Exception:
        print("Serial port opening failed.")
        exit(1)
    serial_port.flush()
    cube = CubeComm(200)
    cube.set_serial_port(serial_port)

    print("Checking cube:")
    error, ret = cube.status()
    if error:
        print("!!! Comm error:", error)
        exit(1)
    if ret.error != 0:
        print("!!! Cube error:", ret.error)
        exit(1)
    print(ret)
    
    console = CubeConsole(cube)
    console.cmdloop()
    serial_port.close()
    exit(0)
    
        
    
