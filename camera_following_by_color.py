import cv2, time, serial
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np

camera = PiCamera()
camera.resolution = (320,240)
rawCapture = PiRGBArray(camera, size=(320,240))
time.sleep(2)

FOVx = 62.2
B = FOVx / camera.resolution.width
ser = serial.Serial("/dev/ttyACM0",9600)

global angle
angle = 90
ser.write(chr(angle))

drag=False
point1=None
point2=None

selection=False
color_selected = False
h = 0
s = 0
v = 0

def nothing(x):
        pass

def choose_roi(event, x, y, flags, param): # mouse callback
        global drag, point1, point2, selection
        selection = False
        img2= image.copy()

        hsv_mean = np.zeros([1,3])

        if event==cv2.EVENT_LBUTTONDOWN:
                point1=(x,y)
                drag=True
                #print point1
        if event == cv2.EVENT_MOUSEMOVE and drag:
                point2=(x,y)
                #cv2.rectangle(img2, point1, point2, (0,0,255),4)
                #print point2
        if event == cv2.EVENT_LBUTTONUP and drag:
                point2=(x,y)
                cv2.rectangle(img2, point1, point2, (0,0,255),4)
                selection=True
                drag=False
                #print point2
        if selection and not drag:
                print("x1: {} x2: {} y1: {} y2: {}".format(point1[0],point2[0],point1[1],point2[1]))
                cv2.imshow('roi',img2)
                hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
                cv2.imshow('HSV',hsv)

                global h
                global s
                global v
                global color_selected

                for i in range (point1[0],point2[0]):
                       for j in range (point1[1],point2[1]):

                               hsv_current = np.array([hsv[i,j][0],hsv[i,j][1],hsv[i,j][2]])
                               #print("hsv_current: ",hsv_current)
                               hsv_mean += hsv_current
                               #print("hsv_mean total: ",hsv_mean)

                image_size = (abs(point1[0]-point2[0])*abs(point1[1]-point2[1]))

                hsv_mean /= image_size
                #print("hsv_mean: ", hsv_mean)
                h = hsv_mean[0][0]
                s = hsv_mean[0][1]
                v = hsv_mean[0][2]
                color_selected = True
                #print("h: ",h)
                #print("size: ",abs(point1[0]-point2[0])*abs(point1[1]-point2[1]))
                print("h: {} s: {} v: {}".format(h,s,v))

def show_roi(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
                cv2.imshow('roi',image)
                
#Create Image Windows
cv2.namedWindow('image',cv2.WINDOW_NORMAL)
#cv2.namedWindow('image_show',cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('roi',cv2.WINDOW_NORMAL)
cv2.namedWindow('HSV',cv2.WINDOW_NORMAL)

#Create Trackbars
cv2.createTrackbar('Hue_low','image',1,179,nothing)
cv2.createTrackbar('Hue_high','image',2,179,nothing)
cv2.createTrackbar('Saturation_low','image',1,255,nothing)
cv2.createTrackbar('Saturation_high','image',255,255,nothing)
cv2.createTrackbar('Value_low','image',30,255,nothing)
cv2.createTrackbar('Value_high','image',255,255,nothing)
cv2.createTrackbar('kernel_size','image',3,5,nothing)
#Set Trackbars
hue_l=cv2.getTrackbarPos('Hue_low','image')
hue_h=cv2.getTrackbarPos('Hue_high','image')
sat_l=cv2.getTrackbarPos('Saturation_low','image')
sat_h=cv2.getTrackbarPos('Saturation_high','image')
val_l=cv2.getTrackbarPos('Value_low','image')
val_h=cv2.getTrackbarPos('Value_high','image')
kernel_size = cv2.getTrackbarPos('kernel_size','image')

for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    #Read current input image
    image = frame.array

    cv2.imshow('image',image)

    cv2.setMouseCallback('image',choose_roi)
    
    if color_selected:
            hue_l= int(h*0.75)
            cv2.setTrackbarPos('Hue_low','image', hue_l)
            hue_h=int(h*1.25)
            cv2.setTrackbarPos('Hue_high','image' ,hue_h )
            sat_l=int(s*0.75)
            cv2.setTrackbarPos('Saturation_low','image',sat_l )
            sat_h=int(s*1.50)
            cv2.setTrackbarPos('Saturation_high','image', sat_h)
            val_l=int(v*0.75)
            cv2.setTrackbarPos('Value_low','image', val_l)
            val_h=int(v*1.50)
            cv2.setTrackbarPos('Value_high','image', val_h)
            kernel_size = cv2.getTrackbarPos('kernel_size','image')

            color_selected = False

    if kernel_size == 0: kernel_size = 3

    lower_hsv = np.array([hue_l,sat_l,val_l])
    higher_hsv = np.array([hue_h,sat_h,val_h])

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_hsv, higher_hsv)

    rawCapture.truncate(0)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contour_max = 0
    best_contour = None
    cx= 0
    cy= 0
    
    for cnt in contours:
            countour_area = cv2.contourArea(cnt)
            if countour_area > contour_max and countour_area > 100:
                    moments = cv2.moments(cnt)
                    contour_max = countour_area
                    cx = int(moments['m10']/moments['m00'])         # cx = M10/M00
                    cy = int(moments['m01']/moments['m00'])
                    best_contour = cnt
    if best_contour is not None:
            cv2.drawContours(image,[best_contour],0,(0,255,0),1)
            cv2.circle(image,(cx,cy),5,(0,0,255),-1)
            error = cx - camera.resolution.width/2
            
            camera_speed = B * error 
            
            angle = angle + 0.5*camera_speed
            if(angle > 179):
                    angle = 179
            elif(angle < 0):
                    angle = 0
                    
            ser.write(chr(int(angle)))
            #print(angle)
            
    cv2.imshow('out',image)

    if cv2.waitKey(1) & 0xFF == 27: # ESC key
        ser.close()
        break

cv2.destroyAllWindows()
