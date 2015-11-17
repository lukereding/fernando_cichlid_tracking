## fernando_cichlid_tracking

I'm using this repo to store all the tracking code and scripts associated with tracking fish in a tank for Fernando's project.

The goal is to create a real-time tracker that can detect a single fish in a tank, then do this for four tanks.


#### running the `R` script
The `R` script does a couple things and should be run from the command line. First, it draws the tracks of the fish over a photo of the tank. Second, it plot the distribution of the number of frames the fish spends on the right, left, and middle parts of the tank. It is run from this repo like `Rscript fernando_tracking.R /path/to/dir` where `path/to/dir` is the path to the directory that the tracker outputs and contains all kinds of goodies. The script will save but the photo of the tank with the tracking results on top of it and the graph to this directory.

#### ideas for doing things four at a time:
python fernando_tracker.py -i 0 -n camera_0 &
python fernando_tracker.py -i 1 -n camera_1 &
python fernando_tracker.py -i 2 -n camera_2 &
python fernando_tracker.py -i 3 -n camera_3 &

Put this in a shell script, then run as `bash -x name_of_script.sh`

Each processor (assuming four processors) gets it's own job.
Still need to inorporating making sure a constant frame rate is maintained (use the --fps argument of the python script for this)

#### to install python, opencv on windows, follow these directions:
http://opencvpython.blogspot.com/2012/05/install-opencv-in-windows-for-python.html

#### ffmpeg
To make a video from the frames you save, try `ffmpeg -f image2 -i %08d.jpg -r 5 -vcodec libx264 name_of_video.avi`
