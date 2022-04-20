#### Libraries ####
library(readr)
library(magrittr)
library(MASS)
library(randomForest)
library(htmltools)
library(webshot)
library(formattable)
library(fmsb)
options(warn=-1)

#### My functions ####
tablePlot <- function(dataframe, sampleName){
  Sample_ID <- c(sampleName)
  dataframe <- cbind(Sample_ID, dataframe)
  customRed = "firebrick2"
  customGreen = "springgreen3"
  
  tab <- formattable::formattable(dataframe,
    align =c("c","c","c","c","c","c","c"),
    list(
      `Sample_ID` = formatter("span", style = ~ style(
        color = "grey",font.weight = "bold")),
      `cg18849583`= color_tile(customGreen, customRed), 
      `cg01268345`= color_tile(customGreen, customRed), 
      `cg10333416`= color_tile(customGreen, customRed), 
      `cg12925355`= color_tile(customGreen, customRed), 
      `cg25542041`= color_tile(customGreen, customRed), 
      `cg02227036`= color_tile(customGreen, customRed)
      )
    )
  tab
}

export_formattable <- function(f, file, width = "100%", height = NULL, 
  background = "white", delay = 0.2) {
  w <- as.htmlwidget(f, width = width, height = height)
  path <- html_print(w, background = background, viewer = NULL)
  url <- paste0("file:///", gsub("\\\\", "/", normalizePath(path)))
  print(url)
  webshot(url,
          file = file,
          selector = ".formattable_widget",
          delay = delay)
}

score <- function(distancia) {
  return(1 - round(distancia/6, digits = 2))
}

#### Debug Flag ####

debug <- F

if (debug) {
  # Path del archivo csv
  path <- "~/Desktop/debug_script/sample/results/"
  
}else{
  # Fetch command line arguments #
  myArgs <- commandArgs(trailingOnly = TRUE)
  
  path <- as.character(myArgs)
}

#### Workflow ####

# Read data
dataframe <- read_delim(paste0(path, "Results.csv"), "\t", 
  escape_double = FALSE, trim_ws = TRUE)

# get data of interes
doi <- dataframe[dataframe$Task == "UNKNOWN",]

# get mean rn dataframe  
delta_dataframe <- plyr::ddply(doi, "`SNP Assay Name`", function(dx){
  deltaRnAllele1 <- mean(dx$`Allele1 Delta Rn`)
  deltaRnAllele2 <- mean(dx$`Allele2 Delta Rn`)
  dd <- data.frame(delta1_avg = deltaRnAllele1, 
                   delta2_avg = deltaRnAllele2)
})

# change 1r colname 
colnames(delta_dataframe)[1] <- "CpG_name"

# transform to log scale
delta_dataframe$delta1_avg_log <- log(delta_dataframe$delta1_avg)
delta_dataframe$delta2_avg_log <- log(delta_dataframe$delta2_avg)

# load logistic regression
logitModel <- readRDS("~/epigen_app/epigen_app/R/logitModel.RDS")

# get methylation probabilites 
delta_dataframe$meth_prob <- predict(logitModel, delta_dataframe, type = "response")

# get methylation class with a optimal cutoff = 0.456
delta_dataframe$meth_class <- ifelse(delta_dataframe$meth_prob > 0.456, 1, 0)

# create report probabilities table 
probabilities_table <- data.frame(
  CpG = c("cg18849583", "cg01268345", "cg10333416", "cg12925355", "cg25542041", "cg02227036"),
  Status = ifelse(delta_dataframe$meth_class == 1,"Methylated","Unmethylated"),
  Probability = round(delta_dataframe$meth_prob, digits = 4))

# saving previous table
write_csv(probabilities_table, paste0(path, "table_logistic_regression.csv"))

# transform dataframe
# G1, G3, S1, S3, W1, W3 -> cg18849583, cg01268345, cg10333416, cg12925355, cg25542041, cg02227036
sample_data <- data.frame(cg18849583=delta_dataframe$meth_class[1],
                          cg01268345=delta_dataframe$meth_class[2],
                          cg10333416=delta_dataframe$meth_class[3],
                          cg12925355=delta_dataframe$meth_class[4],
                          cg25542041=delta_dataframe$meth_class[5],
                          cg02227036=delta_dataframe$meth_class[6])

# create pattern
pattern <- paste0(sample_data$cg18849583,
                  sample_data$cg01268345,
                  sample_data$cg10333416,
                  sample_data$cg12925355,
                  sample_data$cg25542041,
                  sample_data$cg02227036)

# compute hamming distances
distances <- stringdist::stringdist(pattern, c("100101","011001","010110"), 
                                    method = "hamming")
# get the shortest distance
min_distance <- Reduce(min,distances)

# get MB subgroup and distance score
if (sum(min_distance == distances) < 2) {
  names(distances) <- c("non-WNT/non-SHH","SHH","WNT")
  mb_subgroup <- names(distances)[which.min(distances)]
  distance_score <- score(min_distance)
}else{
  mb_subgroup <- "Not classified"
  distance_score <- score(min_distance)
}

# create table to save
distance_table <- data.frame(subgroup = mb_subgroup, 
                             d_G3G4 = round(score(distances[1]), digits = 2),
                             d_SHH = round(score(distances[2]), digits = 2),
                             d_WNT = round(score(distances[3]), digits = 2))

# formatting rownames
row.names(distance_table) <- NULL

# saving table
write_csv(distance_table, paste0(path, "table_distances.csv"))


#### Plots ####

#### plot 1: Sample table ####
# get sample name 
sample_name <- unique(doi$`Sample Name`)

# make figure
tab <- tablePlot(dataframe = sample_data, sampleName = sample_name)

# save figure
export_formattable(f = tab, file = paste0(path, "plots/table_sample.png"))

#### plot 2: Radar plot ####
dataplot <- data.frame(sample = c("max", "min", "cutoff", sample_name), 
                       d_G3G4 = c(1,0,0.67,score(distances[1])),
                       d_SHH = c(1,0,0.67,score(distances[2])),
                       d_WNT = c(1,0,0.67,score(distances[3])))

tiff(paste0(path,"radar_plot.tiff"), width = 5, height = 5, units = 'in', res = 300)
op <- par(mar = c(0, 1, 1, 1))
radarchart(dataplot[,2:4], 
           vlabels=c("non-WNT/non-SHH (100101)","SHH (011001)","WNT (010110)"), 
           pcol = c("#f23f3f","#00AFBB"), pfcol = scales::alpha("#00AFBB", c(0,0.5)), plwd = 2, plty = c(2,1),
           vlcex = 0.8,
           cglcol = "grey", cglty = 1, cglwd = 0.8,
           axistype = 1, axislabcol = "grey", caxislabels = c(0, .25, .50, .75, 1),
           centerzero = T)
par(op)
dev.off()



