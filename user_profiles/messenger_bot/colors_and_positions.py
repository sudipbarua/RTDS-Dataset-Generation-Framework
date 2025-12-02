"""
This is a helper program to prints the live coordinates of the mouse pointer as it moves through the screen.
It can also print the color of the corresponding pixels. These data will help us in later part of the development and
modification.
NOTE: You must install tkinter on Linux to use MouseInfo. Run the following: sudo apt-get install python3-tk python3-dev
NotImplementedError: "scrot" must be installed to use screenshot functions in Linux. Run: sudo apt-get install scrot
pip install Pillow
Due to security issue, ubuntu may block pyautogui from taking screenshots or saves black-screen as screenshot.
    solution: logout Ubuntu system. At the login screen, under the password field, click the gear icon and switch to Xorg
Point of new message: Point(x=481, y=997) RGB(red=228, green=230, blue=235)

"""
import pyautogui as pt
from time import sleep

while True:
    posXY = pt.position()
    pixel_val = pt.pixel(posXY[0], posXY[1])
    print(posXY, pixel_val)
    sleep(5)
    if posXY[0] == 0:
        break
