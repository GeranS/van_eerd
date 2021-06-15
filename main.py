import tkinter
from PIL import ImageTk, Image
import cv2

from pick_logic import PickLogic


class Main:
    def __init__(self):
        self.frame = None
        self.window = tkinter.Tk()

        self.window.title("Van Eerd")
        self.window.minsize(width=640, height=480)
        #self.window.attributes('fullscreen', True)

        # 0 is stop, 1 is automatic
        self.state = 0

        # Components
        self.live_feed_label = None

        # Services
        self.pick_logic = PickLogic()

    def show_frame(self):
        new_frame = self.pick_logic.current_frame

        new_frame = cv2.resize(new_frame, (1280, 720))
        image = Image.fromarray(new_frame)
        image = ImageTk.PhotoImage(image)

        self.live_feed_label.image = image
        self.live_feed_label.configure(image=image)
        self.live_feed_label.after(10, self.show_frame())

    def change_mode(self):
        if self.state == 0:
            self.state = 1
        else:
            self.state = 0

    def open_main_menu(self):
        menu = tkinter.Frame(master = self.window)
        menu.pack(fill="both", expand="yes")

        mode_button = tkinter.Button(master=menu, text="Mode: Paused", width=30, height=2, command=self.change_mode, font=("Helvetica", 12))
        mode_button.pack(side="right")

        frame_live = tkinter.Frame(master=menu)
        frame_live.pack(side="left", fill="both", anchor="nw")

        self.live_feed_label = tkinter.Label(master=frame_live)
        self.live_feed_label.pack()

        self.show_frame()