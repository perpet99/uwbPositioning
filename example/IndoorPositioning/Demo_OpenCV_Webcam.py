import math
import sys
import time
import socket
import json
import PySimpleGUI as sg
import cv2
import cmath
import cv2 as cv
from PIL import Image
import io
from threading import Thread, Lock
from queue import Queue


hostname = socket.gethostname()
UDP_IP = socket.gethostbyname(hostname)
print("***Local ip:" + str(UDP_IP) + "***")
# UDP_PORT = 80
UDP_PORT = 20001
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


from pynput import mouse

from sys import exit as exit

"""
Demo program that displays a webcam using OpenCV
"""
oldTime = time.time()
def curTime():
    global  oldTime
    t = time.time() - oldTime
    oldTime = time.time()
    return round(t * 1000)

class pointInfo:
    rx = 0.0
    ry = 0.0
    vx = 0.0
    vy = 0.0

pList = []
aList = []

rx = 100
ry = 0

def removePoint():
    if addType == "anchor":
        aList.pop()
    else:
        pList.pop()


addType = "anchor"

def addPoint(x,y):
    global rx
    global addType
    p = pointInfo()
    p.vx = x
    p.vy = y

    p.rx = rx
    p.ry = ry

    if addType == "anchor":
        aList.append(p)
    else:
        pList.append(p)

    # if 0 < len(pList):
    #     rx = 100


def calibration():

    # rx = -200

    if len(pList) < 2:
        return rx,ry


    centerRX = pList[0].rx + (pList[1].rx -pList[0].rx) /2
    centerVX = pList[0].vx + (pList[1].vx -pList[0].vx) /2
    moveRX = centerVX - centerRX
    rateX = ((pList[1].vx -pList[0].vx) / (pList[1].rx -pList[0].rx) )/ 1

    centerRY = pList[0].ry + (pList[1].ry -pList[0].ry) /2
    centerVY = pList[0].vy + (pList[1].vy -pList[0].vy) /2
    moveRY = centerVY - centerRY
    rateY = ((pList[1].vy -pList[0].vy) / (pList[1].ry -pList[0].ry) )/ 1

    # 센터 이동시키고  오리지날 값 범위기준으로 비율로 넓힘

    return moveRX +  (rx - centerRX)  * rateX  , moveRY +  (ry - centerRY)  * rateY


def read_data2():
    uwb_list = []

    try:


        line = sock.recvfrom(1024)

        uwb_data = json.loads(line[0])

        print(uwb_data)

        uwb_list = uwb_data["links"]
        for uwb_archor in uwb_list:
            print(uwb_archor)

    except Exception as e:
        print(e)



    return uwb_list
class MyThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.input_queue = Queue()
        self.results_queue = Queue()

        self.daemon = True

    # receives a name, then prints "Hello, name!"
    def run(self):
        while True:
            list = read_data2()
            self.results_queue.put(list)


def draw_uwb_tag(x, y, txt, t):
    pos_x = -250 + int(x * meter2pixel)
    pos_y = 150 - int(y * meter2pixel)
    r = 20
    # fill_cycle(pos_x, pos_y, r, "blue", t)
    # write_txt(pos_x, pos_y, txt + ": (" + str(x) + "," + str(y) + ")",
    #           "black",  t, f=('Arial', 16, 'normal'))

def draw_uwb_anchor(frame, x, y,radius,text,color=(255, 0, 0)):

    tx = int(x)
    ty = int(y)

    frame = cv2.circle(frame, (tx, ty), 3, color, 5)
    if radius > 0 :
        frame = cv2.circle(frame, (tx, ty),int( radius*100), (0, 255, 0), 5)
    frame = cv2.putText(frame, text, (tx, ty+30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    return frame

def uwb_range_offset(uwb_range):

    temp = uwb_range
    return temp

# distance_a1_a2 = 2
meter2pixel = 100
range_offset = 0.9


def tag_pos(a, b, c):
    # p = (a + b + c) / 2.0
    # s = cmath.sqrt(p * (p - a) * (p - b) * (p - c))
    # y = 2.0 * s / c
    # x = cmath.sqrt(b * b - y * y)
    if b == 0:
        b = 0.1
    cos_a = (b * b + c*c - a * a) / (2 * b * c)
    x = b * cos_a
    y = b * cmath.sqrt(1 - cos_a * cos_a)

    return round(x.real, 1), round(y.real, 1)

global cali
cali = False
def cali_onclick(x, y):
    global cali
    cali = not cali


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def main():
    sg.ChangeLookAndFeel('LightGreen')

    # define the window layout
    layout = [[sg.Text('OpenCV Demo', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Image(filename='', key='image',enable_events=True)],

              [
                sg.ReadButton('add Anchor', size=(10, 1), font='Helvetica 14'),
                  sg.ReadButton('add VPoint', size=(10, 1), font='Helvetica 14'),
                sg.ReadButton('remove', size=(10, 1), font='Helvetica 14'),
                sg.ReadButton('cali', size=(10, 1), font='Helvetica 14'),
                sg.ReadButton('Exit', size=(10, 1), font='Helvetica 14')
              ]]

    # create the window and show it without the plot
    window = sg.Window('Demo Application - OpenCV Integration',
                       location=(800, 400))
    window.Layout(layout).Finalize()

    window.bind('<Motion>', 'Motion')



    # def on_move(x, y):
    #     print(str(x))
    #     # window['x - y'].update(f'{x} - {y}')
    #
    # with mouse.Listener(on_move=on_move) as listener:
    #     listener.join()

    # ---===--- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv.VideoCapture(0)
    print("sdf")
    mouseX = 0
    mouseY = 0

    t = MyThread()
    t.start()

    list = []

    while True:
        # print(curTime())
        node_count = 0







        while True:
            try:
                print("count : " + str(t.results_queue.qsize()))
                ret = t.results_queue.get(False)
            except Exception as e:
                print(e)
                break

            list = ret

        print("input ui")
        print(list)



        event, values = window.read(0)
        # button, values = window.ReadNonBlocking()
        global addType
        if event == 'Exit' or values is None:
            sys.exit(0)
        elif event =="add Anchor":
            addType = "anchor"
        elif event == "add VPoint":
            addType = "point"
        elif event == "image" :
            print(str(mouseX) + ","+ str(mouseY))
            addPoint(mouseX,mouseY)
        elif event == 'Motion':
            e = window.user_bind_event
            mouseX = e.x
            mouseY = e.y
            # x, y = values[event]
        elif event == "remove":
            removePoint()
        elif event == "cali":
            calibration()

        elif event == 'About':
            sg.PopupNoWait('Made with PySimpleGUI',
                           'www.PySimpleGUI.org',
                           'Check out how the video keeps playing behind this window.',
                           'I finally figured out how to display frames from a webcam.',
                           'ENJOY!  Go make something really cool with this... please!',
                           keep_on_top=True)

        ret, frame = cap.read()

        # gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # let img be the PIL image
        # img = Image.fromarray(frame)  # create PIL image from frame
        # frame = cv2.line(frame, (0, 0), (511, 511), (255, 0, 0), 5)

        for p in pList:
            draw_uwb_anchor(frame,p.vx, p.vy, 0, "v")


        for idx, item in enumerate(aList):
            if idx < len(list) :
                a1_range = uwb_range_offset(float(list[idx]["R"]))
                draw_uwb_anchor(frame, item.vx, item.vy,  a1_range, "A1786(0,0)")
                node_count += 1
            else:
                draw_uwb_anchor(frame, item.vx, item.vy,  0, "A1786(0,0)")

        # for one in list:
        #     if one["A"] == "1788":
        #         a1_range = uwb_range_offset(float(one["R"]))
        #         draw_uwb_anchor(frame, 100, 100,  a1_range, "A1786(0,0)")
        #         node_count += 1
        #
        #     if one["A"] == "1787":
        #         a2_range = uwb_range_offset(float(one["R"]))
        #         draw_uwb_anchor(frame, 100 + meter2pixel * distance_a1_a2,
        #                         100,  a2_range,"A1787(" + str(distance_a1_a2) + ")")
        #         node_count += 1




        # if node_count == 0 :
        #     draw_uwb_anchor(frame,100,10,0,"anchor")

        if node_count == 2:
            global rx,ry
            r1 = uwb_range_offset(list[0]["R"])
            r2 = uwb_range_offset(list[1]["R"])

            d = distance(aList[0].vx,aList[0].vy,aList[1].vx,aList[1].vy)
            d =  d / 100
            rx, ry = tag_pos(float(r2), float(r1), d)

            if cali:
                rx2 , ry2 = calibration()
                # draw_uwb_anchor(rx2, ry2, "TAG", t_a3)
                draw_uwb_anchor(frame, rx, ry, 0, "TAG", (0, 0, 255))
            else :
                draw_uwb_anchor(frame,aList[0].vx+rx*100, aList[0].vy+ry*100,0, "TAG", (0,0,255))



        img = Image.fromarray(frame)  # create PIL image from frame

        bio = io.BytesIO()  # a binary memory resident stream
        img.save(bio, format='PNG')  # save image as png to it
        imgbytes = bio.getvalue()  # this can be used by OpenCV hopefully
        window.find_element('image').Update(data=imgbytes)


main()