import cv2,os,time,json,datetime
from colorama import Fore,Style
import PySimpleGUI as sg
import requests

# Modes Available Are:
#     * Normal
#      * Range
#       * B'n'W
#        * Pixelated
#         * Blur

a = False
title = "Webcam - PySimpleGUI"
xml = "haarcascade_frontalface_default.xml"

if os.listdir().count("config.json") == False:
    open("config.json", "w").write("""{
    "Runtime": false,
    "Cam_W": 640,
    "Cam_H": 480,
    "Theme": "SystemDefaultForReal",
    "Color_G": [35, 230, 25],
    "Mode": "Normal",
    "Vision": "Normal"      
}""")

data = json.load(open("config.json"))

if os.listdir().count(xml) == False and data["Mode"] == "Normal":
    try:
        URL = "https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/haarcascade_frontalface_default.xml"
        response = requests.get(URL)
        with open(xml, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(Fore.RED+str(e)+Fore.RESET)

color_green = data["Color_G"]
font = cv2.FONT_HERSHEY_DUPLEX

sg.theme(data["Theme"])
camera_Width  = data["Cam_W"] # 480 # 640 # 1024 # 1280
camera_Heigth = data["Cam_H"] # 320 # 480 # 780  # 930

if data["Mode"] == "Normal" and os.listdir().count(xml):face_cascade = cv2.CascadeClassifier(xml)
frameSize = (camera_Width, camera_Heigth)

print(Fore.GREEN+Style.BRIGHT+"Camera Size: " + str((camera_Width, camera_Heigth)) + Fore.WHITE +Style.NORMAL)
if data["Mode"] == "Normal":print(Fore.GREEN+Style.BRIGHT+"Cascade Classifier: " + str(xml) + Fore.WHITE + Style.NORMAL)


if os.path.isfile(data["Vision"]): 
    if data["Vision"].endswith(".mp4"):
        cap = cv2.VideoCapture(data["Vision"])

elif data["Vision"] == "Normal":cap = cv2.VideoCapture(0)
def callback(value):
    pass

def setup_trackbars():
    cv2.namedWindow("Trackbars", 1)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255
        for j in "HSV":
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)

def get_trackbar_values():
    values = []

    for i in ["MIN", "MAX"]:
        for j in "HSV":
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values

menu1 = [[sg.Text("Camera View")],
         [sg.Image(filename="", key="cam1")],
         [sg.Button("Smile Pls",key="shot1",size=(100,0))],
         [sg.Button("Clear All Shots",key="shot_clear",size=(100,0))]]

layout = [[sg.Column(menu1,element_justification="center")]]

window = sg.Window(title, layout, 
                   no_titlebar=False)   


if data["Runtime"] == True:
    if os.listdir().count("log.txt") == False:open("log.txt", "w")
    g1 = str(len(open("log.txt", "r").read().splitlines())+1)
    g = open("log.txt", "a")
    g.write(datetime.datetime.now().strftime("["+g1+"] Opened on %d/%m/%y %I:%M:%S\n"))
    g.close()

if data["Mode"] == "Range":setup_trackbars()
while True:
    start_time = time.time()
    ret, frameOrig = cap.read()
    event, values = window.read(timeout=.20)
    
    if event == "shot_clear":
        try:
            f = os.listdir('images')
            if len(f) == 0:pass
            if not len(f) == 0: 
                for i in f:
                    del_f = open(f"images/{i}","w")
                    del_f.write("")
                    del_f.close()
                    os.system(f'del images\{i}')
        except Exception as e:
            pass
    

    elif event == sg.WIN_CLOSED:
        if data["Runtime"] == True:
            if os.listdir().count("log.txt") == False:open("log.txt", "w")
            g1 = str(len(open("log.txt", "r").read().splitlines())+1)
            g = open("log.txt", "a")
            g.write(datetime.datetime.now().strftime("["+g1+"] Closed on %d/%m/%y %I:%M:%S\n"))
            g.close()
        print(Fore.RED + Style.BRIGHT +  f'\n"{title}" has been closed' + Fore.WHITE +Style.NORMAL)
        break
    
    # get camera frame
    ret, frameOrig = cap.read()
    frame = cv2.resize(frameOrig, frameSize)
    

    if a == False:
        print(Fore.GREEN+ Style.BRIGHT+ "image Updating" + Fore.WHITE+ Style.NORMAL) 
        a=True
  
    if (time.time() - start_time ) > 0:
        fpsInfo = "FPS: " + str((1.0 / (time.time() - start_time)))[0:2] # FPS = 1 / time to process loop
        font = cv2.FONT_HERSHEY_DUPLEX
        print(end=Style.BRIGHT + f"\r{fpsInfo}" + Fore.WHITE)
        cv2.putText(frame, fpsInfo, (10, 20), font, 0.4, (255, 255, 255), 1)

    # # update webcam1
    if data["Mode"] == "Range":
        frame_to_thresh = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values()
        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))

    if data["Mode"].count("B'n'W"):
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    
    if data["Mode"].count("Pixelated"):
        hh,ww = data["Cam_H"],data["Cam_W"]
        w,h =(130,130)

        result = cv2.resize(frame, (w,h), interpolation=cv2.INTER_AREA)
        frame = cv2.resize(result, (ww,hh), interpolation=cv2.INTER_AREA)

    if data["Mode"].count("Blur"):
        frame = cv2.GaussianBlur(frame,(9,9),99999)

    if data["Mode"] == "Normal" and os.listdir().count(xml):
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    
        face_found = False
        faces = face_cascade.detectMultiScale(gray, 1.1,4)
        
        for (x,y,w,h) in faces:
            if w>0:
                face_found = True
                cv2.rectangle(frame, (x,y), (x+w, y+h), color_green, 2)
                
                #tag
                cv2.putText(frame, 'A Face Detected',(x,y-7), font, 1, color_green)
                cv2.rectangle(frame, (x,y), (x+360,y-37), color_green, 2)
    
    elif event == "shot1":
        if os.listdir().count("images") == False:
            os.mkdir("images")
        if data["Mode"] == "Range":
            cv2.imwrite(f"images/shot{(len(os.listdir('images'))+1)}.png",thresh)
        else:
            cv2.imwrite(f"images/shot{(len(os.listdir('images'))+1)}.png",frame)
    
    if data["Mode"] == "Range": 
        imgbytes = cv2.imencode(".png", thresh)[1].tobytes()
        window["cam1"].update(data=imgbytes)
    else:
        imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        window["cam1"].update(data=imgbytes)
print(end=Style.NORMAL)

cap.release()
cv2.destroyAllWindows()
