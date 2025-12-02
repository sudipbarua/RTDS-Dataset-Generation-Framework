"""
Solution to Not Implemented Error: Only be faced in linux machines
can be fixed by installing one of the copy/paste mechanisms:
sudo apt-get install xsel to install the xsel utility.
sudo apt-get install xclip to install the xclip utility.
pip install gtk to install the gtk Python module.
pip install PyQt4 to install the PyQt4 Python module.
"""
import pyautogui as pt
from time import sleep
import pyperclip
import random
from pyChatGPT import ChatGPT

sleep(3)
init_pos_icon_path = '/home/sudip/rtds_project/user_profiles/messenger_bot/initpoint_icons.png'
blue_dot_icon_path = '/home/sudip/rtds_project/user_profiles/messenger_bot/blue_circle.png'
call_icon_path = '/home/sudip/rtds_project/user_profiles/messenger_bot/call_icon.png'
gif_icon_path = '/home/sudip/rtds_project/user_profiles/messenger_bot/gif_icon.png'
position1 = pt.locateOnScreen(init_pos_icon_path, confidence=0.6)
x = position1[0]
y = position1[1]
# the copy button relative positions: differs according to OS and screen resolution
relpos_copy_button_x = 13
relpos_copy_button_y = -165
# reply type box relative position: differs based on resolution
relpos_type_box_x = 270
relpos_type_box_y = 26


# Get message
def get_message():
    global x, y
    # initial position
    position = pt.locateOnScreen(init_pos_icon_path, confidence=0.8)
    x = position[0]
    y = position[1]
    pt.moveTo(x, y, duration=1)  # move to initial position
    # init point Point(x=482, y=1026) RGB(red=255, green=255, blue=255)
    # Point of new message: Point(x=481, y=997) RGB(red=228, green=230, blue=235)
    # copy point: Point(x=494, y=832) RGB(red=232, green=232, blue=233)
    sleep(5)
    pt.moveTo(x, y - 29, duration=0.1)   # move to new received message position
    pt.tripleClick()  # triple click to select the whole text
    # to copy the selected text, we use hotkeys "ctrl+c" shortcut
    pt.keyDown('ctrl')  # hold control key
    pt.press('c')  # press c once
    pt.keyUp('ctrl')  # release control key
    new_msg = pyperclip.paste()
    return new_msg


def post_response(message):
    global x, y
    position = pt.locateOnScreen(init_pos_icon_path, confidence=0.9)
    x = position[0]
    y = position[1]
    # init point Point(x=482, y=1026) RGB(red=255, green=255, blue=255)
    # point of typing message: Point(x=759, y=1053) RGB(red=243, green=243, blue=245)
    pt.moveTo(x + relpos_type_box_x, y + relpos_type_box_y, duration=0.5)  # move to message typing box
    pt.click()
    pt.typewrite(message, interval=0.1)  # type message/reply
    pt.typewrite("\n", interval=0.01)  # similar to pressing enter after finishing typing


def call_user():
    try:
        position = pt.locateOnScreen(call_icon_path, confidence=0.6)
        x = position[0]
        y = position[1]
        pt.moveTo(x, y, duration=0.5)
        pt.click()
    except:
        print("no call button")


def send_gif():
    try:
        position = pt.locateOnScreen(gif_icon_path, confidence=0.9)
        x = position[0]
        y = position[1]
        # move to gif button and click
        pt.moveTo(x, y, duration=0.5)
        pt.click()
        pt.typewrite(rand_reply(), interval=0.1)
        pt.moveRel(0, -20, duration=0.5)  # move to gif
        pt.click()  # send gif
    except:
        print("no gif button")


def ai_reply(msg):
    # Open authentication token file copied from chatGPT>site inspect>Application/storage>
    # >__Secure-next-auth.session-token in read mode
    with open("openAI_session_auth_token.txt", "r") as f:
        open_ai_session_token = f.read()
    api = ChatGPT(open_ai_session_token)
    reply = api.send_message(msg)
    return reply['message']


def rand_reply():
    # Open the file in read mode
    with open("replies.txt", "r") as f:
        # Read the file line by line
        lines = f.readlines()

        # Choose a random line from the file
        line = random.choice(lines)

        # Print the selected line
        return line


def process_response(message):
    msg = str(message).lower()  # convert to lower case: better while matching/checking for keywords
    if "hello" in msg or "hi" in msg:
        reply = "Hello!! how are you?"

        return reply
    if "photo" in msg:
        send_gif()
        return "here is a photo"

    if "how are you?" in msg:
        return "I am good!! thanks for asking :)"

    if "call" in msg:
        call_user()
        return "ok... I am calling you"

    if "bye" in msg:
        return "bye. Take care..."

    if msg is not None:
        return rand_reply()
        # return ai_reply(message)


# Check for new messages every 5s
def check_for_new_msgs():
    pt.moveTo(x, y-25, duration=0.5)

    while True:
        sleep(5)
        # Continuously check for the blue dot
        try:
            position = pt.locateOnScreen(blue_dot_icon_path, confidence=0.7)
            if position is not None:
                pt.moveTo(position)
                pt.moveRel(-100, 0)
                pt.click()
                sleep(0.5)
        except(Exception):
            print("No new messages")

        # Point of new message: Point(x=481, y=997) RGB(red=228, green=230, blue=235)
        if pt.pixelMatchesColor(x, y-25, (228, 230, 235), tolerance=10):
            # print("found new msg")  # before implementing, calibrate the y coordinate by subtracting the pixel val
            reply = process_response(get_message())
            post_response(reply)
        else:
            print("No messages yet...")


check_for_new_msgs()
