library(rmda)
library(dplyr)
library(ggplot2)
library(tidyverse)
library(data.table)
library(caret)
library(predtools)




##########    READ DEVELOPMENT PROBABILITIES FOR DS 2500, DS 35 AND DS CR

create_plot <- function(Model_name1= "DS_35_Year", 
                        Year1 =2,
                        save_path="PATH_TO_OUTPUT\\"
){
  
  ###########   READ PLOT DATA
  
  df <- fread("\\Recalibration\\DATA FOR PLOTS\\Plot data\\plot_data_development.csv")
  cuttoff <- read.csv("\\Recalibration\\DATA FOR PLOTS\\Cutoffs\\cutoffs_development_recalibrated_probs_subgrp.csv")
  cuttoff <- cuttoff %>% filter(Model== paste0(Model_name1, Year1)) %>% filter( Ageg=="All", Gender =="All")
  
  ########## cutoffs
  cuttoff_sens <- cuttoff$Cutoff[ cuttoff$Type=="Sensitivity"]
  cuttoff_spec  <- cuttoff$Cutoff[ cuttoff$Type=="Specificity"]
  
  message(paste("Creating plot for", Model_name1,Year1))
  col0 <- "#396742"   # for Recalibration = 0
  col1 <- "#A93226"   # for Recalibration = 1
  col_sens <- "#f8766d"  # sensitivity vline colour
  col_spec <- "#00bfc4"  # specificity vline colour
  
  df2 <- df %>% mutate(Recalibration = if_else(Recalibration==1,"Recalibrated", "Original"))
  df1 = df2%>% filter(Model_name==Model_name1, Year==Year1)
  xaxismax <- yaxismax <- max((df1$mean_pred)*1.05,max(df1$observed*1.05))
  df1 <- df1 %>% mutate(Model_name = case_when (substr(Model_name, 1,7) == "DS_35_Y" ~"DeepSurv 35",
                                                substr(Model_name, 1,7) == "DS_35_C" ~"DeepSurv 35 competing",
                                                substr(Model_name, 1,4) == "DS_2" ~"DeepSurv 2500",
                                                substr(Model_name, 1,2) == "XG"~"XGBoost",
                                                substr(Model_name, 1,5) == "COX_4"~"Cox 400",
                                                substr(Model_name, 1,5) == "COX_3"~"Cox 35"))
  
  
  #CREATE PLOT
  p <- ggplot(df1, aes(x = mean_pred, y = observed, group = factor(Recalibration))) +
    geom_point(aes(color = factor(Recalibration)), size = 1, show.legend = FALSE) +
    geom_line(aes(color = factor(Recalibration)), size = 0.8) +
    geom_errorbar(aes(ymin = lower, ymax = upper)) +
    geom_ribbon(aes(ymin = lower, ymax = upper, fill = factor(Recalibration)), alpha = 0.25) +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "gray", lwd = 1.2) +
    geom_vline(aes(xintercept = cutoffs_sens, color = "Sensitivity (80%)",linetype = factor(Recalibration)), linewidth = 1.2) +
    geom_vline(aes(xintercept = cutoffs_spec, color = "Specificity (80%)",linetype = factor(Recalibration)),  linewidth = 1.2) +
    scale_color_manual(
      name = NULL,
      values = c(
        "Original" = col0,
        "Recalibrated" = col1,
        "Sensitivity (80%)" = col_sens,
        "Specificity (80%)" = col_spec
      )) +
    scale_linetype_manual(
      name = "Cutoffs",  
      values = c("Original" = "dashed", "Recalibrated" = "dotted")
    ) +
    scale_fill_manual(values = c("Original" = col0, "Recalibrated" = col1), guide = FALSE) +
    labs(x = "Predicted risk of hip fracture", y = "Observed Proportion of hip fractures", title = paste0(Model_nam, " - ", Year, " Years")) +
    scale_x_continuous(limits = c(0, xaxismax), labels = function(v) format(v, decimal.mark = "\u00B7")) +
    scale_y_continuous(limits = c(0, yaxismax), labels = function(v) format(v, decimal.mark = "\u00B7")) +
    theme_minimal() +
    theme(text = element_text(family = "Times"),
          plot.title = element_text(size = 16),
          plot.subtitle = element_text(size = 16),
          axis.title = element_text(size = 16),
          axis.text = element_text(size = 16),
          legend.position = "right"
    )+
    guides(
      color = guide_legend(order = 1),
      linetype = guide_legend(order = 2)
    )
  
  # SAVE PLOT
  ggsave(paste0(save_path,"Calibration_Development_",Model_name1,Year1, ".pdf"), plot = p, width = 8, height = 6,dpi=600)
}

########### CREATE PLOTS
Model_nam <- df$Model_name %>% unique()
Year <- df$Year %>% unique()



for ( Y in Year){
  for (Mod  in Model_nam){
    create_plot (Model_name1 =Mod, Year1=Y)
  }
}




################################ Validation


create_plot_val <- function(Model_name1, Year1,
                            save_path="PATH_TO_OUTPUT\\"){
  ###########   READ PLOT DATA
  df <- fread("\\Recalibration\\DATA FOR PLOTS\\Plot data\\plot_data_validation.csv")
  cuttoff <- read.csv("\\Recalibration\\DATA FOR PLOTS\\Cutoffs\\cutoffs_development_recalibrated_probs_subgrp.csv")
  cuttoff<- cuttoff %>% filter(Model== paste0(Model_name1, Year1)) %>% filter( Ageg=="All", Gender =="All")
  
  ###########   CUTOFF
  sens_cut <- cuttoff$Cutoff[ cuttoff$Type=="Sensitivity"]
  spec_cut  <- cuttoff$Cutoff[ cuttoff$Type=="Specificity"]
  
  
  message(paste("Creating plot for", Model_name1,Year1))
  col0 <- "#396742"   # for Recalibration = 0
  col1 <- "#A93226"   # for Recalibration = 1
  col_sens <- "#f8766d"  # sensitivity vline colour
  col_spec <- "#00bfc4"  # specificity vline colour
  
  
  df1 <- df%>% filter(Model_name==Model_name1, Year==Year1)
  xaxismax <- yaxismax <- max((df1$mean_pred)*1.05,max(df1$observed*1.05))
  df1 <- df1 %>% mutate(Model_name = case_when (substr(Model_name, 1,7) == "DS_35_Y" ~"DeepSurv 35",
                                                substr(Model_name, 1,7) == "DS_35_C" ~"DeepSurv 35 competing",
                                                substr(Model_name, 1,4) == "DS_2" ~"DeepSurv 2500",
                                                substr(Model_name, 1,2) == "XG"~"XGBoost",
                                                substr(Model_name, 1,5) == "COX_4"~"Cox 400",
                                                substr(Model_name, 1,5) == "COX_3"~"Cox 35"))
  
  df1$cutoffs_sens[df1$Recalibration==1] <- sens_cut
  df1$cutoffs_spec[df1$Recalibration==1] <- spec_cut
  
  
  #CREATE PLOT
  p <- ggplot(df1, aes(x = mean_pred, y = observed)) +
    geom_point( size = 1, show.legend = FALSE, color="#396742") +
    geom_line( size = 0.8, color="#396742") +
    geom_errorbar(aes(ymin = lower, ymax = upper)) +
    geom_ribbon(aes(ymin = lower, ymax = upper), fill="#396742", alpha = 0.25) +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "gray", lwd = 1.2) +
    geom_vline(aes(xintercept = cutoffs_sens, color = "Sensitivity (80%)"), linewidth = 1.2) +
    geom_vline(aes(xintercept = cutoffs_spec, color = "Specificity (80%)"),  linewidth = 1.2) +
    scale_color_manual(
      name = NULL,
      values = c(
        "Original" = col0,
        "Recalibrated" = col1,
        "Sensitivity (80%)" = col_sens,
        "Specificity (80%)" = col_spec
      )
    ) +
    scale_fill_manual(values = c("Original" = col0, "Recalibrated" = col0), guide = FALSE) +
    labs(x = "Predicted risk of hip fracture", y = "Observed Proportion of hip fractures", title = paste0(Model_nam, " - ", Year, " Years")) +
    scale_x_continuous(limits = c(0, xaxismax), labels = function(v) format(v, decimal.mark = "\u00B7")) +
    scale_y_continuous(limits = c(0, yaxismax), labels = function(v) format(v, decimal.mark = "\u00B7")) +
    theme_minimal() +
    theme(text = element_text(family = "Times"),
          plot.title = element_text(size = 16),
          plot.subtitle = element_text(size = 16),
          axis.title = element_text(size = 16),
          axis.text = element_text(size = 16),
          legend.position = "right"
    )+
    guides(
      color = guide_legend(order = 1),
      linetype = guide_legend(order = 2)
    )
  #SAVE PLOT
  ggsave(paste0(save_path,"Calibration_validation_",Model_name1,Year1, ".pdf"), plot = p, width = 8, height = 6,dpi=600)
}

########### CREATE PLOTS
Model_name1 <- df$Model_name %>% unique()
Year <- df$Year %>% unique()



for ( Y in Year){
  for (Mod  in Model_name1){
    create_plot_val (Model_name1 =Mod, Year1=Y)
  }
}
















