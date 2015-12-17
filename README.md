## fernando_cichlid_tracking

I'm using this repo to store all the tracking code and scripts associated with tracking fish in a tank for Fernando's project.

The main script is `fernando_tracker.py`. It's run like `python fernando_tracker.py -n name_of_video -i path/to_video`. It'll create a folder within whatever directory contains `fernando_tracker.py` and output a bunch of useful files. It processes each frame of a video in about ~0.07 seconds on my quad-core 3.2 GHz Mac with 8 GB RAM. The program requires, among some other things, [OpenCV](http://opencv.org/), which is most easily installed on a Mac with [homebrew](www.homebrew.sh) like `brew tap homebrew/science; brew install opencv --with-ffmpeg`.    

 If you have `R` installed and are running Mac or Linux, you can run `Rscript fernando_tracking.R /path/to/dir` to visualize the tracking output from the tracker. An example of what that looks like when the tracker is run on a ~3.5 hour video (lighter colors = later in the video):               

![there should be an image here](https://raw.githubusercontent.com/lukereding/fernando_cichlid_tracking/master/video10/tracking_output1.png)


#### running the `R` script
The `R` script does a couple things and should be run from the command line. It is run from this repo like `Rscript fernando_tracking.R /path/to/dir` where `path/to/dir` is the path to the directory that the tracker outputs and contains all kinds of goodies. The script does a few things:
+ It draws the tracks of the fish over a photo of the tank. The lighter colors represent the fish's position later in the video.
+ It saves a bar graph with the bars: one each for the number of frames the fish spends on the left, right, and middle third of the tank.
+ It outputs the number of transits the fish made (1) from the middle to the left part of the tank and (2) from the middle to the right part of the tank. Check your shell; that's where it'll output to.
