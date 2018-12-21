'''
切除每一帧不带框的图片,并保存每一帧框的四个点坐标
'''
import cv2
import sys
import os


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
    cv2.namedWindow("first frame",0)

    # add mouse response function to window
    cv2.setMouseCallback('first frame', getPosition)

    # resize the window
    cv2.resizeWindow('first frame', 1000, 1000)

    i = 0

    while (clickCount < 2):
        cv2.imshow("first frame", frame)
        cv2.setMouseCallback('first frame', getPosition)
        k = cv2.waitKey(1) & 0xff
        if k == 27: break

    cv2.destroyWindow('first frame')

    # Define an initial bounding box
    bbox = (x1, y1, abs(x2 - x1), abs(y2 - y1))

    # Uncomment the line below to select a different bounding box
    # bbox = cv2.selectROI(frame, False)

    # Initialize tracker with first frame and bounding box
    ok = tracker.init(frame, bbox)

    # make sure the folder exists
    file = "./output2"
    if not (os.path.exists(file)):
        os.mkdir(file)

    file = "./output2/picturePerFrame"
    if not (os.path.exists(file)):
        os.mkdir(file)

    # open local file
    fo = open("./output2/output.txt", "w")

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

        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))  # left-top
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1]))  # right-top
            p3 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))  # right-bottom
            p4 = (int(bbox[0]), int(bbox[1] + bbox[3]))  # left-bottom

            # save the position of the box
            fo.write(
                str(p1[0]) + "," + str(p1[1]) + "\t" + str(p2[0]) + "," + str(p2[1]) + "\t" + str(p3[0]) + "," + str(
                    p3[1]) + "\t" + str(p4[0]) + "," + str(p4[1]) + "\n")
        else:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        # Display result
        cv2.namedWindow('Tracking', 0)
        cv2.resizeWindow('Tracking', 1000, 1000)
        cv2.imshow("Tracking", frame)
        cv2.imwrite('output2/picturePerFrame/{}.jpg'.format(i), frame)
        i += 1

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            fo.close()
            break

    fo.close()
