'''
Please see the dock
https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/

run cmd :
python webstreaming.py -i 192.168.123.100 -o 8080
'''
# import the necessary packages
# from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from function import countCameras
from flask import Response
from flask import Flask,abort
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2

# count number of camera connected
countCamera = countCameras()
if countCamera <= 0:
	print("Sorry ! , No Camera Found ")
	exit()
	pass


# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = []

lock = threading.Lock()
# initialize a flask object
app = Flask(__name__)
# initialize the video stream and allow the camera sensor to
# warmup
# vs = VideoStream(usePiCamera=1).start()
# vs = VideoStream(src=0).start()
vs = []
for i in range( countCamera ):
	outputFrame.append(None)
	vs.append(VideoStream(src=i).start())
	pass

time.sleep(2.0)

### This is is use to clear the clear Capture

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html", countCamera=countCamera)



width_vdo = 640
height_vdo = 480
def video_rec(camera_id):
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
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

        # timestamp = datetime.datetime.now()
        # cv2.putText(
        #     gray,
        #     "Date-Time : "+timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), 
        #     (10, frame.shape[0] - 10),cv2.FONT_HERSHEY_SIMPLEX, 
        #     0.35, 
        #     (0, 0, 255),
        #     1)

        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()


def detect_motion(frameCount,cameraNumber):


	
	# out = cv2.VideoWriter(file_name,fourcc, 20, (width_vdo,width_vdo))
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock
	# initialize the motion detector and the total number of frames
	# read thus far
	# md = SingleMotionDetector(accumWeight=0.1)
	total = 0
    	# loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		frame = vs[cameraNumber].read()
		frame = imutils.resize(frame, width=400, height=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
		# grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

        # if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		# if total > frameCount:
		# 	# detect motion in the image
		# 	motion = md.detect(gray)
		# 	# check to see if motion was found in the frame
		# 	if motion is not None:
		# 		# unpack the tuple and draw the box surrounding the
		# 		# "motion area" on the output frame
		# 		(thresh, (minX, minY, maxX, maxY)) = motion
		# 		cv2.rectangle(frame, (minX, minY), (maxX, maxY),
		# 			(0, 0, 255), 2)
		
		# update the background model and increment the total number
		# of frames read thus far
		# md.update(gray)
		total += 1
		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame[cameraNumber] = frame.copy()   





def generate(cameraNumber):
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame[cameraNumber] is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame[cameraNumber])
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')


# @app.route("/video_feed")
# def video_feed():
# 	# return the response generated along with the specific media
# 	# type (mime type)
# 	return Response(generate(),
# 		mimetype = "multipart/x-mixed-replace; boundary=frame")


@app.route("/video_feed/<id>")
def video_feed(id):
	camNum = int(id)
	if camNum >= countCamera:
		abort(404)
		return

	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(camNum),
		mimetype = "multipart/x-mixed-replace; boundary=frame")




    # check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())
	
	for cam in range(countCamera):
		# start a thread that will perform motion detection
		

		t = threading.Thread(target=detect_motion, args=(
			args["frame_count"],cam))
		t.daemon = True
		t.start()

		# t2 = threading.Thread(target=video_rec, args=(cam))
		# t2.daemon = True
		# t2.start()
		pass




	
	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)
# release the video stream pointer
for i in range(countCamera):
	vs[i].stop()
	pass
