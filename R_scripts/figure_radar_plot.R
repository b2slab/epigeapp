#### Libraries ####
library(readr)
library(magrittr)
library(fmsb)
options(warn=-1)

Sys.setenv("OPENSSL_CONF"="/dev/null")

#### Main ####

#### Debug Flag ####

debug <- F

if (debug) {
  # Path del archivo csv
  path <- "~/media/samples/b45607e0-f732-44e0-bb99-f3859e2c7414/results/"
  
}else{
  # Fetch command line arguments #
  myArgs <- commandArgs(trailingOnly = TRUE)
  
  path <- as.character(myArgs)
}

#### plot 2: Radar plot ####

# load data
dataframe <- read.csv(paste0(path, "distances_dataframe.csv"))


dataplot <- data.frame(sample = c("max", "min", "cutoff", "sample"),
                       d_G3G4 = c(1,0,0.67,dataframe$dGG),
                       d_SHH = c(1,0,0.67,dataframe$dSHH),
                       d_WNT = c(1,0,0.67,dataframe$dWNT))

tiff(paste0(path,"plots/radar_plot.tiff"), width = 5, height = 5, units = 'in', res = 300)
op <- par(xpd=T, mar = c(0.8, 0.8, 0.8, 0.8), cex = 1.2)
radarchart(dataplot[,2:4], 
           vlabels=c("non-WNT/non-SHH (100101)","SHH (011001)","WNT (010110)"), 
           pcol = c("#f23f3f","#00AFBB"), pfcol = scales::alpha("#00AFBB", c(0,0.5)), plwd = 2, plty = c(2,1),
           vlcex = 0.8,
           cglcol = "grey", cglty = 1, cglwd = 0.8,
           axistype = 1, axislabcol = "grey", caxislabels = c(0, .25, .50, .75, 1),
           centerzero = T)
par(op)
dev.off()
