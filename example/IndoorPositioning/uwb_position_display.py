import time
import turtle
import cmath
import socket
import json
import cv2
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

# sock.setblocking(False)
# sock.settimeout(0.2)

# sock.listen(1)  # 接收的连接数
# data, addr = sock.accept()

print("start")

distance_a1_a2 = 2.0
meter2pixel = 100
range_offset = 0.9


def screen_init(width=1200, height=800, t=turtle):
    t.setup(width, height)
    t.tracer(False)
    t.hideturtle()
    t.speed(0)


def turtle_init(t=turtle):
    t.hideturtle()
    t.speed(0)


def draw_line(x0, y0, x1, y1, color="black", t=turtle):
    t.pencolor(color)

    t.up()
    t.goto(x0, y0)
    t.down()
    t.goto(x1, y1)
    t.up()


def draw_fastU(x, y, length, color="black", t=turtle):
    draw_line(x, y, x, y + length, color, t)


def draw_fastV(x, y, length, color="black", t=turtle):
    draw_line(x, y, x + length, y, color, t)


def draw_cycle(x, y, r, color="black", t=turtle):
    t.pencolor(color)

    t.up()
    t.goto(x, y - r)
    t.setheading(0)
    t.down()
    t.circle(r)
    t.up()


def fill_cycle(x, y, r, color="black", t=turtle):
    t.up()
    t.goto(x, y)
    t.down()
    t.dot(r, color)
    t.up()


def write_txt(x, y, txt, color="black", t=turtle, f=('Arial', 12, 'normal')):

    t.pencolor(color)
    t.up()
    t.goto(x, y)
    t.down()
    t.write(txt, move=False, align='left', font=f)
    t.up()


def draw_rect(x, y, w, h, color="black", t=turtle):
    t.pencolor(color)

    t.up()
    t.goto(x, y)
    t.down()
    t.goto(x + w, y)
    t.goto(x + w, y + h)
    t.goto(x, y + h)
    t.goto(x, y)
    t.up()


def fill_rect(x, y, w, h, color=("black", "black"), t=turtle):
    t.begin_fill()
    draw_rect(x, y, w, h, color, t)
    t.end_fill()
    pass


def clean(t=turtle):
    t.clear()


def draw_ui(t):
    write_txt(-300, 250, "UWB Positon", "black",  t, f=('Arial', 32, 'normal'))
    fill_rect(-400, 200, 800, 40, "black", t)
    write_txt(-50, 205, "WALL", "yellow",  t, f=('Arial', 24, 'normal'))


def draw_uwb_anchor2(x,y,t,color):
    fill_cycle(x, y, 20, color, t)

def draw_uwb_anchor(x, y, txt, range, t):
    r = 20
    fill_cycle(x, y, r, "green", t)

    draw_cycle(x, y, range*100, "orange", t)

    write_txt(x + r, y, txt + ": " + str(range) + "M",
              "black",  t, f=('Arial', 16, 'normal'))


def draw_uwb_tag(x, y, txt, t):
    pos_x = -250 + int(x * meter2pixel)
    pos_y = 150 - int(y * meter2pixel)
    r = 20
    fill_cycle(pos_x, pos_y, r, "blue", t)
    write_txt(pos_x, pos_y, txt + ": (" + str(x) + "," + str(y) + ")",
              "black",  t, f=('Arial', 16, 'normal'))

def draw_uwb_tag2(x, y, txt, t):
    pos_x = x
    pos_y = y
    r = 20
    fill_cycle(pos_x, pos_y, r, "blue", t)
    write_txt(pos_x, pos_y, txt + ": (" + str(x) + "," + str(y) + ")",
              "black",  t, f=('Arial', 16, 'normal'))


def read_data():

    line = data.recv(1024).decode('UTF-8')

    uwb_list = []

    try:
        uwb_data = json.loads(line)
        print(uwb_data)

        uwb_list = uwb_data["links"]
        for uwb_archor in uwb_list:
            print(uwb_archor)

    except:
        print(line)
    print("")

    return uwb_list

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


def uwb_range_offset(uwb_range):

    temp = uwb_range
    return temp


def print_xy( x, y):
    if y < -300:
        return
    addPoint(x, y)

    # turtle.goto(x, y)
    # turtle.stamp()   # 도장을 찍습니다.
    # turtle.write("x:%d, y:%d"%(x,y))


s = turtle.Screen()
s.onscreenclick(print_xy, 1)




CURSOR_SIZE = 70
FONT_SIZE = 12
FONT = ('Arial', FONT_SIZE, 'bold')

def createButton(button,x,y,size,color,str,fun):
    button.hideturtle()
    button.shape('square')
    button.fillcolor(color)
    button.penup()
    button.goto(x, y)
    button.write(str, align='center', font=FONT)
    button.sety(y + CURSOR_SIZE + FONT_SIZE)
    button.onclick(fun)
    button.turtlesize(size)
    button.showturtle()


# createButton(turtle.Turtle(),0,0,25,'yellow')

global cali
cali = False
def cali_onclick(x, y):
    global cali
    cali = not cali


    # turtle.dot(100, 'cyan')

def remove_onclick(x, y):
    removePoint()


global Show
Show = True


def sh_onclick(x, y):
    global Show
    Show = not Show


createButton(turtle.Turtle(),-300,-400,5,'blue',"remove",remove_onclick)

createButton(turtle.Turtle(),-150,-400,5,'blue',"cali",cali_onclick)

createButton(turtle.Turtle(),0,-400,5,'blue',"show/hide",sh_onclick)



class pointInfo:
    rx = 0.0
    ry = 0.0
    vx = 0.0
    vy = 0.0

pList = []




rx = -100
ry = 0





def addPoint(x,y):
    global rx

    p = pointInfo()
    p.vx = x
    p.vy = y


    p.rx = rx
    p.ry = ry

    pList.append(p)

    # if 0 < len(pList):
    #     rx = 100


def removePoint():
    pList.pop()
    # del pList[-1]


oldTime = time.time()
def curTime():
    global  oldTime
    t = time.time() - oldTime
    oldTime = time.time()
    return round(t * 1000)

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

def run():
    while True:
        list = read_data2()


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

def main():

    t = MyThread()
    t.start()


    t_ui = turtle.Turtle()
    t_a1 = turtle.Turtle()
    t_a2 = turtle.Turtle()
    t_a3 = turtle.Turtle()

    t_p = turtle.Turtle()

    turtle_init(t_p)

    turtle_init(t_ui)
    turtle_init(t_a1)
    turtle_init(t_a2)
    turtle_init(t_a3)

    a1_range = 0.0
    a2_range = 0.0

    draw_ui(t_ui)

    cam = cv2.VideoCapture(0)

    mirror = False
    c = 1

    # s.register_shape("1.png")






    # s.addshape('1.png')
    # t = turtle.Turtle()
    # t.shape('1.png')
    # t.forward(100)

    # s.bgpic("1.png")
    c = 1
    while True:

        print(curTime())

        node_count = 0
        # c += 1
        # if c %2 == 0:
        #     draw_uwb_anchor(-250, 150, "A1782(0,0)", 1, t_a1)
        # else :
        #     clean(t_a1)

        list = []

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

        # ret_val, img = cam.read()

        if mirror:
            img = cv2.flip(img, 1)

        # cv2.imshow('my webcam', img)
        fname = "./img/"+str(c)+".png"
        # cv2.imwrite(fname, img)
        # s.bgpic(fname)
        c += 1

        clean(t_p)

        for p in pList:

            draw_uwb_anchor2(p.vx, p.vy, t_p,"red")


        for one in list:
            if one["A"] == "1788":
                clean(t_a1)
                a1_range = uwb_range_offset(float(one["R"]))
                draw_uwb_anchor(-250, 150, "A1786(0,0)", a1_range, t_a1)
                node_count += 1

            if one["A"] == "1787":
                clean(t_a2)
                a2_range = uwb_range_offset(float(one["R"]))
                draw_uwb_anchor(-250 + meter2pixel * distance_a1_a2,
                                150, "A1787(" + str(distance_a1_a2)+")", a2_range, t_a2)
                node_count += 1


        if node_count == 0 :
            clean(t_a1)
            draw_uwb_anchor(-250, 150, "A1782(0,0)", 1, t_a1)

        if node_count == 2:
            global rx,ry
            rx, ry = tag_pos(a2_range, a1_range, distance_a1_a2)
            # print(x, y)


        clean(t_a3)

        if cali:

            rx2 , ry2 = calibration()
            draw_uwb_tag2(rx2, ry2, "TAG", t_a3)
        else :
            draw_uwb_tag(rx, ry, "TAG", t_a3)



        # time.sleep(0.1)

        # s.update()


    turtle.mainloop()


if __name__ == '__main__':
    main()
