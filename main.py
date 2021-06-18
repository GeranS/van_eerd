import tkinter
from PIL import ImageTk, Image
import cv2
import _thread
import numpy as np

from pick_logic import PickLogic


class Main:
    def __init__(self):
        self.frame = None
        self.window = tkinter.Tk()

        self.window.title("Van Eerd")
        self.window.minsize(width=640, height=480)
        # self.window.attributes('fullscreen', True)

        # State
        self.state = tkinter.StringVar(None, "paused")
        self.show_manual_buttons = False

        # Components
        self.live_feed_label = None
        self.mode_button = None
        self.manual_mode_frame = None

        # Services
        self.pick_logic = PickLogic(self)

        self.open_main_menu()
        self.window.mainloop()

    def show_frame(self):

        # time.sleep(0.05)
        new_frame = self.pick_logic.current_frame

        if self.state.get() == "manual" and self.show_manual_buttons is False:
            # Show buttons
            print("Show manual mode buttons")
            self.manual_mode_frame.pack(anchor="ne", side="right")
            self.show_manual_buttons = True
        if self.state.get() != "manual" and self.show_manual_buttons is True:
            # Hide buttons
            print("Hide manual mode buttons")
            self.manual_mode_frame.pack_forget()
            self.show_manual_buttons = False

        if new_frame is None:
            new_frame = np.zeros((720, 1280))
        else:
            try:
                new_frame = cv2.resize(new_frame, (1280, 720))
                new_frame = cv2.cvtColor(new_frame, cv2.COLOR_RGBA2BGR)
            except:
                new_frame = np.zeros((720, 1280))

        image = Image.fromarray(new_frame)
        image = ImageTk.PhotoImage(image)

        self.live_feed_label.image = image
        self.live_feed_label.configure(image=image)
        self.live_feed_label.after(10, self.show_frame)

    def open_main_menu(self):
        menu = tkinter.Frame(master=self.window)
        menu.pack(fill="both", expand="yes")

        # mode_button = tkinter.Button(master=menu, text="Mode: Paused", width=30, height=2, command=self.change_mode,
        #                             font=("Helvetica", 12))
        # mode_button.pack(side="right")

        modes = {"Paused": "paused",
                 "Automatic": "auto",
                 "Manual": "manual",
                 "Test": "test",
                 "Calibrate Matrix": "matrix"}

        for (text, value) in modes.items():
            tkinter.Radiobutton(master=menu, text=text, variable=self.state,
                                value=value, indicator=0, width=30).pack(anchor="nw")

        frame_live = tkinter.Frame(master=menu)
        frame_live.pack(side="left", fill="both", anchor="nw")

        self.live_feed_label = tkinter.Label(master=frame_live)
        self.live_feed_label.pack()

        # Frame for manual mode buttons
        self.manual_mode_frame = tkinter.Frame(master=self.window)

        button_grab_stack = tkinter.Button(master=self.manual_mode_frame, text="Grab Stack", width=20, command=self.pick_logic.grab_one_stack)
        button_grab_stack.pack(anchor="ne")

        button_grab_sheet = tkinter.Button(master=self.manual_mode_frame, text="Grab Sheet", width=20)
        button_grab_sheet.pack(anchor="ne")

        button_get_new_grid = tkinter.Button(master=self.manual_mode_frame, text="Get New Grid", width=20, command=self.pick_logic.get_pile_grid_and_set_as_active)
        button_get_new_grid.pack(anchor="ne")

        _thread.start_new_thread(self.show_frame, ())


Main()
