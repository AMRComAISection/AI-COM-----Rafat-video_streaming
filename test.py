import cv2
import numpy as np
import datetime
import threading,logging,time


def clearCapture(capture):
    capture.release()
    cv2.destroyAllWindows()

def countCameras():
    n = 0
    number_of_ittration = 100
    for i in range(number_of_ittration):
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            n = i
            cap.release()
            cv2.destroyAllWindows()
            break
    
        cap.release()
        cv2.destroyAllWindows()

    return n

def thread_function(camera_id):
    cap = cv2.VideoCapture(camera_id)
    # cap = all_camera[camera_id]
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    file_name = str(camera_id)+".avi"
    width = 640
    height = 480
    if cap.isOpened(): 
        width  = int(cap.get(3)) # float
        height = int(cap.get(4)) # float
        print (width,height)

    out = cv2.VideoWriter(file_name,fourcc, 20, (width,height))
    # cap.set(cv2.cv2.CV_CAP_PROP_FPS, 60)
    while(cap.isOpened()):
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

        timestamp = datetime.datetime.now()
        cv2.putText(
            gray,
            "Date-Time : "+timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), 
            (10, frame.shape[0] - 10),cv2.FONT_HERSHEY_SIMPLEX, 
            0.35, 
            (0, 0, 255),
            1)

        out.write(frame)

        # cv2.imshow(file_name,gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    
    for i in range(countCameras()) :
        x = threading.Thread(target=thread_function, args=(i,))
        x.start()
    pass
