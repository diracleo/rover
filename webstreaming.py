# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from collections import deque
from flask import Response
from flask import Flask
from flask import render_template
from flask import request
import threading
import argparse
import datetime
import imutils
import time
import cv2
import serial
import math
import json

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__, static_folder="./build/static", template_folder="./build")

# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=9600,
)

ser.isOpen()
	
def feed(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lockf

	greenLower = (6, 130, 130)
	greenUpper = (51, 255, 255)
	frame_width = 400

	# loop over frames from the video stream
	while True:
		f = open('./running.txt', 'r')
		data = {}
		try:
			raw = f.read()
			data = json.loads(raw)
		except Exception:
			data['ai_enabled'] = False
			data['ai_type'] = None
		ai_enabled = data.get('ai_enabled', False)
		if not ai_enabled:
			frame = vs.read()
			frame = imutils.resize(frame, width=frame_width)
			with lock:
				outputFrame = frame.copy()
		else:
			ai_type = data.get('ai_type', None)
			if ai_type == 'motion':
				frame = vs.read()
				frame = imutils.resize(frame, width=frame_width)
			
				blurred = cv2.GaussianBlur(frame, (11, 11), 0)
				hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
				mask = cv2.inRange(hsv, greenLower, greenUpper)
				mask = cv2.erode(mask, None, iterations=2)
				mask = cv2.dilate(mask, None, iterations=2)
				
				cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
				cnts = imutils.grab_contours(cnts)
				center = None
				# only proceed if at least one contour was found
				if len(cnts) > 0:
					# find the largest contour in the mask, then use
					# it to compute the minimum enclosing circle and
					# centroid
					c = max(cnts, key=cv2.contourArea)
					((x, y), radius) = cv2.minEnclosingCircle(c)
					M = cv2.moments(c)
					center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
					# only proceed if the radius meets a minimum size
					if radius > 10 and radius < frame_width / 4:
						# draw the circle and centroid on the frame,
						# then update the list of tracked points
						cv2.circle(frame, (int(x), int(y)), int(radius),
							(0, 255, 255), 2)
						if center[0] > frame_width / 2 - 50 and center[0] < frame_width / 2 + 50:
							power_wheels(200, 200)
						elif center[0] < frame_width / 2 - 50:
							power_wheels(-200, 200)
						elif center[0] > frame_width / 2 + 50:
							power_wheels(200, -200)
					else:
						power_wheels(0, 0)
				else:
					power_wheels(0, 0)
				with lock:
					outputFrame = frame.copy()
	
	
def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

def power_wheels(left, right):
	cmd = str(left) + 'L' + str(right) + 'R'
	ser.write(cmd.encode())
	
@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")
	
@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")
		
@app.route("/command/")
def command():
	cmd = ''
	left = request.args.get("left")
	right = request.args.get("right")
	ret = {}
	ret['left'] = left
	ret['right'] = right
	power_wheels(left, right)
	return ret
	
@app.route("/ai/")
def ai():
	cmd = ''
	enabled = request.args.get("enabled")
	ret = {}
	data = {};
	data['ai_enabled'] = True if enabled == '1' else False
	data['ai_type'] = request.args.get("type")
	f = open('./running.txt', 'w')
	f.write(json.dumps(data))
	f.close()
	ret['ai'] = enabled
	power_wheels(0, 0);
	return ret

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

	# start a thread that will perform motion detection
	t = threading.Thread(target=feed, args=(
		args["frame_count"],))
	t.daemon = True
	t.start()

	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=False,
		threaded=True, use_reloader=False)

# release the video stream pointer
vs.stop()
