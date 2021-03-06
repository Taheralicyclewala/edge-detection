import numpy as np
import cv2
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from scipy import signal
from PIL import ImageFilter
from skimage import feature


np.set_printoptions(threshold=np.nan)
#filt runs a filter on the image and returns array of endpoints
#argument is the image
def filt(image):
	gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	#blur = cv2.bilateralFilter(gray,9,80,80) ###may need to blur the image to get rid of noise

	edges = findSigma(gray)
	edges = edges.astype('uint8')
	
	#plt.imshow(edges, 'Greys')
	#plt.show()

	#######hough lines#############
	minLine = 1000
	maxGap = 100

	segs = cv2.HoughLinesP(edges,8,np.pi/180,100,minLine,maxGap,75)
	return segs

def angle_between(p1, p2):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return np.rad2deg((ang1 - ang2) % (2 * np.pi))

#segfinds will make sure lines are desired length
#argument is the array of endpoints and the image
def segFind(segs,image):

	minSeg = (len(image)+len(image[0]))/100 ###this is the minimum line segment based on size of image
	
	###distance formula to find long-ish segments####
	i=-1
	for x1,y1,x2,y2 in segs[0]:
		i=i+1
		dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)

		#random tolerance for now... seems to produce good segments
		if dist<minSeg:
			segs[0,i]=0

	return segs

#this function finds a suitable sigma (tolerance) for the canny edge detector
#argument is the image
def findSigma(image):
	sig = 3.5
	total = len(image)*len(image[0])
	flag = True
	cnt = 0
	while(flag):
		cnt = cnt+1
		edges = feature.canny(image, sigma=sig)
		edSum = np.sum(edges)
		tmp = total/edSum
		#print tmp

		###if there are too many pixels, increase sig
		if tmp<200:
			sig = sig + .13
		###too few pixels, decr sig
		if tmp>401:
			sig = sig - .13
		elif tmp>200 and tmp <401:
			return edges

		##sometimes any sigma we put in will be incorct so we let feature decide after some trying
		elif cnt>10 and tmp == 0:
			edges = feature.canny(image)
			return edges

#this draws the line segments on the image
#arguments are the image and the array of line segment endpoints
def draw(image,segs):
	for x1,y1,x2,y2 in segs[0]:
		cv2.line(image,(x1,y1),(x2,y2),(255,0,0),10)
	return image

def profile(segs,imNum):

	segs = segs[0,:,:]

	objs = []

	for i in range(len(segs)):
		objs.append(Segment(segs[1],imNum))

		##calc length of seg
		dist = np.sqrt((segs[i,2]-segs[i,0])**2 + (segs[i,3]-segs[i,1])**2)
		objs[i].setDistance(dist)

		##Angle ###this doesnt work yet
		ang = angle_between((segs[i,0],segs[i,1]),(segs[i,2],segs[i,3]))
		print ang




def main():
	image = cv2.imread('corner.jpg')
	segs =segFind(filt(image),image)
	im1 = draw(image,segs)
	profile(segs,1)

	image = cv2.imread('scoot1.jpg')
	segs =segFind(filt(image),image)
	im2 = draw(image,segs)
	profile(segs,2)

	fig = plt.figure()
	a = fig.add_subplot(1,2,1)
	im1plot = plt.imshow(im1)
	a = fig.add_subplot(1,2,2)
	im2plot = plt.imshow(im2)

	plt.show()

	

	#profile(segs,image)

class Segment:
	def __init__(self,points,Num):
		self.points=points
		self.Num = Num

	def setColor(self, color):
		self.color = color

	def setAng(self,ang):
		self.ang = ang

	def setDistance(self,dist):
		self.dist = dist


main()
