#### Libraries ####
library(readr)
library(magrittr)
library(ggplot2)
library(htmltools)
library(webshot)
library(formattable)
options(warn=-1)

#### Load data ####
load("~/epigen_app/epigen_app/R/badPatterns.Rdata")
load("~/epigen_app/epigen_app/R/knowsPatterns.Rdata")

pls_model <- readRDS("~/epigen_app/epigen_app/R/plsda_model.rds")
lda_model <- readRDS("~/epigen_app/epigen_app/R/EpiWNT-SHH.rds")
pca_model <- readRDS("~/epigen_app/epigen_app/R/pca_train_model.rds")
label_meth <- readRDS("~/epigen_app/epigen_app/R/labels_train.rds")

#### Functions ####
checkBadPattern <- function(dataframe, replica) {
  flag <- FALSE
  names <- c("cg18849583","cg01268345","cg10333416", "cg12925355", "cg25542041", "cg02227036")
  for (i in 1:dim(badPatterns)[1]) {
    if (all(dataframe[replica,names] == badPatterns[i,names])) flag <- TRUE
  }
  flag
}

checkReplicate <- function(dataframe) {
  flag <- FALSE
  names <- c("cg18849583","cg01268345","cg10333416", "cg12925355", "cg25542041", "cg02227036")
  if (all(dataframe[1,names] == dataframe[2,names])) flag <- TRUE
  flag
}

scoreLDA <- function(object, dataframe, index){
  names <- c("cg18849583","cg01268345","cg10333416", "cg12925355", "cg25542041", "cg02227036")
  coefs <- object$scaling
  coefs <- rowSums(abs(coefs))
  N <- sum(coefs)
  coefs <- coefs[names]
  
  d <- stringdist::stringdist(dataframe$pattern[index], c("100101","011001","010110"))
  names(d) <- c("non-WNT/non-SHH","SHH","WNT")
  lab <- names(d)[which.min(d)]
  if (lab == "WNT"){
    v <- knowsPatterns[4,names] != dataframe[index,names]
    sc <- sum(coefs[v])/N
  } else if(lab == "SHH"){
    v <- knowsPatterns[3,names] != dataframe[index,names]
    sc <- sum(coefs[v])/N
  } else {
    v <- knowsPatterns[1,names] != dataframe[index,names]
    sc <- sum(coefs[v])/N
  }
  score <- 1 - sc
  list(score = score, lab = lab)
}

plotCMSpanel <- function(object, dataframe, label_meth, path2save){
  proj <- predict(object, dataframe)

  df_pca_train <- as.data.frame(object$x)
  df_pca_train$methylation <- label_meth
  df_pca_train$snp <- ""

  proj <- as.data.frame(proj)
  proj$methylation <- ifelse(dataframe$pred == 1, "M","U")
  proj$snp <- dataframe$snp

  dat1 <- rbind(df_pca_train, proj[1,])
  dat2 <- rbind(df_pca_train, proj[2,])
  dat3 <- rbind(df_pca_train, proj[3,])
  dat4 <- rbind(df_pca_train, proj[4,])
  dat5 <- rbind(df_pca_train, proj[5,])
  dat6 <- rbind(df_pca_train, proj[6,])
  dat7 <- rbind(df_pca_train, proj[7,])
  dat8 <- rbind(df_pca_train, proj[8,])
  dat9 <- rbind(df_pca_train, proj[9,])
  dat10 <- rbind(df_pca_train, proj[10,])
  dat11 <- rbind(df_pca_train, proj[11,])
  dat12 <- rbind(df_pca_train, proj[12,])

  percentage <- round(pca_model$sdev^2/sum(pca_model$sdev^2) * 100, 2)
  percentage <- paste0(colnames(df_pca_train), " (", paste( as.character(percentage), "%", ")", sep="") )

  p1 <- ggplot(dat1,aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat1[dat1$snp != "",], color = ifelse(dat1[dat1$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[1])

  p2 <- ggplot(dat2, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat2[dat2$snp != "",], color = ifelse(dat2[dat2$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[2])

  p3 <- ggplot(dat3, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat3[dat3$snp != "",], color = ifelse(dat3[dat3$snp != "","methylation"]=="U","dodgerblue4","firebrick1"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[3])

  p4 <- ggplot(dat4, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat4[dat4$snp != "",], color = ifelse(dat4[dat4$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[4])

  p5 <- ggplot(dat5, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat5[dat5$snp != "",], color = ifelse(dat5[dat5$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[5])

  p6 <- ggplot(dat6, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat6[dat6$snp != "",], color = ifelse(dat6[dat6$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[6])

  p7 <- ggplot(dat7, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat7[dat7$snp != "",], color = ifelse(dat7[dat7$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[7])

  p8 <- ggplot(dat8, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat8[dat8$snp != "",], color = ifelse(dat8[dat8$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[8])

  p9 <- ggplot(dat9, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat9[dat9$snp != "",], color = ifelse(dat9[dat9$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[9])

  p10 <- ggplot(dat10, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat10[dat10$snp != "",], color = ifelse(dat10[dat10$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[10])

  p11 <- ggplot(dat11, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat11[dat11$snp != "",], color = ifelse(dat11[dat11$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[11])

  p12 <- ggplot(dat12, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) +
    geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) +
    stat_ellipse(geom = "polygon", alpha=0.1) +
    geom_point(data = dat12[dat12$snp != "",], color = ifelse(dat12[dat12$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) +
    ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,
                             max.overlaps = Inf, color="black") + ggtitle(dataframe$Well[12])

  ggpubr::ggarrange(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, ncol = 4, nrow = 3)

  ggsave("CMS_panel.png", path = paste0(path2save,"plots/"), dpi = 300, width = 20, height = 15)

}

tablePlot <- function(dataframe){
  Sample_ID <- c("Rep1","Rep2")
  dataframe <- cbind(Sample_ID, dataframe)
  customRed = "firebrick2"
  customGreen = "springgreen3"

  tab <- formattable(dataframe, align =c("c","c","c","c","c", "c", "c"),
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

#### Theme for ggplot ####
theme <- theme(panel.background = element_blank(),
               panel.border=element_rect(fill=NA),
               panel.grid.major = element_blank(),
               panel.grid.minor = element_blank(),
               strip.background=element_blank(),
               axis.ticks=element_line(colour="black"),
               plot.margin=unit(c(1,1,1,1),"line"),
               legend.position = "none",
               axis.text.x=element_blank(),
               axis.text.y=element_blank())

### Fetch command line arguments NO MODIFICAR
myArgs <- commandArgs(trailingOnly = TRUE)

path <- as.character(myArgs)

#### Workflow ###
dataframe <- read_csv(paste0(path,"dataframe.csv"), col_types = cols()) %>% as.data.frame(.)

dataframe$pred <- predict(pls_model, dataframe)

dataframe$pred <- dataframe$pred %>% as.character(.) %>% as.numeric(.)

probabilities <- predict(pls_model, dataframe, type = "prob")

data4table <- data.frame(Sample = dataframe$X1,
                         SNP = dataframe$snp,
                         Status = dataframe$pred,
                         Unmeth_prob = probabilities$`0`,
                         Meth_prob = probabilities$`1`)

data4table$Status <- ifelse(data4table$Status==1, "Methylated", "Unmethylated")
data4table$Unmeth_prob <- round(data4table$Unmeth_prob, digits = 4)
data4table$Meth_prob <- round(data4table$Meth_prob, digits = 4)

data4table <- data4table %>% tidyr::separate(Sample, c("Sample", "Well"), sep="_")
data4table <- data4table[order(data4table$SNP),]

#Save table for CMS
write_csv(data4table, paste0(path, "dataframe_results_cms.csv"))

df <- data.frame("cg18849583" = dataframe[dataframe$snp=="G1_1884","pred"],
                 "cg01268345" = dataframe[dataframe$snp=="G3_0126","pred"],
                 "cg10333416" = dataframe[dataframe$snp=="S1_1033","pred"],
                 "cg12925355" = dataframe[dataframe$snp=="S3_1292","pred"],
                 "cg25542041" = dataframe[dataframe$snp=="W1_2554","pred"],
                 "cg02227036" = dataframe[dataframe$snp=="W3_0222","pred"])

df <- dplyr::mutate(df, pattern = paste0(cg18849583, cg01268345, cg10333416, cg12925355, cg25542041, cg02227036))

tab <- tablePlot(dataframe = df[,-7])

export_formattable(f = tab, file = paste0(path, "plots/replicas.png"))

if (checkReplicate(df)){
  
  if(!checkBadPattern(dataframe = df, replica = 1)){
    ypred <- predict(lda_model, df[1,])
    
    score <- scoreLDA(lda_model, df, 1)
    
    results <- data.frame(predicted1 = ypred$class, score1 = score$score, distLab1 = score$lab,
                          predicted2 = ypred$class, score2 = score$score, distLab2 = score$lab)
    
    write_csv(results, paste0(path, "dataframe_results_lda.csv"))
  } else {
    warning.df <- data.frame(warning1 = "Sample pattern is imposible to classify.")
    
    write_csv(warning.df, paste0(path, "dataframe_warning_lda.csv"))
  }

} else {
  names <- c("cg18849583","cg01268345","cg10333416", "cg12925355", "cg25542041", "cg02227036")
  if (sum(df[1,names] != df[2,names]) <= 1){
    if(!checkBadPattern(dataframe = df, replica = 1) & !checkBadPattern(dataframe = df, replica = 2)) {
      ypred1 <- predict(lda_model, df[1,])
      
      score1 <- scoreLDA(lda_model, df, 1)
      
      ypred2 <- predict(lda_model, df[2,])
      
      score2 <- scoreLDA(lda_model, df, 2)
      
      results <- data.frame(predicted1 = ypred1$class, score1 = score1$score, distLab1 = score1$lab,
                            predicted2 = ypred2$class, score2 = score2$score, distLab2 = score2$lab)
      
      write_csv(results, paste0(path, "dataframe_results_lda.csv"))
      
    } else {
      warning.df <- data.frame(warning1 = "Sample pattern is imposible to classify.")
      
      write_csv(warning.df, paste0(path, "dataframe_warning_lda.csv"))
    }
    
  } else {
    warning.df <- data.frame(warning1 = "The replicas have totally different patterns.")
    
    write_csv(warning.df, paste0(path, "dataframe_warning_lda.csv"))
  }
}

#### PLOT CMS ####
dataframe <- dataframe[order(dataframe$snp),]
dataframe$Well <- data4table$Well
plotCMSpanel(object = pca_model, dataframe = dataframe, label_meth = label_meth, path2save = path)

cat("R script completed!")




