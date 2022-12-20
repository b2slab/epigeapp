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

# Filter df 
dummy = df[df['Task'] == "UNKNOWN",]

# Get the Ct values
Allele1 <- dummy$Allele1.Ct

# Fixing the 'Undetermined' values to max Ct value
Allele1 <- ifelse(Allele1 == 'Undetermined', '40', Allele1) %>% as.numeric(.)

# Get the Ct values
Allele2 <- dummy$Allele2.Ct

# Fixing the 'Undetermined' values to max Ct value
Allele2 <- ifelse(Allele2 == 'Undetermined', '40', Allele2) %>% as.numeric(.)

# Change the original values for the changed values
dummy$Allele1.Ct <- Allele1
dummy$Allele2.Ct <- Allele2

# Init var
names = c('S1_1033', 'S3_1292', 'W1_2554', 'W3_0222', 'G1_1884', 'G3_0126')
std1 = vector(length = length(names))
std2 = vector(length = length(names))
snp_name = vector(length = length(names))
i = 1

# Loop to compute the std
for (name in names) {
  snp_name[i] <- name
  v <- dummy["SNP.Assay.Name"] == name
  std1[i] <- round(sd(dummy$Allele1.Ct[v]), 2)
  std2[i] <- round(sd(dummy$Allele2.Ct[v]), 2)
  i <- i + 1
}

# Create a new df
data2table <- data.frame("SNP Assay Name" = snp_name,
                         "Allele1 Ct Std" = std1,
                         "Allele2 Ct Std" = std2)

# Rename cols
colnames(data2table) <- c("SNP Assay Name",
                          "Allele1 Ct Std",
                          "Allele2 Ct Std")

# Making the format table
tab <- formattable::formattable(data2table, align = c("c","c","c"), 
                                table.attr = 'style="font-size: 16px;"')


# Saving as png
export_formattable(f = tab, 
                   file = paste0(path, "plots/standard_deviation_table.png"))


