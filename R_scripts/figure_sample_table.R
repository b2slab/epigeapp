#### Libraries ####
library(readr)
library(magrittr)
library(htmltools)
library(webshot)
library(formattable)
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
                                      color = "grey")),
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
          delay = delay,
          zoom = 2)
}

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

#### plot 1: Sample table ####

# load data
dataframe <- read.csv(paste0(path, "sample_dataframe.csv"))

# get sample name 
sample_name <- as.character(dataframe$sample_name)

# get sample data
sample_data <- dataframe[,1:6]

# make figure
tab <- tablePlot(dataframe = sample_data, sampleName = sample_name)

# save figure
export_formattable(f = tab, file = paste0(path, "plots/sample_table.png"))
