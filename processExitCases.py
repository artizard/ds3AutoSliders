import threading
import macroHelpers as mh
import time
import win32api
from tkinter import messagebox
from pynput import keyboard
import pydirectinput


def startPolling():
    stopProcess.clear()
    global keyListener
    thread = threading.Thread(target=checkIfInvalidState)
    thread.start()
    keyListener = keyboard.Listener(on_press=handleKeyPress)
    keyListener.start()
def endPolling():
    stopProcess.set()
    keyListener.stop()
    pydirectinput.keyUp('shift')
    print("RELEASED SHIFT")

def shouldContinue():
    """Raises a runtime error if stopProcess is set. This will be set in scenarios where 
    the user does something that will mess up the import so the import will be stopped early. 

    Raises: 
        RuntimeError: Used as a way to exit the importMacro altogether.
    """
    if stopProcess.is_set(): # end early if told to
        raise RuntimeError("Invalid game state")
def checkIfInvalidState(): 
    """Runs on a separate thread and checks if either the mouse is moved, a key is pressed, or the game is tabbed out/closed. 
        All cases would mess up the macro, so recursion will stop. Otherwise the program will continue pressing buttons which makes
        it super hard to stop. """
    while not stopProcess.is_set():
        if not isCursorPosSafe():
            endPolling()
            mouseMovedMessage()
        elif not mh.isGameFocused():
            endPolling()
            gameClosedMesage()
        time.sleep(.01)
def isCursorPosSafe():
    x,y = win32api.GetCursorPos()
    return (
        x < safeMouseRange[0] or 
        x > safeMouseRange[2] or 
        y < safeMouseRange[1] or 
        y > safeMouseRange[3]
    )

def gameClosedMesage():
    """Shows dialog box message for the scenario where the user closes the game mid import/export."""
    messagebox.showwarning("ERROR", "The game was closed or tabbed out of during the process, the game needs to stay open for it to work.")
def mouseMovedMessage():
    """Shows dialog box message for the scenario where the user moves the mouse mid import/export."""
    messagebox.showwarning("ERROR", "The mouse was moved so the process was canceled to avoid errors. Please do not move your mouse until the process is finished.")
def keyPressedMessage():
    """Shows dialog box message for the scenario where the user moves the mouse mid import/export."""
    messagebox.showwarning("ERROR", "A key was pressed so the process was canceled to avoid errors. Please do not press keys until the process is finished.")
def handleKeyPress(key):
    #print("TEST -", mh.isUserInput)
    if not mh.isUserInput:
        return
    if hasattr(key, "char") and key.char in bannedChars:
        endPolling()
        keyPressedMessage()
    elif key in bannedKeys:
        endPolling()
        keyPressedMessage()
    
# theis will be assigned values by loadOCR() before it is used 
safeMouseRange = []

stopProcess = threading.Event() # if called then the import/export will be stopped 
bannedChars = ('e','q','g','f') # up, down, left, right, e, q, g, f
bannedKeys = (keyboard.Key.up, keyboard.Key.down, keyboard.Key.left, keyboard.Key.right)
keyListener = None