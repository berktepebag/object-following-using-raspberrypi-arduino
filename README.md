# Follow the object using Raspberry-Pi and Arduino

The camera follows the object according to the color in the chosen ROI. 

### System Setup

* Raspberry-Pi
* Arduino
* Servo motor controlled Raspberry-Pi camera

```
for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    #Read current input image
    image = frame.array

    cv2.imshow('image',image)

    cv2.setMouseCallback('image',choose_roi)
```

cv2.setMouseCallback is called every time mouse pointer is on the 'image' window. 

```
def choose_roi(event, x, y, flags, param): # mouse callback
        global drag, point1, point2, selection
        selection = False
        img2= image.copy()

        hsv_mean = np.zeros([1,3])
```

hsv_mean array is created to sum all the pixel's HSV values in the ROI. 

```
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
```

With mouse events, the region is defined to be used to find the color to be followed.

```
                global h
                global s
                global v
                global color_selected
```

global h,s,v,color_selected (bool) is defined to be later filled with values from ROI.

``` 
                for i in range (point1[0],point2[0]):
                       for j in range (point1[1],point2[1]):

                               hsv_current = np.array([hsv[i,j][0],hsv[i,j][1],hsv[i,j][2]])
                               #print("hsv_current: ",hsv_current)
                               hsv_mean += hsv_current
                               #print("hsv_mean total: ",hsv_mean)
```

for each pixel in the chosen region HSV values are taken into hsv_current and summed into hsv_mean to be later divided by the ROI size.

```
                image_size = (abs(point1[0]-point2[0])*abs(point1[1]-point2[1]))
```

Image size calculated with using points from cv2.setMouseCallback.

```
                hsv_mean /= image_size
                #print("hsv_mean: ", hsv_mean)
                h = hsv_mean[0][0]
                s = hsv_mean[0][1]
                v = hsv_mean[0][2]
                color_selected = True
                #print("h: ",h)
                #print("size: ",abs(point1[0]-point2[0])*abs(point1[1]-point2[1]))
                print("h: {} s: {} v: {}".format(h,s,v))
```

h,s,v values are separated to be used later in masking the selected HSV values.

 






