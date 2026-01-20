# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
import io
from picamera2 import Picamera2
from flask import Response
from flask import Flask
from flask import render_template
from flask import request
import threading
import argparse
import time
import cv2
import serial

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
#outputFrame = None
#lock = threading.Lock()

# initialize a flask object
app = Flask(__name__, static_folder="./build/static", template_folder="./build")

# initialize the video stream and allow the camera sensor to
# warmup
"""
vs = VideoStream(usePiCamera=True, resolution=(640, 480), framerate=32).start()
#vs = VideoStream(src=0).start()
time.sleep(2.0)
ser = serial.Serial(
    port='/dev/serial0',
    baudrate=9600,
)
ser.isOpen()
"""

picam2 = Picamera2()
# Configure the camera for video
camera_config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(camera_config)
picam2.set_controls({"FrameRate": 20, "NoiseReductionMode": 1})
picam2.start()

def generate_frames():
    while True:
        # Capture the frame
        frame = picam2.capture_array()
        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def power_wheels(drive, steer):
	#cmd = str(drive) + 'L' + str(steer) + 'R'
	#ser.write(cmd.encode())
	pass
	
@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")
	
@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
		
@app.route("/command/")
def command():
	cmd = ''
	drive = request.args.get("drive")
	steer = request.args.get("steer")
	ret = {}
	ret['drive'] = drive
	ret['steer'] = steer
	power_wheels(drive, steer)
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

	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=False,
		threaded=True, use_reloader=False)
