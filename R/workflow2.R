#### Libraries ####
library(readr)
library(magrittr)
library(MASS)
library(randomForest)
library(htmltools)
library(webshot)
library(formattable)
options(warn=-1)

#### Own functions ####
tablePlot <- function(dataframe, sampleName){
  Sample_ID <- c(sampleName)
  dataframe <- cbind(Sample_ID, dataframe)
  customRed = "firebrick2"
  customGreen = "springgreen3"
  
  tab <- formattable::formattable(dataframe, align =c("c","c","c","c","c", "c", "c"), 
                                  list(
                                    `Sample_ID` = formatter("span", style = ~ style(color = "grey",font.weight = "bold")),
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

export_formattable <- function(f, file, width = "100%", height = NULL, background = "white", delay = 0.2) {
  w <- as.htmlwidget(f, width = width, height = height)
  path <- html_print(w, background = background, viewer = NULL)
  url <- paste0("file:///", gsub("\\\\", "/", normalizePath(path)))
  print(url)
  webshot(url,
          file = file,
          selector = ".formattable_widget",
          delay = delay)
}

### Fetch command line arguments NO MODIFICAR
myArgs <- commandArgs(trailingOnly = TRUE)

path <- as.character(myArgs)

#### Start workflow ####
dataframe <- read_delim(paste0(path, "Results.csv"), "\t", escape_double = FALSE, trim_ws = TRUE)

doi <- dataframe[dataframe$Task == "UNKNOWN",]

rnData <- plyr::ddply(doi, "`SNP Assay Name`", function(dx){
  print(dx)
  deltaRnAllele1 <- mean(dx$`Allele1 Delta Rn`)
  deltaRnAllele2 <- mean(dx$`Allele2 Delta Rn`)
  dd <- data.frame(deltaRnAllele1 = deltaRnAllele1, deltaRnAllele2 = deltaRnAllele2)
})

colnames(rnData)[1] <- "cpg"

rnData$delta1_avg_log <- log(rnData$deltaRnAllele1)
rnData$delta2_avg_log <- log(rnData$deltaRnAllele2)

logitModel <- readRDS("~/epigen_app/R/logitModel.RDS")

rnData$meth_prob <- predict(logitModel, rnData, type = "response")

rnData$meth_class <- ifelse(rnData$meth_prob > 0.456, 1, 0)

## tabla para el report ##
data4table1 <- data.frame(SNP = c("cg18849583", "cg01268345", "cg10333416", "cg12925355", "cg25542041", "cg02227036"),
                          MethylationStatus = ifelse(rnData$meth_class == 1,"Methylated","Unmethylated"), 
                          MethylationProbability = round(rnData$meth_prob, digits = 4))

write_csv(data4table1, paste0(path, "dataframe_logit.csv"))

mat <- rnData$meth_class %>% as.matrix(.) %>% t(.)

cpg_names <- rnData$cpg

colnames(mat) <- c("cg18849583", "cg01268345", "cg10333416", "cg12925355", "cg25542041", "cg02227036")

rf.model <- readRDS("~/epigen_app/R/randomForestModel.RDS")

results <- data.frame(subgroup = predict(rf.model, mat))

results <- cbind(results, predict(rf.model, mat, type = "prob"))

colnames(results)[2:4] <- paste("probability", colnames(results)[2:4], sep = " ")

## tabla para el report ##
data4table2 <- results

write_csv(data4table1, paste0(path, "dataframe_rf.csv"))

#### Plot sample ####
df <- mat %>% as.data.frame(.)

sampleName <- unique(doi$`Sample Name`)

tab <- tablePlot(dataframe = df, sampleName = sampleName)

export_formattable(f = tab, file = paste0(path, "plots/sample.png"))


