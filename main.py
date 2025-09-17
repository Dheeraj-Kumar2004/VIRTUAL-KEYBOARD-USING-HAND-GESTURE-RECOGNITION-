import cv2
import numpy as np
from pynput.keyboard import Controller
from handtracker import HandTracker  # Import your HandTracker module

# Initialize the keyboard controller
keyboard = Controller()

# Define key layouts for the virtual keyboard
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "CL"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "SP"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "APR"]]

keys1 = [["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "CL"],
         ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "SP"],
         ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "APR"]]

# Initialize the HandTracker
hand_tracker = HandTracker()

# Function to draw buttons on the screen
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (96, 96, 96), cv2.FILLED)
        cv2.putText(img, button.text, (x + 10, y + 40),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    return img

# Create button objects for both layouts
class Button:
    def __init__(self, pos, text):
        self.pos = pos
        self.size = (60, 60)
        self.text = text

buttonList = []
buttonList1 = []

for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([80 * j + 20, 80 * i + 10], key))

for i in range(len(keys1)):
    for j, key in enumerate(keys1[i]):
        buttonList1.append(Button([80 * j + 20, 80 * i + 10], key))

cap = cv2.VideoCapture(0)  # Initialize video capture
app = 0      
delay = 0
text = ""

while True:
    success, frame = cap.read()
    frame = cv2.resize(frame, (1000, 580))
    frame = cv2.flip(frame, 1)

    # Use HandTracker methods
    frame = hand_tracker.findHands(frame)
    lmList = hand_tracker.findPosition(frame)

    if app == 0:
        frame = drawAll(frame, buttonList) 
        list = buttonList
    else:
        frame = drawAll(frame, buttonList1) 
        list = buttonList1 

    if lmList:
        try:
            x5, y5 = lmList[5][1], lmList[5][2]
            x17, y17 = lmList[17][1], lmList[17][2]
            dis = np.sqrt((x5 - x17) ** 2 + (y5 - y17) ** 2)  # Calculate distance

            # Example of calculating distanceCM based on dis (you may replace with actual logic)
            distanceCM = dis / 10  # Adjust this based on your calibration

            if 20 < distanceCM < 50:
                x, y = lmList[8][1], lmList[8][2]
                x2, y2 = lmList[6][1], lmList[6][2]
                x3, y3 = lmList[12][1], lmList[12][2]
                cv2.circle(frame, (x, y), 20, (255, 0, 255), cv2.FILLED)
                cv2.circle(frame, (x3, y3), 20, (255, 0, 255), cv2.FILLED)

                if y2 > y:
                    for button in list:
                        xb, yb = button.pos
                        wb, hb = button.size
                        
                        if (xb < x < xb + wb) and (yb < y < yb + hb):
                            cv2.rectangle(frame, (xb - 5, yb - 5), (xb + wb + 5, yb + hb + 5), (160, 160, 160), cv2.FILLED)
                            cv2.putText(frame, button.text, (xb + 20, yb + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                            dis = np.sqrt((x - x3) ** 2 + (y - y3) ** 2)
                            
                            if dis < 50 and delay == 0:
                                k = button.text
                                cv2.rectangle(frame, (xb - 5, yb - 5), (xb + wb + 5, yb + hb + 5), (255, 255, 255), cv2.FILLED)
                                cv2.putText(frame, k, (xb + 20, yb + 65), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 4)
                                
                                # Handle keyboard actions here (implement your existing logic)
                                if k == "CL":
                                     text = text[:-1]  # Clear text
                                elif k == "SP":
                                    if len(text) == 0 or text[-1] != ' ':  # Ensure no consecutive spaces
                                         text += ' '
                                elif k == "APR":
                                    app = 1 - app  # Toggle between layouts
                                else:
                                    keyboard.press(k)
                                    keyboard.release(k)
                                    text += k
                                
                                delay = 1
         
        except Exception as e:
            print(f"Error: {e}")  # Handle exceptions and print error message
           
    if delay != 0:
        delay += 1
        if delay > 10:
            delay = 0      

    cv2.rectangle(frame, (20, 250), (850, 400), (255, 255, 255), cv2.FILLED)
    cv2.putText(frame, text, (30, 300), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
    hand_tracker.getFPS(frame)  # Display FPS
    cv2.imshow('Virtual Keyboard', frame)
    
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
