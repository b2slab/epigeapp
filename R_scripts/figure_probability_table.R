#### Libraries ####
library(readr)
library(magrittr)
library(htmltools)
library(webshot)
library(formattable)
options(warn=-1)


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
df <- read.csv(paste0(path, "probability_dataframe.csv"))

# Transform character to factor
df$Status <- as.factor(df$Status)

# set colors
customRed = "firebrick2"
customGreen = "springgreen3"

colnames(df)[3] <- "Probability of being methylated"

# make formattable
tab <- formattable::formattable(df,
                                align =c("c","c","c"),
                                list(
                                  `CpG` = formatter("span"),
                                  `Status`= color_tile(customRed, customGreen)
                                ),
                                table.attr = 'style="font-size: 16px;"')

# save figure
export_formattable(f = tab, file = paste0(path, "plots/probability_table.png"))
