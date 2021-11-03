from pyCubeLib import CubeGUI

def measure_func(cube):
    return False, None, (0, 0, 0)

def init_func(cube):
    return True

gui = CubeGUI(measure_func, init_func)
gui.run_app()