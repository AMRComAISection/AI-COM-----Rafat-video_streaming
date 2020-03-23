import cv2
import numpy as np

def clearCapture(capture):
    capture.release()
    cv2.destroyAllWindows()


### Get the number of Cameras Connected in computer
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
