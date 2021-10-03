from functools import partial
import dearpygui.dearpygui as dpg
import time

class Application:
    def __init__(self):
        window_base = partial(dpg.window, no_close=True, no_resize=True)
        self.__vp = dpg.create_viewport(title='Cube Control App', width=720, height=560, resizable=True, clear_color=((128, 128, 128, 255)))
        self.__automated_window = window_base(label="Automated measuring", width=720, height=280, collapsed=True, pos=(0, 0))
        self.__console_window = window_base(label="Console", width=480, height=540, pos=(0, 20))
        self.__connection_window = window_base(label="Connection", width=240, height=180, pos=(480, 20))
        self.__status_window = window_base(label="Status", width=240, height=180, pos=(480, 200))
        self.__control_window = window_base(label="Control", width=240, height=180, pos=(480, 380))

    def __test_func(self, s, a, u):
        temp = dpg.get_value("CONSOLE_OUT")
        temp += str(dpg.get_value("CONSOLE_IN"))
        temp += "\n"
        dpg.set_value("CONSOLE_OUT", temp)
        dpg.set_value("CONSOLE_IN", "")

    def __setup_automated(self):
        base_input_float = partial(dpg.add_input_float, default_value=0, step=1, step_fast=True)
        with self.__automated_window:
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Axis:")
                    dpg.add_text("X")
                    dpg.add_text("Y")
                    dpg.add_text("Z")
                with dpg.group(width=160):
                    dpg.add_text("Start position:")
                    base_input_float(min_value=-10000, max_value=10000, id="AUTO_START_X")
                    base_input_float(min_value=-10000, max_value=10000, id="AUTO_START_Y")
                    base_input_float(min_value=-10000, max_value=10000, id="AUTO_START_Z")
                    dpg.add_button(label="Set current position")
                with dpg.group(width=160):
                    dpg.add_text("Step size (mm):")
                    base_input_float(min_value=0, max_value=10000, id="AUTO_STEP_X")
                    base_input_float(min_value=0, max_value=10000, id="AUTO_STEP_Y")
                    base_input_float(min_value=0, max_value=10000, id="AUTO_STEP_Z")
                with dpg.group(width=160):
                    dpg.add_text("Number of steps:")
                    dpg.add_input_int(default_value=0, step=1, step_fast=True, min_value=0, max_value=10000, id="AUTO_COUNT_X")
                    dpg.add_input_int(default_value=0, step=1, step_fast=True, min_value=0, max_value=10000, id="AUTO_COUNT_Y")
                    dpg.add_input_int(default_value=0, step=1, step_fast=True, min_value=0, max_value=10000, id="AUTO_COUNT_Z")
                with dpg.group(width=160):
                    dpg.add_text("Final position:")
                    dpg.add_text("0", id="AUTO_FINAL_X")
                    dpg.add_text("0", id="AUTO_FINAL_Y")
                    dpg.add_text("0", id="AUTO_FINAL_Z")
            with dpg.group(horizontal=True):
                with dpg.file_dialog(label="Select file", show=False, callback=lambda s, a, u : print(s, a, u)):
                    dpg.add_file_extension(".csv", color=(255, 255, 255, 255))
                dpg.add_button(label="Select save location", user_data=dpg.last_container(), callback=lambda s, a, u: dpg.configure_item(u, show=True))
                dpg.add_text("Current location:")
                dpg.add_text("../..", id="AUTO_SAVE_FILE")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start measuring")
                dpg.add_button(label="Stop measuring")
            with dpg.group(horizontal=True):
                dpg.add_text("Progress:")
                dpg.add_text("0/0", id="AUTO_PROGRESS")

    def __setup_console(self):
        with self.__console_window:
            dpg.add_input_text(id="CONSOLE_OUT", width=460, height=480, multiline=True, readonly=True)
            dpg.add_text("Input:")
            dpg.add_same_line()
            dpg.add_input_text(id="CONSOLE_IN", width=360, on_enter=True, callback=self.__test_func)
            dpg.add_same_line()
            dpg.add_button(label="Send", width=40, callback=self.__test_func)

    def __setup_connection(self):
        with self.__connection_window:
            dpg.add_text("Serial ports:")
            dpg.add_same_line()
            dpg.add_button(label="Refresh")
            dpg.add_combo(items=("Port1", "Port2", "Port3"), id="CONNECT_PORT")
            dpg.add_button(label="Connect")
            dpg.add_same_line()
            dpg.add_button(label="Disconnect")

    def __setup_status(self):
        with self.__status_window:
            dpg.add_text("Status:")
            dpg.add_same_line()
            dpg.add_text("Disconnected", id="STATUS_CON")
            dpg.add_text("Position:")
            dpg.add_same_line()
            dpg.add_text("(0, 0, 0)", id="STATUS_POS")
            dpg.add_text("Mode:")
            dpg.add_same_line()
            dpg.add_text("Cartesian", id="STATUS_MODE")
            dpg.add_text("Last sent ID:")
            dpg.add_same_line()
            dpg.add_text("0", id="STATUS_SENT_ID")
            dpg.add_text("Last ack ID:")
            dpg.add_same_line()
            dpg.add_text("0", id="STATUS_ACK_ID")

    def __setup_control(self):
        base_input_float = partial(dpg.add_input_float, default_value=0, step=1, step_fast=True, min_value=-10000, max_value=10000)
        with self.__control_window:
            dpg.add_text("X:")
            dpg.add_same_line()
            base_input_float(id="CONTROL_X")
            dpg.add_text("Y:")
            dpg.add_same_line()
            base_input_float(id="CONTROL_Y")
            dpg.add_text("Z:")
            dpg.add_same_line()
            base_input_float(id="CONTROL_Z")
            dpg.add_button(label="Go to position")
            dpg.add_button(label="Measure")
            dpg.add_button(label="Home")

    def __setup_windows(self):
        self.__setup_automated()
        self.__setup_console()
        self.__setup_connection()
        self.__setup_status()
        self.__setup_control()

    def run_app(self):
        #with dpg.font_registry():
        #    dpg.add_font("JetBrainsMono-Regular.ttf", 15, default_font=True)

        self.__setup_windows()
        dpg.setup_dearpygui(viewport=self.__vp)
        dpg.show_viewport(self.__vp)
        dpg.start_dearpygui()


temp = Application()
temp.run_app()