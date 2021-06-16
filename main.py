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

        # 0 is stop, 1 is automatic, 2 is manual
        self.state = tkinter.StringVar(None, "paused")

        # Components
        self.live_feed_label = None
        self.mode_button = None

        # Services
        self.pick_logic = PickLogic(self)

        self.open_main_menu()
        self.window.mainloop()

    def show_frame(self):

        #time.sleep(0.05)
        new_frame = self.pick_logic.current_frame

        if new_frame is None:
            new_frame = np.zeros((1280,720))

        new_frame = cv2.resize(new_frame, (1280, 720))
        image = Image.fromarray(new_frame)
        image = ImageTk.PhotoImage(image)

        self.live_feed_label.image = image
        self.live_feed_label.configure(image=image)
        self.live_feed_label.after(10, self.show_frame)

    def change_mode(self):
        if self.state == 0:
            self.state = 1
            self.mode_button.configure(text="Mode: Automatic")
        else:
            self.state = 0
            self.mode_button.configure(text="Mode: Paused")



    def open_main_menu(self):
        menu = tkinter.Frame(master=self.window)
        menu.pack(fill="both", expand="yes")

        #mode_button = tkinter.Button(master=menu, text="Mode: Paused", width=30, height=2, command=self.change_mode,
        #                             font=("Helvetica", 12))
        #mode_button.pack(side="right")

        modes = {"Paused": "paused",
                 "Automatic": "auto",
                 "Manual": "manual"}

        for (text, value) in modes.items():
            tkinter.Radiobutton(master=menu, text=text, variable=self.state,
                                value=value, indicator=0, width=30).pack(anchor="nw")

        frame_live = tkinter.Frame(master=menu)
        frame_live.pack(side="left", fill="both", anchor="nw")

        self.live_feed_label = tkinter.Label(master=frame_live)
        self.live_feed_label.pack()

        _thread.start_new_thread(self.show_frame, ())


Main()
