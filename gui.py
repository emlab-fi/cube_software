from functools import partial
import dearpygui.dearpygui as dpg

window_base = partial(dpg.window, no_close=True, no_resize=True)

vp = dpg.create_viewport(title='Cube Control App', width=720, height=560, resizable=False) # create viewport takes in config options too!


with window_base(label="Automated measuring", width=720, height=280, collapsed=True, pos=(0, 0)) as automation_window:
    dpg.add_text("Here b stuff soon")

with window_base(label="Console", width=480, height=540, pos=(0, 20)) as console_window:
    dpg.add_text("Here b stuff soon")

with window_base(label="Connection", width=240, height=180, pos=(480, 20)) as connection_window:
    dpg.add_text("Here b stuff soon")

with window_base(label="Status", width=240, height=180, pos=(480, 200)) as status_window:
    dpg.add_text("Here b stuff soon")

with window_base(label="Control", width=240, height=180, pos=(480, 380)) as control_window:
    dpg.add_text("Here b stuff soon")

dpg.setup_dearpygui(viewport=vp)
dpg.show_viewport(vp)
dpg.start_dearpygui()