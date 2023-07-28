import cv2,os,time,json,datetime
from colorama import Fore,Style
import PySimpleGUI as sg
import requests
if os.listdir().count("haarcascade_frontalface_default.xml") == False:
    URL = "https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/haarcascade_frontalface_default.xml"
    response = requests.get(URL)
    with open('haarcascade_frontalface_default.xml', 'wb') as file:
        file.write(response.content)


title = "Webcam - PySimpleGUI"
xml = "haarcascade_frontalface_default.xml"

if os.listdir().count("config.json") == False:
    open("config.json", "w").write("""{
    "Runtime": true,
    "Cam_W": 640,
    "Cam_H": 480,
    "Theme": "SystemDefaultForReal",
    "Color_R": [25, 25, 230],
    "Color_G": [35, 230, 25]                   
}""")

data = json.load(open("config.json"))


color_green = data["Color_G"]
color_red = data["Color_R"]
font = cv2.FONT_HERSHEY_DUPLEX
sg.theme(data["Theme"])
camera_Width  = data["Cam_W"] # 480 # 640 # 1024 # 1280
camera_Heigth = data["Cam_H"] # 320 # 480 # 780  # 960

face_cascade = cv2.CascadeClassifier(xml)
frameSize = (camera_Width, camera_Heigth)

print(Fore.GREEN+Style.BRIGHT+"Camera Size: " + str((camera_Width, camera_Heigth)) + Fore.WHITE +Style.NORMAL)
print(Fore.GREEN+Style.BRIGHT+"Cascade Classifier: " + str(xml) + Fore.WHITE + Style.NORMAL)

cap = cv2.VideoCapture(0)

menu1 = [[sg.Button("Smile Pls",key="shot1",size=(100,1))],
        [sg.Button("Clear All Shots",key="shot_clear",size=(100,1))]]
# def webcam col
colwebcam1_layout = [[sg.Text("Camera View", size=(60, 1), justification="center")],
                        [sg.Image(filename="", key="cam1")],
                        [sg.Column(menu1,justification="top")]]
colwebcam1 = sg.Column(colwebcam1_layout, element_justification='center')

layout = [[colwebcam1]]

window    = sg.Window(title, layout, 
                      no_titlebar=False, 
                      alpha_channel=1, 
                      location=(100, 100))   
a = False
if data["Runtime"] == True:
    if os.listdir().count("log.txt") == False:open("log.txt", "w")
    g1 = str(len(open("log.txt", "r").read().splitlines())+1)
    g = open("log.txt", "a")
    g.write(datetime.datetime.now().strftime("["+g1+"] Opened on %d/%m/%y %I:%M:%S\n"))
    g.close()
while True:
    start_time = time.time()
    ret, frameOrig = cap.read()
    event, values = window.read(timeout=.20)
    
    if event == "shot1":
        if os.listdir().count("images") == False:
            os.mkdir("images")
        cv2.imwrite(f"images/shot{(len(os.listdir('images'))+1)}.png",frameOrig)
    elif event == "shot_clear":
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
        print(Fore.RED + Style.BRIGHT +  f'\n"{title}" has been closed' + Fore.WHITE +Style.NORMAL)
        break

    # get camera frame

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
    imgbytes = cv2.imencode(".png", frame)[1].tobytes()
    window["cam1"].update(data=imgbytes)
print(end=Style.NORMAL)

cap.release()
cv2.destroyAllWindows()