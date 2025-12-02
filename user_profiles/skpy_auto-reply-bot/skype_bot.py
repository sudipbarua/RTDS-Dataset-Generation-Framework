from skpy import Skype
from skpy import SkypeEventLoop, SkypeNewMessageEvent
import random
import os
from time import sleep
# # Create a Skype object
# skype = Skype("tnikola230@gmail.com", "tucKN2022")
# #
# # Get the contact you want to send a message to
# contact = skype.contacts["live:sudip.barua"]
photo_dir = 'photos'
video_dir = 'videos'
doc_dir = 'docs'
replies_file = 'replies.txt'


def rand_reply():
    # Open the file in read mode
    with open(replies_file, "r") as f:
        # Read the file line by line
        lines = f.readlines()
        # Choose a random line from the file
        line = random.choice(lines)
        # Print the selected line
        return line


def send_file(dir):
    # get the filename of a randomly selected file from dir
    filename = random.choice(os.listdir(dir))
    # create the full path
    path = os.path.join(dir, filename)
    return path, filename

class SkypeReply(SkypeEventLoop):
    def __init__(self):
        super(SkypeReply, self).__init__("tnikola230@gmail.com", "tucKN2022")

    def onEvent(self, event):
        # check for new messages
        if isinstance(event, SkypeNewMessageEvent) and not event.msg.userId == self.userId:
            txt = str(event.msg.content).lower()  # collect message text content
            sleep(10)
            if 'photo' in txt:
                try:
                    path, filename = send_file(photo_dir)
                    with open(path, 'rb') as f:
                        event.msg.chat.sendFile(f, filename)
                    event.msg.chat.sendMsg("here is my photo")
                except:
                    event.msg.chat.sendMsg("I don\'t share photos with strangers.")
            elif 'video' in txt:
                try:
                    path, filename = send_file(video_dir)
                    with open(path, 'rb') as f:
                        event.msg.chat.sendFile(f, filename)
                except:
                    event.msg.chat.sendMsg("Sorry!!! I dont have any")
            elif 'paper' in txt:
                try:
                    path, filename = send_file(doc_dir)
                    with open(path, 'rb') as f:
                        event.msg.chat.sendFile(f, filename)
                    event.msg.chat.sendMsg("here are some of my works")
                except:
                    event.msg.chat.sendMsg("Sorry!!! I dont have any")
            # if txt is not None:
            else:
                reply = rand_reply()
                event.msg.chat.sendMsg(reply)


check_msg = SkypeReply()

# Start the event loop
check_msg.loop()
