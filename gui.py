from functools import partial
import dearpygui.dearpygui as dpg
import serial.tools.list_ports as ports
import serial

class Application:
    def __init__(self, measure_func = None):
        window_base = partial(dpg.window, no_close=True, no_resize=True)
        self.__vp = dpg.create_viewport(title='Cube Control App', width=720, height=560, resizable=True, clear_color=((128, 128, 128, 255)))
        self.__automated_window = window_base(label="Automated measuring", width=720, height=280, collapsed=True, pos=(0, 0))
        self.__console_window = window_base(label="Console", width=480, height=540, pos=(0, 20))
        self.__connection_window = window_base(label="Connection", width=240, height=180, pos=(480, 20))
        self.__status_window = window_base(label="Status", width=240, height=180, pos=(480, 200))
        self.__control_window = window_base(label="Control", width=240, height=180, pos=(480, 380))
        self.__error_window = dpg.window(no_close=True, no_collapse=True, label="Error", pos=(240, 240), modal=True, show=False, id="ERROR_WINDOW")
        self.__serial_port = None
        self.__measure_func = measure_func
        self.__cube = None

    def __send_command(self):
        temp = dpg.get_value("CONSOLE_OUT")
        in_txt = dpg.get_value("CONSOLE_IN")
        if (in_txt == ""):
            return
        temp += in_txt
        temp += "\n"
        dpg.set_value("CONSOLE_OUT", temp)
        dpg.set_value("CONSOLE_IN", "")

    def __update_final_pos(self):
        final_pos_x = dpg.get_value("AUTO_START_X") + dpg.get_value("AUTO_STEP_X") * dpg.get_value("AUTO_COUNT_X")
        final_pos_y = dpg.get_value("AUTO_START_Y") + dpg.get_value("AUTO_STEP_Y") * dpg.get_value("AUTO_COUNT_Y")
        final_pos_z = dpg.get_value("AUTO_START_Z") + dpg.get_value("AUTO_STEP_Z") * dpg.get_value("AUTO_COUNT_Z")
        dpg.set_value("AUTO_FINAL_X", final_pos_x)
        dpg.set_value("AUTO_FINAL_Y", final_pos_y)
        dpg.set_value("AUTO_FINAL_Z", final_pos_z)
        return

    def __set_current_pos(self):
        dpg.set_value("AUTO_START_X", dpg.get_value("CONTROL_X"))
        dpg.set_value("AUTO_START_Y", dpg.get_value("CONTROL_Y"))
        dpg.set_value("AUTO_START_Z", dpg.get_value("CONTROL_Z"))

    def __update_save_location(self, s, a, u):
        path = a["file_path_name"]
        dpg.set_value("AUTO_SAVE_FILE", path)

    def __start_measuring(self):
        print("AUTOMATED MEASURING NOT IMPLEMENTED")

    def __update_ports(self):
        port_list = ports.comports(include_links=True)
        names = []
        for port in port_list:
            names.append(port[0])
        dpg.configure_item("CONNECT_PORT", items=names)

    def __connect_serial(self):
        port = dpg.get_value("CONNECT_PORT")
        try:
            self.__serial_port = serial.Serial(port, 115200, timeout = 0.1)
        except Exception:
            self.__show_error("Serial port connection failed!")
            return
        self.__serial_port.flush()
        dpg.set_value("STATUS_CON", "Connected " + port)
        dpg.set_value("CONSOLE_IN", "status")
        self.__send_command()

    def __disconnect_serial(self):
        if (self.__serial_port == None):
            self.__show_error("No port to close!")
        self.__serial_port.flush()
        self.__serial_port.close()
        self.__serial_port = None
        dpg.set_value("STATUS_CON", "Disconnected")

    def __goto_pos(self):
        return

    def __measure(self):
        if (self.__measure_func == None):
            self.__show_error("No measurement function implemented!")

    def __home(self):
        return

    def __show_error(self, error_text):
        dpg.set_value("ERROR_TEXT", error_text)
        dpg.configure_item("ERROR_WINDOW", show=True)

    def __setup_automated(self):
        base_input_float = partial(dpg.add_input_float, default_value=0, step=1, step_fast=True, callback=self.__update_final_pos)
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
                    dpg.add_button(label="Set current position", callback=self.__set_current_pos)
                with dpg.group(width=160):
                    dpg.add_text("Step size (mm):")
                    base_input_float(min_value=0, max_value=10000, id="AUTO_STEP_X")
                    base_input_float(min_value=0, max_value=10000, id="AUTO_STEP_Y")
                    base_input_float(min_value=0, max_value=10000, id="AUTO_STEP_Z")
                with dpg.group(width=160):
                    dpg.add_text("Number of steps:")
                    dpg.add_input_int(default_value=0, step=1, step_fast=True, min_value=0, max_value=10000, id="AUTO_COUNT_X", callback=self.__update_final_pos)
                    dpg.add_input_int(default_value=0, step=1, step_fast=True, min_value=0, max_value=10000, id="AUTO_COUNT_Y", callback=self.__update_final_pos)
                    dpg.add_input_int(default_value=0, step=1, step_fast=True, min_value=0, max_value=10000, id="AUTO_COUNT_Z", callback=self.__update_final_pos)
                with dpg.group(width=160):
                    dpg.add_text("Final position:")
                    dpg.add_text("0", id="AUTO_FINAL_X")
                    dpg.add_text("0", id="AUTO_FINAL_Y")
                    dpg.add_text("0", id="AUTO_FINAL_Z")
            with dpg.group(horizontal=True):
                with dpg.file_dialog(label="Select file", show=False, callback=self.__update_save_location):
                    dpg.add_file_extension(".csv", color=(255, 255, 255, 255))
                dpg.add_button(label="Select save location", user_data=dpg.last_container(), callback=lambda s, a, u: dpg.configure_item(u, show=True))
                dpg.add_text("Current location:")
                dpg.add_text("../..", id="AUTO_SAVE_FILE")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start measuring", callback=self.__start_measuring)
                #dpg.add_button(label="Stop measuring")
            with dpg.group(horizontal=True):
                dpg.add_text("Progress:")
                dpg.add_text("0/0", id="AUTO_PROGRESS")

    def __setup_console(self):
        with self.__console_window:
            dpg.add_input_text(id="CONSOLE_OUT", width=460, height=480, multiline=True, readonly=True)
            dpg.add_text("Input:")
            dpg.add_same_line()
            dpg.add_input_text(id="CONSOLE_IN", width=360, on_enter=True, callback=self.__send_command)
            dpg.add_same_line()
            dpg.add_button(label="Send", width=40, callback=self.__send_command)

    def __setup_connection(self):
        with self.__connection_window:
            dpg.add_text("Serial ports:")
            dpg.add_same_line()
            dpg.add_button(label="Refresh", callback=self.__update_ports)
            dpg.add_combo(items=[], id="CONNECT_PORT")
            dpg.add_button(label="Connect", callback=self.__connect_serial)
            dpg.add_same_line()
            dpg.add_button(label="Disconnect", callback=self.__disconnect_serial)

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
            dpg.add_button(label="Go to position", callback=self.__goto_pos)
            dpg.add_button(label="Measure", callback=self.__measure)
            dpg.add_button(label="Home", callback=self.__home)

    def __setup_error(self):
        with self.__error_window:
            dpg.add_text("Error!", id="ERROR_TEXT")
            dpg.add_button(label="Ok", callback=lambda: dpg.configure_item("ERROR_WINDOW", show=False))

    def __setup_windows(self):
        self.__setup_automated()
        self.__setup_console()
        self.__setup_connection()
        self.__setup_status()
        self.__setup_control()
        self.__setup_error()

    def run_app(self):
        #with dpg.font_registry():
        #    dpg.add_font("JetBrainsMono-Regular.ttf", 15, default_font=True)

        self.__setup_windows()
        dpg.setup_dearpygui(viewport=self.__vp)
        dpg.show_viewport(self.__vp)
        dpg.start_dearpygui()


temp = Application()
temp.run_app()