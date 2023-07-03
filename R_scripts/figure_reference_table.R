#### Libraries ####
library(htmltools)
library(webshot)
library(formattable)

Sys.setenv("OPENSSL_CONF"="/dev/null")

export_formattable <- function(f, file, width = "100%", height = NULL, 
                               background = "white", delay = 0.2)
{
  w <- as.htmlwidget(f, width = width, height = height)
  path <- html_print(w, background = background, viewer = NULL)
  url <- paste0("file:///", gsub("\\\\", "/", normalizePath(path)))
  webshot(url,
          file = file,
          selector = ".formattable_widget",
          delay = delay,
          zoom = 2)
}


df <- data.frame(Subgroup = c("non-WNT/non-SHH","SHH","WNT"),
                 cg18849583 = c(1,0,0),
                 cg01268345 = c(0,1,1),
                 cg10333416 = c(0,1,0),
                 cg12925355 = c(1,0,1),
                 cg25542041 = c(0,0,1),
                 cg02227036 = c(1,1,0))

customRed = "firebrick2"
customGreen = "springgreen3"

format_tab <- formattable::formattable(df,
                                align =c("c","c","c","c","c","c","c"),
                                list(
                                  `Subgroup` = formatter("span", style = ~ style(
                                    color = "grey")),
                                  `cg18849583`= color_tile(customGreen, customRed), 
                                  `cg01268345`= color_tile(customGreen, customRed), 
                                  `cg10333416`= color_tile(customGreen, customRed), 
                                  `cg12925355`= color_tile(customGreen, customRed), 
                                  `cg25542041`= color_tile(customGreen, customRed), 
                                  `cg02227036`= color_tile(customGreen, customRed)
                                ),
                                table.attr = 'style="font-size: 16px;"')

export_formattable(format_tab, "reference_table.png")


