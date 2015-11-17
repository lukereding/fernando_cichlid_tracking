## fernando tracking R script
## started 17 Nov 2015
# this script should be run from the command line like `Rscript fernando_tracking.R /path/to/dir/containing/.txt/and/.csv/files`

sessionInfo()

options(echo=TRUE)
args <- commandArgs(trailingOnly = TRUE)
print(args)
# change the working directory to whatever the directory passed as the arugment is 
setwd(args[1])

# get required pakcages if not installed
if (!"adimpro" %in% installed.packages()) install.packages("adimpro",repos='http://cran.us.r-project.org')
if (!"viridis" %in% installed.packages()) install.packages("viridis",repos='http://cran.us.r-project.org')


# plot the background image
library(adimpro)

# show the image
(background_file <- list.files(path=".", pattern = "*.jpg", full.names=T)[1])
back <- read.image(background_file, compress=TRUE)
back <- rotate.image(back, angle = 180, compress=NULL)
# set up for saving
png(filename = "./tracking_output.png", width = back$dim[1], height = back$dim[2])
show.image(back, xlim=c(0,back$dim[1]), ylim=c(0,back$dim[2]), bty="n", xaxt = "n", yaxt = "n")

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

# remaining frames
print(paste("removed ", original_frames - nrow(coords), " frames", sep = ""))

# assume the fish didn't move if the tracker doesn't pick up its position:
for(i in 1:nrow(coords)){
  if(is.na(coords$x[i])){
    coords$x[i] <- coords$x[i-1]
    coords$y[i] <- coords$y[i-1]
  }
}

# plot the tracks
library(viridis)
cols <- viridis(nrow(coords) -1)

for(i in 1:(nrow(coords)-1)){
  lines(x = c(coords$x[i], coords$x[i+1]), y = c(coords$y[i], coords$y[i+1]), col = cols[i], lwd=1.5)
}


# finish plotting
dev.off()

### save a stacked bar plot of the sides the fish was on:
png("./graph.png")
# read in the .txt file saved from the tracker
sides <- list.files(path=".", pattern = "*.txt", full.names=T)[2]
sides <- read.table(sides)
# factor
sides[,1] <- factor(sides[,1])

counts <- table(sides)

barplot(counts, main="", xlab="side of tank", col=viridis(4)[1:3], ylab= "number of frames")

dev.off()
