'''
切除每一帧中标出的框，并且以框的大小切其他部门生成负样本
'''
import cv2
import sys
import os
import random
from PIL import Image
import numpy as np

# Mouse response function
def getPosition(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global x1, y1, x2, y2, clickCount
        if (clickCount == 0):
            x1, y1 = x, y
            clickCount = clickCount + 1
            cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)
            return
        if (clickCount == 1):
            x2, y2 = x, y
            clickCount = clickCount + 1
            return

def cutPic(filename, savePath,x0, y0, dx, dy,num):
    img = Image.open(filename)
    imgArr = np.array(img)
    newImgArr_1 = []
    for xi in range(dx):
        x = x0+xi
        newImgArr_1.append(imgArr[x,:,:])
    newImgArr_1 = np.array(newImgArr_1)
    newImgArr_2 = []
    for yi in range(dy):
        y = y0+yi
        newImgArr_2.append(newImgArr_1[:,y,:])
    m, n , k = np.shape(newImgArr_2)
    newImgArr = np.zeros([n,m]).tolist()
    for i in range(m):
        for j in range(n):
            newImgArr[j][i] = newImgArr_2[i][j]
    newImgArr = np.array(newImgArr)
    newImg = Image.fromarray(newImgArr)
    newImg.save(savePath+str(num)+'.jpg')
    # newImg.show()

if __name__ == '__main__':

    # Set up tracker.
    # Instead of MIL, you can also use
    tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']

    # tracker_type = tracker_types[2]
    tracker_type = tracker_types[0]
    tracker = cv2.TrackerBoosting_create()

    # Read video
    video = cv2.VideoCapture("./test.mp4")

    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video")
        sys.exit()

    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print('Cannot read video file')
        sys.exit()

    # init global variable
    clickCount = 0
    x1, y1, x2, y2 = -1, -1, -1, -1

    # show the first frame of the video
    cv2.namedWindow("first frame")

    # add mouse response function to window
    cv2.setMouseCallback('first frame', getPosition)

    imageNum = 0
    #print(cv2.getWindowProperty(frame))
    while (clickCount < 2):
        cv2.imshow("first frame", frame)
        cv2.setMouseCallback('first frame', getPosition)
        k = cv2.waitKey(1) & 0xff
        if k == 27: break

    cv2.destroyWindow('first frame')

    # Define an initial bounding box
    bbox = (x1, y1, abs(x2 - x1), abs(y2 - y1))
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    # Uncomment the line below to select a different bounding box
    # bbox = cv2.selectROI(frame, False)

    # Initialize tracker with first frame and bounding box
    ok = tracker.init(frame, bbox)

    # make sure the folder exists

    file = './output3'
    if not (os.path.exists(file)):
        os.mkdir(file)
    
    file = './output3/positiveSimples'
    if not (os.path.exists(file)):
        os.mkdir(file)

    file = './output3/negativeSimples'
    if not (os.path.exists(file)):
        os.mkdir(file)

    #负样本输出计数
    outputCounts = 0

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        # Start timer
        timer = cv2.getTickCount()

        # Update tracker
        ok, bbox = tracker.update(frame)

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        ## initialize positive and negative sample frame
        positiveFrame = None
        negativeFrame = None
        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))  # left-top
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1]))  # right-top
            p3 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))  # right-bottom
            p4 = (int(bbox[0]), int(bbox[1] + bbox[3]))  # left-bottom
            

            positiveFrame = frame[p1[1]:p3[1],p1[0]:p3[0]]

            # draw the box
            cv2.rectangle(frame, p1, p3, (255, 0, 0), 2, 1)

        else:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        # Display result
        cv2.imshow("Tracking", frame)

        file = "./output3/positiveSimples"
        nfile = "./output3/negativeSimples"
        # if not (os.path.exists(file)):
        #     os.mkdir(file)

        cv2.imwrite((file+'/{}.jpg').format(imageNum), positiveFrame)

        # cutPic((file+'/'+str(i)+'.jpg'),(file+'/'),x1,y1,width,height,i)

        tryTimes = 0
        while(tryTimes<15 and outputCounts<=200):
            x_random = random.randint(0, abs(frame.shape[1]-bbox[2]))
            y_random = random.randint(0, abs(frame.shape[0]-bbox[3]))
            if not(abs(x_random - p1[0]) < bbox[2] and abs(y_random - p1[1]) < bbox[3]):
                negativeFrame = frame[y_random:int(y_random+bbox[3]),
                                      x_random:int(x_random+bbox[2])]

                cv2.imwrite((nfile+'/{}.jpg').format(outputCounts), negativeFrame)
                outputCounts += 1
                break
            tryTimes += 1


        # cv2.imwrite('output1/{}.jpg'.format(i), frame)
        imageNum += 1

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

