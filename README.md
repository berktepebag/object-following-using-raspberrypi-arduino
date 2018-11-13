# Follow the object using Raspberry-Pi and Arduino

The camera follows the object according to the color in the chosen ROI. 

### System Setup

* Raspberry-Pi
* Arduino
* Servo motor controlled Raspberry-Pi camera

```python
for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    #Read current input image
    image = frame.array

    cv2.imshow('image',image)

    cv2.setMouseCallback('image',choose_roi)
```

### choose_roi function:
cv2.setMouseCallback is called every time mouse pointer is on the 'image' window. 

hsv_mean array is created to sum all the pixel's HSV values in the selected ROI area. 
```python
def choose_roi(event, x, y, flags, param): # mouse callback
        global drag, point1, point2, selection
        selection = False
        img2= image.copy()

        hsv_mean = np.zeros([1,3])
```

With mouse events, the ROI area is defined to find the color to be followed.

```python
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
Global h,s,v,color_selected (bool) is called to be later filled with values from ROI.
```python
                global h
                global s
                global v
                global color_selected
```

For each pixel in the chosen region HSV values are taken into hsv_current and summed into hsv_mean to be later divided by the ROI area size.
```python
                for i in range (point1[0],point2[0]):
                       for j in range (point1[1],point2[1]):

                               hsv_current = np.array([hsv[i,j][0],hsv[i,j][1],hsv[i,j][2]])
                               #print("hsv_current: ",hsv_current)
                               hsv_mean += hsv_current
                               #print("hsv_mean total: ",hsv_mean)
```

Image size calculated with using points from cv2.setMouseCallback.
```
                image_size = (abs(point1[0]-point2[0])*abs(point1[1]-point2[1]))
```

h,s,v values are separated to be used later in masking the selected HSV values.
```python
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

Each frame captured by the camera, assigned to the image array.

```python
for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    #Read current input image
    image = frame.array

    cv2.imshow('image',image)

    cv2.setMouseCallback('image',choose_roi)
```

#### Setting the lower & higher HSV values to draw the contours and the centroid

After getting values from choose_roi function, set the values to relevant masking filters.

Multipliers are chosen after few trials. Setting a low margine between upper and lower boundaries results system not find any object to be tracked. Setting a high margine causes mismatching.

Trackbars are used to indicate received values from the ROI. 
```
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

```

H,S,V values used to mask image.

```python
   lower_hsv = np.array([hue_l,sat_l,val_l])
   higher_hsv = np.array([hue_h,sat_h,val_h])

   hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
   mask = cv2.inRange(hsv, lower_hsv, higher_hsv)
```

If contour_area fed is larger than current contour_area and larger than 100 pixels, set new "best contour" to this contour. 
```python
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
```

Centroid of the contour can be calculated as above. For more information on contours:
https://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html
```python
                    cx = int(moments['m10']/moments['m00'])         # cx = M10/M00
                    cy = int(moments['m01']/moments['m00'])
                    best_contour = cnt
```

If the best_contour is found, draw contour and centroid of the contour.
```python             
    if best_contour is not None:
            cv2.drawContours(image,[best_contour],0,(0,255,0),1)
            cv2.circle(image,(cx,cy),5,(0,0,255),-1)
```

Error is calculated with the distance from center of the camera to the centroid of the object in x direction. Camera speed is calculated with the formulation below * error.
```python
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
```

FOVx -Horizontal field of view-, is camera specific parameters which can be found here. https://www.raspberrypi.org/documentation/hardware/camera/
```python
FOVx = 62.2
B = FOVx / camera.resolution.width
```


## Calculating the Error

<img width="100" alt="Error" src="/imgs/error1.png">

e = S(p(t)) - S*

S(p(t)) : current value (cx in our case)
S* : Desired value (half width of the camera resolution, in our case)

<img width="100" alt="Error Derivation " src="/imgs/error2.png">

Change in error can be calculated by deriving error over time. 

<img width="100" alt="Counting other vehicles" src="/imgs/error3.png">

Since camera moves only in x-axis we can neglect Ls. Then camera_speed is related with derivation of error (-lambda*error) only.

<img width="100" alt="Counting other vehicles" src="/imgs/exponential.png">
As camera moves to make the object in the center of x-axis, e is at it's maximum value - so the speed of the camera is. As error decreases by time, speed will also decrease exponentially.



  



