## fernando tracking R script
## started 17 Nov 2015
# this script should be run from the command line like `Rscript fernando_tracking.R /path/to/dir/containing/.txt/and/.csv/files`

# print session info for reference / debugging purposes
sessionInfo()

options(echo=TRUE)
args <- commandArgs(trailingOnly = TRUE)
print(args)
# change the working directory to whatever the directory passed as the arugment is
setwd(args[1])

# get required pakcages if not installed
if (!"adimpro" %in% installed.packages()) install.packages("adimpro",repos='http://cran.us.r-project.org')
if (!"viridis" %in% installed.packages()) install.packages("viridis",repos='http://cran.us.r-project.org')

# load adimpro
library(adimpro)

# show the image
(background_file <- list.files(path=".", pattern = "*.jpg", full.names=T)[1])
back <- read.image(background_file, compress=TRUE)
# because of differences in the coordinate schemes of R and Python, we need to rotate the image 180 degrees \
# in order to have the tracks plotted in the right spot.
# we will flip the photo back later using a system() call to imagemagick
back <- rotate.image(back, angle = 180, compress=NULL)
# set up for saving
png(filename = "./tracking_output.png", width = back$dim[1], height = back$dim[2])
# actually display the image
show.image(back, xlim=c(0,back$dim[1]), ylim=c(0,back$dim[2]), bty="n", xaxt = "n", yaxt = "n", main=args[1])

# read in coordinate data from tracking program
coords <- list.files(path=".", pattern = "*.csv", full.names=T)[1]
coords <- read.csv(coords)

# number of frames
original_frames <- nrow(coords)
print(paste("number of frames: ", nrow(coords), sep = ""))

# for now, strip beginning NA's:
while(is.na(coords$x[1])){
  coords <- coords[-1,]
}

# print number of leading frames removed
print(paste("removed ", original_frames - nrow(coords), " frames", sep = ""))

# for now, assume the fish didn't move if the tracker doesn't pick up its position:
for(i in 1:nrow(coords)){
  if(is.na(coords$x[i])){
    coords$x[i] <- coords$x[i-1]
    coords$y[i] <- coords$y[i-1]
  }
}

# plot the tracks
library(viridis)
cols <- plasma(nrow(coords) -1)

for(i in 1:(nrow(coords)-1)){
  lines(x = c(coords$x[i], coords$x[i+1]), y = c(coords$y[i], coords$y[i+1]), col = cols[i], lwd=1.5)
}

# finish plotting; save the result
dev.off()

# because of differences in the coordinate schemes of R and Python, we need to
# use imageMagick to rotate the image back 180 degrees
# if you don't have this and want it, on a mac run `brew install imagemagick`
system("convert ./tracking_output.png -rotate 180 ./tracking_output.png")

### save a  bar plot of the sides the fish was on:
# set up for saving the plot
png("./graph.png")
# read in the .txt file saved from the tracker
sides <- list.files(path=".", pattern = "*.txt", full.names=T)[2]
sides <- read.table(sides)
# factor
sides[,1] <- factor(sides[,1])

# get counts of # of frames on each side of the tank
counts <- table(sides)

# plot it
barplot(counts, main="", xlab="side of tank", col=viridis(4)[1:3], ylab= "number of frames")

# calculate number of times the fish enters the left or right zone of the tank
sides[,1] <- as.character(sides[,1])
entries_right <- entries_left <- 0
for(i in 1:(nrow(sides) - 1)){
    if(sides[i+1, 1] != sides[i, 1]){
        if(sides[i, 1] == "right"){
            entries_right <- entries_right + 1
        }
        else if(sides[i, 1] == "left"){
            entries_left <- entries_left + 1
        }
    }
}
x <- paste("entries into the left side of the tank: ", entries_left, "\nentries into the right side of the tank: ", entries_right)
cat(x)

# paste the results into a legend
legend("topright", legend = x, bty="n")

# save it
dev.off()
