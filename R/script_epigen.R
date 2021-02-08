library(readr)
library(magrittr)
library(ggplot2)
options(warn=-1)

#### Theme for ggplot figures ####
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


# Fetch command line arguments
myArgs <- commandArgs(trailingOnly = TRUE)

# Do some conversion/calculation here
path = as.character(myArgs)

dataframe <- read_csv(paste0(path,"dataframe.csv"), col_types = cols()) %>% as.data.frame(.)

pls_model <- readRDS("~/epigen_app/R/plsda_model.rds")

dataframe$pred <- predict(pls_model, dataframe)

dataframe$pred <- dataframe$pred %>% as.character(.) %>% as.numeric(.)

probabilities <- predict(pls_model, dataframe, type = "prob")

data4table <- data.frame(sample = dataframe$X1,
                         snp = dataframe$snp,
                         methylation = dataframe$pred,
                         unmeth_prob = probabilities$`0`,
                         meth_prob = probabilities$`1`)

data4table$methylation <- ifelse(data4table$methylation==1, "M", "U")
data4table$unmeth_prob <- round(data4table$unmeth_prob, digits = 4)
data4table$meth_prob <- round(data4table$meth_prob, digits = 4)

data4table <- data4table %>% tidyr::separate(sample, c("sample", "well"), sep="_")

write_csv(data4table, paste0(path, "CMS.csv"))

df <- data.frame("cg18849583" = mean(dataframe[dataframe$snp=="G1_1884","pred"]),
                 "cg01268345" = mean(dataframe[dataframe$snp=="G3_0126","pred"]),
                 "cg10333416" = mean(dataframe[dataframe$snp=="S1_1033","pred"]),
                 "cg12925355" = mean(dataframe[dataframe$snp=="S3_1292","pred"]),
                 "cg25542041" = mean(dataframe[dataframe$snp=="W1_2554","pred"]),
                 "cg02227036" = mean(dataframe[dataframe$snp=="W3_0222","pred"]))

linear_model <- readRDS("~/epigen_app/R/EpiWNT-SHH.rds")

ypred <- predict(linear_model, df)

probabilities <- ypred$posterior  %>% as.data.frame(.)

probabilities$class <- as.character(ypred$class)

write_csv(probabilities, paste0(path, "LDA.csv"))

#### PLOT CMS ####

pca_model <- readRDS("~/epigen_app/R/pca_train_model.rds")

label_meth <- readRDS("~/epigen_app/R/labels_train.rds")

proj <- predict(pca_model, dataframe)

df_pca_train <- as.data.frame(pca_model$x)
df_pca_train$methylation <- label_meth
df_pca_train$snp <- ""

proj <- as.data.frame(proj)
proj$methylation <- data4table$methylation
proj$snp <- data4table$snp

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
                           max.overlaps = Inf, color="black") + ggtitle(data4table[1,2])

p2 <- ggplot(dat2, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat2[dat2$snp != "",], color = ifelse(dat2[dat2$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,  
                           max.overlaps = Inf, color="black") + ggtitle(data4table[2,2])

p3 <- ggplot(dat3, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat3[dat3$snp != "",], color = ifelse(dat3[dat3$snp != "","methylation"]=="U","dodgerblue4","firebrick1"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5, 
                           max.overlaps = Inf, color="black") + ggtitle(data4table[3,2])

p4 <- ggplot(dat4, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat4[dat4$snp != "",], color = ifelse(dat4[dat4$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,  
                           max.overlaps = Inf, color="black") + ggtitle(data4table[4,2])

p5 <- ggplot(dat5, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat5[dat5$snp != "",], color = ifelse(dat5[dat5$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,  
                           max.overlaps = Inf, color="black") + ggtitle(data4table[5,2])

p6 <- ggplot(dat6, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat6[dat6$snp != "",], color = ifelse(dat6[dat6$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,  
                           max.overlaps = Inf, color="black") + ggtitle(data4table[6,2])

p7 <- ggplot(dat7, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat7[dat7$snp != "",], color = ifelse(dat7[dat7$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,  
                           max.overlaps = Inf, color="black") + ggtitle(data4table[7,2])

p8 <- ggplot(dat8, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat8[dat8$snp != "",], color = ifelse(dat8[dat8$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5,  
                           max.overlaps = Inf, color="black") + ggtitle(data4table[8,2])

p9 <- ggplot(dat9, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat9[dat9$snp != "",], color = ifelse(dat9[dat9$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5, 
                           max.overlaps = Inf, color="black") + ggtitle(data4table[9,2])

p10 <- ggplot(dat10, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat10[dat10$snp != "",], color = ifelse(dat10[dat10$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5, 
                           max.overlaps = Inf, color="black") + ggtitle(data4table[10,2])

p11 <- ggplot(dat11, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat11[dat11$snp != "",], color = ifelse(dat11[dat11$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5, 
                           max.overlaps = Inf, color="black") + ggtitle(data4table[11,2])

p12 <- ggplot(dat12, aes(x=PC1,y=PC2, color=methylation, fill = methylation)) + 
  geom_point(size=2, alpha=0.5) + theme + xlab(percentage[1]) + ylab(percentage[2]) + 
  stat_ellipse(geom = "polygon", alpha=0.1) +
  geom_point(data = dat12[dat12$snp != "",], color = ifelse(dat12[dat12$snp != "","methylation"]=="U","dodgerblue4","firebrick3"), size=3) + 
  ggrepel::geom_text_repel(aes(label = snp), min.segment.length = 0, box.padding = 0.5, point.padding = 0.5, 
                           max.overlaps = Inf, color="black") + ggtitle(data4table[12,2])

ggpubr::ggarrange(p1, p7, p2, p8, p3, p9, p4, p10, p5, p11, p6, p12, ncol = 4, nrow = 3)

ggsave("CMS_panel.png", path = paste0(path,"plots/"), dpi = 300, width = 20, height = 15)

cat("R script completed!")
