import cv2
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt


pixelAverage=0
counter=0
flag=0

#method for sending mail
def email_trigger(number):
    msg = MIMEMultipart()
    msg['Subject'] = 'Human Fall'
    msg['From'] = 'e@mail.cc'
    msg['To'] = 'e@mail.cc'

    messageText = MIMEText("Human Fall")
    msg.attach(messageText)

    serverGmail = smtplib.SMTP('smtp.gmail.com', 587)
    serverGmail.starttls()
    serverGmail.login("human.fall.project", "123ABC++")

    if number == '5':
        serverGmail.sendmail("human.fall.project@gmail.com", "mourey@ualberta.ca", msg.as_string())
        serverGmail.quit()

    ret

#method for creating the graphs
def graph(a,n,b,m):
    plt.plot(a,b ,linewidth=2.0)
    line, = plt.plot(a,b, '-')
    plt.ylabel(n)
    plt.xlabel(m)
    #plt.plot(a,b, 'ro')
    plt.show()
    ret




#method for selecting the backgroud Substractions method
def setBackgroundSubstractionMethod(method):
    frame_number = 0
    if method == 0:
        bgSubtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
        bgs = bgSubtractor
    elif method == 1:
        bgSubtractor = cv2.createBackgroundSubtractorMOG2(96, cv2.THRESH_BINARY, 1)
        bgs = bgSubtractor
    else:
        bgSubtractor = cv2.bgsegm.createBackgroundSubtractorGMG()
        bgs = bgSubtractor
    return  bgs


# Create the background subtraction object
def getBackgroundSubstractionMethod (a):

    if(a>83):
       bgs= setBackgroundSubstractionMethod(1)

    else:
        bgs= setBackgroundSubstractionMethod(2)


    return bgs


#importing the video and finding out the length( numbers of frames) of it
video = cv2.VideoCapture ('C:/Users/mourey/Desktop/project/dataset/Home_01/Videos/video (1).avi')
lengthVideo = int(video.get(cv2.CAP_PROP_FRAME_COUNT))


#defining the blurring image
maskKernel = np.ones((5, 5), np.float32) / 25

# Create the kernel that will be used to remove the noise in the foreground mask
#kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

frameCounter= 0
frameCount=[]
contorCount=[]
theta=[]
ratio=[]
remain_fall=0

while (True):
    frameCounter = frameCounter + 1

    #reading each frames
    ret, frame = video.read ()

    #blurring the frame
    blurFrame = cv2.filter2D(frame, 0, maskKernel)

    #converting into grayscale
    grayFrame = cv2.cvtColor(blurFrame, cv2.COLOR_BGR2GRAY)

    #finding out the average contouring rate of the first frame
    a = np.double(grayFrame)
    a_mean=a.mean()
    pixelAverage= pixelAverage + a_mean
    counter=counter+1


    if(flag==0):
        illumination_room = int(pixelAverage / counter)
        #print(illumination_room)
        bgs=getBackgroundSubstractionMethod(illumination_room)
        #print(bgs)
        flag=1

    #applying the background extraction
    mask = bgs. apply (grayFrame)

    #finding the contouring of the frame to create bounding box
    ret,th1 = cv2.threshold(mask,127,255,cv2.THRESH_BINARY)
    _,contours,hierarchy = cv2.findContours(th1, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)#showing the masked result


    cv2.imshow('background subtraction', mask)

    #for cnt in contours:
    if len(contours) != 0:
        for i in range(len(contours)):
            if len(contours[i]) >= 5:
                #x, y, w, h = cv2.boundingRect(cnt)

                #geting the 4 points of rectangle
                x, y, w, h = cv2.boundingRect(contours[i])

                #getting the point of ellipse
                (center, size, angle) = cv2.fitEllipse(contours[i])
                ellipse = cv2.fitEllipse(contours[i])


                if (w*h>3500):
                    #Creating rectangle and ellipse
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # showing the original video
                    cv2.ellipse(frame, ellipse, (0, 255, 0), 2)
                    #cv2.imshow('frame', frame)

                    #size of ellipse
                    f = int(size[1])

                    #Getting the theta value,ratio and frame number to plot on graph
                    theta.append(round(angle,2))
                    frameCount.append(frameCounter)
                    ratio.append(w/h)
                    contorCount.append(f)

                    #Defining the fall based on angle, ellipse size and ratio
                    if (45<angle< 50) and  (f<=69) or (w / h > 1):
                        remain_fall=remain_fall+1
                        cv2.ellipse(frame, ellipse, (0, 0, 255), 2)

                        print('fall happens in frame number', frameCounter, 'at angle', round(angle, 2))


    cv2.imshow ('frame' , frame)

    #showing the blurred image
    cv2.imshow('dst', blurFrame)

    #showing the grayscale frame
    cv2.imshow('gray', grayFrame)

    if(frameCounter==(lengthVideo - 1)):
        #printing how many frame the person remain fall
        print('remain fall till',remain_fall,'frames')

        #If more than 5 frames he/she remain fall sending mail
        if(remain_fall>=5):
            email_trigger('5')
        numberOfFrame = 'number of frame'
        sizeOfEllipse = 'f'
        angleOfEllipse = 'theta'
        ratioOfBoundingBox = 'ratio'

        #ploting the graphs
        graph(frameCount, numberOfFrame, theta, angleOfEllipse)
        graph(frameCount, numberOfFrame, contorCount, sizeOfEllipse)
        graph(frameCount, numberOfFrame, ratio, ratioOfBoundingBox)

    waitTime = cv2.waitKey(30) & 0xff
    if waitTime == 29:
        break

cv2.destroyAllWindows()
