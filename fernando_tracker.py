 #!/usr/bin/python

import numpy as np
import cv2, csv, os, re, sys, time, argparse, datetime

'''
this script started long ago as differenceImageGravel.py. It's since gone through various incarnations.

The goal now (4 Nov 2015) is to modify the script to meet fernado's needs for his cichlid study

important: the long side of the tank must be perpendicular to the camera view


#### some challenges #######
## to do this in real time, we can't use a background image that we've generated using cv2.accumulateWeighted
## what we CAN do is to use the first frame as our background image and as the program continues to get new frames,
## we can add these to cv2.accumulateWeighted until we get to some frame number, where this image then becomes the background image
## we can refresh the background image by incorporting new images into cv2.accumulatedWeighted as the program progresses

### to do:
## I've noticed that when the fish is on top of the black thing in the middle of the tank, its difference image shows up as green
## so, in the future: when you can't find the fish, only look for green regions of the tank and see if you can find the fish then
## also to do: in boundingRect, make it so that the rectangle does not have to be parrallel to the bottom of the screen

help menu:  python fernando_tracker.py --help
arguments:
--pathToVideo or -i : full or relative path to video file or input number.
--videoName or -n: used to save files associated with the trial. required
--fps or -f: frames per second

example of useage: python fernando_tracker.py -i /Volumes/NEXT/Video\ 5.mp4 -n video5

'''
print time.strftime('%X %x %Z')

# initialize some constants, lists, csv writer
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--pathToVideo", help = "integer that represents either the relative or full path to the video you want to analyze",nargs='?',default=0)
ap.add_argument("-n", "--videoName", help = "name of the video to be saved",required=True)
ap.add_argument("-f", "--fps", help = "frames per second of the video")

args = ap.parse_args()

# print arguments to the screen
print("\n\n\tinput path: {}".format(args.pathToVideo))
print("\tname of trial: {}".format(args.videoName))
if args.fps is not None:
	print("\tfps of video: {}".format(args.fps))

args = vars(ap.parse_args())

fps = args["fps"]

# calculate the time that the program should start the main loop
start_time = time.time()

counter = 0

# create new folder if it doesn't exist
name = args["videoName"]
if not os.path.exists(name):
    os.makedirs(name)

# output to csv file where the results will be written
print "name of csv file: " + str(name) + ".csv"
myfile = open(name + "/" + name+".csv",'wb')
csv_writer = csv.writer(myfile, quoting=csv.QUOTE_NONE)
csv_writer.writerow(("x","y","frame"))

# for drawing the rectangle around the tank at the beginning of the trial
drawing = False # true if mouse is pressed
ix,iy = -1,-1

# print python version
print "python version:\n"
print sys.version

######################
# declare some functions:####
#####################################

def printUsefulStuff(listOfSides,fps):
	fps = int(fps)
	# print realized fps for the trial
	print "\ntotal frames: " + str(len(listOfSides))

	# now subset the list of sides into four parts. each will be a quarter of the total length of the list
	# there is probably a better way to do this, but I don't know what it is
	leftPart1 = listOfSides[0:int(len(listOfSides)*0.2381)].count("left")
	rightPart1 = listOfSides[0:int(len(listOfSides)*0.2381)].count("right")
	neutralPart1 = listOfSides[0:int(len(listOfSides)*0.2381)].count("neutral")

	# stimuli here
	leftPart2 = listOfSides[int(len(listOfSides)*0.2381):int(len(listOfSides)*0.4762)].count("left")
	rightPart2 = listOfSides[int(len(listOfSides)*0.2381):int(len(listOfSides)*0.4762)].count("right")
	neutralPart2 = listOfSides[int(len(listOfSides)*0.2381):int(len(listOfSides)*0.4762)].count("neutral")

	# stimuli here
	leftPart3 = listOfSides[int(len(listOfSides)*0.5238):int(len(listOfSides)*0.7619)].count("left")
	rightPart3 = listOfSides[int(len(listOfSides)*0.5238):int(len(listOfSides)*0.7619)].count("right")
	neutralPart3 = listOfSides[int(len(listOfSides)*0.5238):int(len(listOfSides)*0.7619)].count("neutral")

	leftPart4 = listOfSides[int(len(listOfSides)*0.7619):len(listOfSides)].count("left")
	rightPart4 = listOfSides[int(len(listOfSides)*0.7619):len(listOfSides)].count("right")
	neutralPart4 = listOfSides[int(len(listOfSides)*0.7619):len(listOfSides)].count("neutral")

	# print association time stats to the screen for each part
	print "------------------------------\n\n\n\n\n\n\nassociation time statistics for each part of the trial:"
	print "\n\npart 1:\nframes 0 - " + str(int(len(listOfSides)*0.2381))
	print "seconds left: " + str(leftPart1/fps)
	print "seconds right: " + str(rightPart1/fps)
	print "seconds neutral: " + str(neutralPart1/fps) + "\n"

	# print association time stats to the screen for each part
	print "\n\npart 2:\nframes " + str(int(len(listOfSides)*0.2381)) + " - " + str(int(len(listOfSides)*0.4762))
	print "seconds left: " + str(leftPart2/fps)
	print "seconds right: " + str(rightPart2/fps)
	print "seconds neutral: " + str(neutralPart2/fps) + "\n"

	# print association time stats to the screen for each part
	print "\n\npart 3:\nframes " + str(int(len(listOfSides)*0.5238)) + " - " + str(int(len(listOfSides)*0.7619))
	print "seconds left: " + str(leftPart3/fps)
	print "seconds right: " + str(rightPart3/fps)
	print "seconds neutral: " + str(neutralPart3/fps) + "\n"

	# print association time stats to the screen for each part
	print "\n\npart 4:\n" + str(int(len(listOfSides)*0.7619)) + " - " + str(int(len(listOfSides)))
	print "seconds left: " + str(leftPart4/fps)
	print "seconds right: " + str(rightPart4/fps)
	print "seconds neutral: " + str(neutralPart4/fps) + "\n"

	# check for time spend in the neutral zone
	print "\nchecking for to see whether the fish spend > 50% of the trial in the neutral part of the tank:\n"

	time_neutral = int((neutralPart2+neutralPart3)/fps)

	print "time in neutral zone during parts 2 and 3: " + str(time_neutral)
	if time_neutral > 300:
		print "female spent more than half the time in the neutral zone. RETEST FEMALE."

# set up video writer to save the video
def setupVideoWriter(width, height,videoName):
	# Define the codec and create VideoWriter object
	fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
	videoName = os.getcwd() + '/' + name + "/" + videoName + ".avi"
	out = cv2.VideoWriter(videoName,fourcc, 5.0, (int(width),int(height)))
	return out, videoName

# converts a frame to HSV, blurs it, masks it to only get the tank by itself
## TO DO: get rid of tank bounds as global variables, include as arguments to this function
def convertToHSV(frame):
	# blur image to make color uniform
	blurred = cv2.blur(frame,(7,7))
	# conver to hsv
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	# apply mask to get rid of stuff outside the tank
	mask = np.zeros((camHeight, camWidth, 3),np.uint8)
	# use rectangle bounds for masking
	mask[top_bound:lower_bound,left_bound:right_bound] = hsv[top_bound:lower_bound,left_bound:right_bound]
	#cv2.imwrite(name + "/mask.jpg",mask)
	return mask


# returns centroid from largest contour from a binary image
@profile
def returnLargeContour(frame,totalVideoPixels):
	potential_centroids = []

	# find all contours in the frame
	contours = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[0]
	print "number of contours: " + str(len(contours)) + "\n"

	for z in contours:
		# calculate some things
		area = cv2.contourArea(z)
		x,y,w,h = cv2.boundingRect(z)
		aspect_ratio = float(w)/h

		##### the main filtering statement:
		# the problem with use absolute values for the size cutoffs is that this will vary with the dimensions of the camera
		# I originally found that including blobs within the range (150, 2000) worked well for videos that were 1280x780
		# thus the fish took up ~0.016776% to ~0.21701% of the total available pixels (921,600)
		# based on that, I should be able to apply those percents to any video resolution and get good results
		if area > (totalVideoPixels*0.00010) and area < (totalVideoPixels*0.0022) and aspect_ratio <= 4 and aspect_ratio >= 0.25:
			potential_centroids.append(z)
			print "area: " + str(area) + "; aspect_ratio: " + str(aspect_ratio)

	largestCon = sorted(potential_centroids, key = cv2.contourArea, reverse = True)[:1]
	print str(len(largestCon)) + " largest contours"

	if len(potential_centroids) == 0:
		csv_writer.writerow(("NA","NA",counter))
		return(None)
	else:
		for j in largestCon:
			m = cv2.moments(j)
			centroid_x = int(m['m10']/m['m00'])
			centroid_y = int(m['m01']/m['m00'])
			csv_writer.writerow((centroid_x,centroid_y,counter))
			return((centroid_x,centroid_y))

# gets background image when the input is a video file
def getBackgroundImage(vid,numFrames):
	print "\n\n\n\n-----------------------\n\ninitializing background detection\n"

	# set a counter
	i = 0
	_,frame = vid.read()
	# initialize an empty array the same size of the pic to update
	update = np.float32(frame)

	# loop through the first numFrames frames to get the background image
	while i < numFrames:
		# grab a frame
		_,frame = vid.read()

		# main function
		cv2.accumulateWeighted(frame,update,0.001)
		final = cv2.convertScaleAbs(update)
		# increment the counter
		i += 1

	# print something every 100 frames so the user knows the gears are grinding
		if i%100 == 0:
			print "detecting background -- on frame " + str(i) + " of " + str(numFrames)

	return final

# adds frame to the background image called old_background_image, returns updated image
def addToBackgroundImage(frame,old_background_image):
	cv2.accumulateWeighted(frame,old_background_image,0.001)
	final = cv2.convertScaleAbs(update)
	return final


def find_tank_bounds(image,name_of_trial):

	# blur the image a lot
	blur = cv2.blur(image, (15,15))
	# convert to hsv
	hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
	# get only the whitish parts
	mask = cv2.inRange(hsv,np.array([10,0,0]),np.array([70,75,200]))

	# find all contours in the frame
	contours = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[0]
	# find largest contour
	largestCon = sorted(contours, key = cv2.contourArea, reverse = True)[:1]
	for j in largestCon:
		# to be a bit more precise, we use minAreaRect instead of boundingRect
		#x,y,w,h = cv2.boundingRect(j)
		rect = cv2.minAreaRect(j)
		coords, dim, angle = rect
		x, y = coords
		w, h = dim
		# note that these measurements assume the long edge of the bottom of the tank is parrallel with the bottom edge of the video feed
		print "x, y, w, h, angle:"
		print x, y, w, h, angle

		# to get actual bounds of the rectange, accounting for the fact that it might be tilted slightly
		box = cv2.cv.BoxPoints(rect)
		# convert to integers
		box = tuple([ (int(x),int(y)) for x,y in box])

		# declare the tank bounds globally
		global top_bound, left_bound, right_bound, lower_bound
		### 17 Nov 2015
		# given what fernando's tank looks like and the fact the tank's position in the video screen shouldn't change a whole lot, I'm just going to hard-code these values. If you want to go back to have the tank bounds determined programatically, uncomment the line below:
		top_bound, left_bound, right_bound, lower_bound = 250, 200, 1100, 525
		#top_bound, left_bound, right_bound, lower_bound = box[1][1], box[1][0], box[3][0], box[3][1]
		print "rectangle bounds: "
		print top_bound, left_bound, right_bound, lower_bound

		# save a photo of the tank bounds for reference:
		# first make a copy of the image
		image_copy = image.copy()

		#box = np.int0(box)
		#cv2.drawContours(image_copy,[box],0,(0,255,255),10)
		cv2.rectangle(image_copy,(left_bound, top_bound),(right_bound,lower_bound),(0,255,255),10)
		cv2.imwrite(name + "/" + str(name_of_trial) + "_tank_bounds.jpg", image_copy)


		# save tank bound coordinates to a file for parsing later if need be
		coord_file = open(name + "/" + str(name_of_trial) + "_tank_bounds.txt", "w")
		coord_file.write("top bound: " + str(top_bound) + "\n" + "left bound: " + str(left_bound) + "\n" + "right bound: " + str(right_bound) + "\n" + "lower bound: " + str(lower_bound) + "\n")
		coord_file.close()


#########################
## end function declarations ####
###################################################

path = args["pathToVideo"]

# set up the video capture to the video that was the argument to the script, get feed dimensions
# if it's not a file but a webcam feed, change the path variable to an int
try:
	path = int(path)
	live = True, True
	print "live video detected"
except:
	pass
	live, write_video = False, False
	print "looks like we're reading from a file"

cap = cv2.VideoCapture(path)
global camWidth, camHeight # for masking
camWidth, camHeight = cap.get(3), cap.get(4)
print "\n\nvideo dimensions: " + str(camWidth) + " x " + str(camHeight)

if live == False:
	# grab the 20th frame for drawing the rectangle
	i = 0
	while i <20:
		ret,frame = cap.read()
		i += 1
	print "grabbed first frame? " + str(ret)
	background = getBackgroundImage(cap,2000)

elif live == True:
	# if live, we take the background image to be the first image we capture
	ret, background = cap.read()
	if ret == False:
		print "could not read frame from the webcam"
		sys.exit(1)

if write_video == True:
	out, _ = setupVideoWriter(camWidth, camHeight, name)


# find the bounds of the tank:
find_tank_bounds(background,name)

# convert background to HSV and save a copy of the background image for reference
hsv_initial = convertToHSV(background)
cv2.imwrite(name + "/" + name + "_background.jpg", background)
cv2.imwrite(name + "/" + name + "_background_hsv.jpg", hsv_initial)

# keep a list of coordinates of the fish.
# the idea is, for the purposes of this code, if we can't ID the fish we assume it's stopped
# the csv file we save will have NAs for these frames instead
# in R, I then go back and interpolate the missing frames
# it would be nice to have a python function at the end of this script that would do that for me, actually

# initiating with the center of the tank in case tracker can't find fish initially
# also set up left of 'left' 'right' or 'neutral' zone
center1 =((right_bound-left_bound)/2)+left_bound
center2 = ((lower_bound-top_bound)/2)+top_bound
coordinates = [(center1,center2)]
zone = []

# set association zone bounds
zoneSize = int((right_bound-left_bound) / 3)
leftBound = left_bound + zoneSize
rightBound = left_bound + (2*zoneSize)

print "left bound: " + str(leftBound)
print "right bound: " + str(rightBound)

# set up video writer specifying size (MUST be same size as input) and name (command line argument)
#videoWriter, pathToVideo = setupVideoWriter(camWidth, camHeight,name)


startOfTrial = time.time()
cap = cv2.VideoCapture(path)
###########################
### the main loop######
###################
while(cap.isOpened()):

	print "frame " + str(counter) + "\n\n"

	# for timing, maintaining constant fps
	beginningOfLoop = time.time()

	# read in the frame
	ret,frame = cap.read()

	# maybe do a try statement here?
	if ret == False:
		print "didn't read frame from video file"
		break

	# do image manipulations for tracking
	hsv = convertToHSV(frame)
	difference = cv2.subtract(hsv_initial,hsv)
	masked = cv2.inRange(difference,np.array([0,0,0]),np.array([255,255,10]))
	maskedInvert = cv2.bitwise_not(masked)

	# find the centroid of the largest blob
	center = returnLargeContour(maskedInvert, camWidth*camHeight)

	# if the fish wasn't ID'ed by the tracker, assume it's stopped moving
	if not center:
		coordinates.append(coordinates[-1])
	# otherwise add the coordinate to the growing list
	else:
		coordinates.append(center)

	print "coordinates: " + str(coordinates[-1])

	# find what association zone the fish is in:
	if coordinates[-1][0] < leftBound:
		zone.append("left")
	elif coordinates[-1][0] > rightBound:
		zone.append("right")
	else:
		zone.append("neutral")


	print "Center: " + str(center) + "\n"

	# save the frame before drawing on it
	if write_video == False:
		cv2.imwrite(name + "/" + '%08d' % counter + ".jpg", frame)
	elif write_video == True:
		out.write(frame)

	# draw the centroids on the image and place text
	cv2.circle(frame,coordinates[-1],4,[0,0,255],-1)
	cv2.putText(frame,str(name),(int(camWidth/5),50), cv2.FONT_HERSHEY_PLAIN, 5.0,(0,0,0))
	cv2.putText(frame,str(zone[-1]),(leftBound,top_bound+50), cv2.FONT_HERSHEY_PLAIN, 5.0,(0,0,0))
	cv2.putText(frame,str("frame " + str(counter)), (leftBound,top_bound+100),cv2.FONT_HERSHEY_PLAIN, 5.0,(0,0,0))

	#resize image for the laptop
	frame = cv2.resize(frame,(0,0),fx=0.5,fy=0.5)
	cv2.imshow('image',frame)
	masked = cv2.resize(masked,(0,0),fx=0.5,fy=0.5)
	cv2.imshow('thresh',masked)
	difference = cv2.resize(difference,(0,0),fx=0.5,fy=0.5)
	cv2.imshow('diff',difference)

	endOfLoop = time.time()

	if counter%100 == 0:
		pass
		#hsv_initial = addToBackgroundImage(hsv,hsv_initial)

	print "time of loop: " + str(round(time.time()-beginningOfLoop,4))

	k = cv2.waitKey(1)
	if k == 27:
		break

	# the idea here is to re-set the 'initial' image every 150 frames in case there are changes with the light or top of the water reflections
#	if counter % 150 ==0:
#		hsv_initial = hsv

	counter+=1


########################
##### end of main loop #####
###################################

# save list of association zones
output = open(name + "/" + name+'.txt', 'wb')
for line in zone:
	output.write("%s\n" % line)
output.close()

### after the program exits, print some useful stuff to the screen
# first calculate realized fps
print "counter: " + str(counter)
print "\nthis program took " + str(time.time() - start_time) + " seconds to run."

# calculate and print association time to the screen
try:
	printUsefulStuff(zone,fps)
# just to make sure it works:
except:
	printUsefulStuff(zone,fps)


cv2.destroyAllWindows()
