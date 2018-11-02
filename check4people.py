import threading
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import StringIO
import time
import traceback
from threading import Thread
import cv2
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np


DEBUG=1
IMAGE_WIDTH=1024
IMAGE_HEIGHT = 768

PORT = 80
bounding = []


class CamHandler:
	def __init__(self):
		DEVICE = '/dev/video0'
		self.SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
		self.camera = cv2.VideoCapture(0)

        def get_camera_image(self):
		(ret,img) = self.camera.read()
                return img


class HttpHandler(BaseHTTPRequestHandler):
	def __init__(self, *args):
		self.bounding = []
                self.cas1 = cv2.CascadeClassifier('erwan.xml')
		self.cas2 = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
		self.cas3 = cv2.CascadeClassifier('haarcascade_profileface.xml')
		self.cas4 = cv2.CascadeClassifier('haarcascade_upperbody.xml')
		self.cas=[self.cas1,self.cas2,self.cas3,self.cas4]

                self.camera = camera

		BaseHTTPRequestHandler.__init__(self, *args)



	def runIndex(self):
		 self.send_response(200)
                 self.send_header('Content-type','text/html')
                 self.end_headers()
                 self.wfile.write('<html><head></head><body>')
                 self.wfile.write('<img src="/cam.mjpg"/>')
                 self.wfile.write('</body></html>')

	def runMjpgThread(self,image):
		rects=[]
		i=0
		for cas in self.cas:
			rect = cas.detectMultiScale(image, 1.3,5)
			if len(rect)>0:
				print "---> Cas %i found bb" % i
			i+=1
			for r in rect:
				rects.append(r)

 		rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
                self.bounding = non_max_suppression(rects, probs=None, overlapThresh=0.65)




	def runMjpg(self):
		print "*********** Running MJPG"
		self.send_response(200)
                self.send_header('Content-type','multipart/x-mixed-replace; boundary=--myboundary')
                self.end_headers()
                o = self.wfile
                frame=0
		result=[]
		t = None
		self.cas1 = cv2.CascadeClassifier('erwan.xml')

                try:
                	while True:
                        	image = self.camera.get_camera_image()
				if frame==0 or (frame % 15 == 14 and t!=None and not t.isAlive()):
					t = threading.Thread(target=self.runMjpgThread,args=(image,))
					t.start()
				#self.runMjpgThread(image)
				for (xA, yA, xB, yB) in self.bounding:
		                        cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
				data = cv2.imencode('.jpg', image)[1].tostring()
                                o.write( "--myboundary\r\n" )
                                o.write( "Content-Type: image/jpeg\r\n" )
                                o.write( "Content-Length: %s\r\n" % str(len(data)))
                                o.write( "\r\n" )
                                o.write(data)
                                o.write( "\r\n" )
                                time.sleep(0.05)
                                frame+=1
		except Exception as e:
                	print e

	def run404(self):
		self.send_response(404)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write('<html><head></head><body>')
                self.wfile.write('404 : Not Found')
                self.wfile.write('</body></html>')

	def do_GET(self):
		try:

			if self.path.endswith('index.html'):
				self.runIndex()
				return

			if self.path.endswith('cam.mjpg'):
				self.runMjpg()
				return

			self.run404()

		except Exception as e:
			print e

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():
	global camera 
	camera= CamHandler()
	try:
		server = ThreadedHTTPServer(('0.0.0.0', PORT), HttpHandler)
		print "server started"
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()

if __name__ == '__main__':
	main()




