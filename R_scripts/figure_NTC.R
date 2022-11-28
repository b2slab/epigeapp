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

# load data
df <- read.csv(paste0(path, "Results.csv"), sep = "\t")

# Filter data by rows
df_ntc = df[df['Task'] == 'NTC',]

# Filter data by columns
df_ntc = df_ntc[,c('Well.Position','SNP.Assay.Name','Allele1.Ct','Allele2.Ct')]

# Rename cols
colnames(df_ntc) <- c('Well Position',
                      'SNP Assay Name',
                      'Allele1 Ct',
                      'Allele2 Ct')
# Rename rows
row.names(df_ntc) <- NULL 

# Make a format table
tab <- formattable::formattable(df_ntc, align =c("c","c","c"))

# Saving table as png
export_formattable(tab, file = paste0(path, "plots/NTC_table.png"))


