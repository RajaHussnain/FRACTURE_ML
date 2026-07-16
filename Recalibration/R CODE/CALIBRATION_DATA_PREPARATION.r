
##################
####### LOAD LIBRARIES
##################
library(rmda)
library(dplyr)
library(ggplot2)
library(tidyverse)
library(data.table)
library(caret)
library(predtools)

#####################################
##########    READ DEVELOPMENT PROBABILITIES FOR DS 2500, DS 35 AND DS CR
###########################
df_2500_probs <- fread("PATH_TO_DATA\\DS_2500_prob_dev.csv")

df_35_probs <- fread("PATH_TO_DATA\\DS_35_prob_dev.csv")

df_35_comp_probs <- fread("PATH_TO_DATA\\DS_35_COMP_prob_dev.csv")

# functions
create_observed<-function(dataset,
                          Year=10, 
                          Model_name="DS_35_Year", 
                          factor_df = data.frame(intercept =0,
                                             slope =1),
                          max_proba = 1,
                          nbins =4){
  
  intercept <- factor_df$intercept
  slope <- factor_df$slope
  var_name  <- paste0(Model_name,Year)
  dataset$temp <- intercept + dataset[[var_name]] * slope
  dataset<- dataset %>% mutate(bin = ntile (temp, nbins))
 
  # Calculate mean predicted and observed for each bin
  
  calib_df <- dataset %>%
    mutate(obs_temp = if_else(Inc_Fx_Inc_fx_hip_bin_cens == 1 & Inc_Fx_Inc_fx_hip_days_to_cens <Year*365.25,1,0 ))%>%
    group_by(bin) %>%
    summarise(
      mean_pred = mean(temp),
      observed = mean(obs_temp)
    )%>%
    arrange(bin)
  return(calib_df)
}
# FUNCTION TO FIND OPTIMAL INTERCEPT AND SLOPE

find_factor <- function(dataset, 
                        Recal=0,
                        Model_name="DS_35_Year", 
                        Year=10, 
                        max_proba,
                        nbins=10){
  
  res = create_observed(dataset=dataset, Model_name=Model_name, Year=Year, max_proba = max_proba, nbins =nbins )

  # FIND intercept and slope such that Sum of square difference is minimized
  fit <- lm(observed ~ mean_pred, data=res)
  coef_values <- coef(fit)

  best_factor <- data.frame(intercept = coef_values[1],
                            slope = coef_values[2],
                            Model_name = Model_name,
                            Year = Year,
                            nbins=Year
                            )
  #
  
  best_factor %>% write.csv(paste0("PATH_TO_SAVE\\Factors\\factors_",Model_name,Year,"Recalibration",Recal,".csv"))
  return (best_factor)
}


# FUNCTION FOR BOOTSTRAPS
get_boots <- function(dataset, Model_name="DS_35_Year", Year=10, max_proba = 1, factor_df, nbins =4) {
  
  intercept <- factor_df$intercept
  slope <- factor_df$slope
  
  var_name <- paste0(Model_name,Year)
  dataset$temp <- intercept + dataset[[var_name]] * slope
 
  datas <- dataset[sample(nrow(dataset), replace = TRUE), ]
  datas<- datas %>% mutate(bin = ntile (temp, nbins))
  
  ress<- datas %>%
    mutate(obs_temp = if_else(Inc_Fx_Inc_fx_hip_bin_cens == 1 & Inc_Fx_Inc_fx_hip_days_to_cens <Year*365.25,1,0 ))%>%
    group_by(bin) %>%
    summarise(obs = mean(obs_temp)) %>%
    arrange(bin)
  return(ress)
}

# Function to create plot

create_calibration_plot <- function (data,
                                     Recalibration=0,
                                     Age_grp="All",
                                     Gen="All",
                                     Model_name="DS_35_Year",
                                     Year=10,
                                     max_proba=1,
                                     nbins =8,
                                     n_boot=30,
                                     xaxismax=0,
                                     yaxismax=0,
                                     folder_path="PATH_TO_SAVE\\"){
  
  factors <- data.frame(intercept =0, slope=1)
  message(paste0("Creating plot for ", Model_name, Year))
  if (Recalibration ==1)   {
    folder_path="PATH_TO_SAVE\\Recalibration\\"
    message("Calculating optimal factor")
    factors <- find_factor(dataset=data, Model_name=Model_name, Year=Year, max_proba = max_proba, nbins =nbins, Recal=1)
  }
  
  if(Recalibration==2){ 
    factors <- find_factor(dataset=data, Model_name=Model_name, Year=Year, max_proba = max_proba, nbins =nbins, Recal=2)
    factors$intercept<-0}
  boot_results <- replicate(n_boot, 
                            get_boots(data=data, 
                                      Model_name=Model_name, 
                                      Year=Year, 
                                      max_proba = max_proba, 
                                      factor_df= factors, 
                                      nbins = nbins)$obs, 
                            simplify = "matrix")
  
  
  Model_namn <- case_when (substr(Model_name, 1,4) == "DS_3" ~"DeepSurv 35",
                           substr(Model_name, 1,4) == "DS_2" ~"DeepSurv 2500",
                           substr(Model_name, 1,2) == "XG"~"XGBoost",
                           substr(Model_name, 1,5) == "COX_4"~"Cox 400",
                           substr(Model_name, 1,5) == "COX_3"~"Cox 35")
  
  # Compute percentiles for CIs
  ci_df <- as.data.frame(t(apply(boot_results, 1, quantile, probs = c(0.025, 0.975))))
  colnames(ci_df) <- c("lower", "upper")
  ci_df$bin <- 1:nrow(ci_df)
  # Merge with observed to get plot
  res <- create_observed(dataset=data, Model_name=Model_name, Year=Year, max_proba = max_proba, factor_df=factors, nbins = nbins )
  
  res1 <- res %>% left_join(ci_df, by="bin")
  if (xaxismax==0) xaxismax <- max(res1$mean_pred)*1.02
  
  if (yaxismax==0) yaxismax<- max(res1$observed*1.2)
  
  ######### READ CUTOFFS
  cutoffs <- read.csv("PATH_TO_CUTOFF\\cutoffs_development.csv")
  
  cutoffs<- cutoffs %>% filter(Ageg==Age_grp, Gender==Gen, Model==paste0(Model_name,Year))
  cutoffs_sens <- factors$intercept + cutoffs$Cutoff [cutoffs$Type=="Sensitivity"] * factors$slope
  
  cutoffs_spec <- factors$intercept +  cutoffs$Cutoff [cutoffs$Type=="Specificity"] * factors$slope
  res1$Model_name <- Model_name
  res1$Year <- Year
  res1$cutoffs_sens <- cutoffs_sens
  res1$Recalibration <- Recalibration
  res1$cutoffs_spec <- cutoffs_spec
  res1$Age_grp <- Age_grp
  res1$Gen <- Gen
  
  res1 %>% mutate(observed = if_else(observed<0,0, observed),
                  lower = if_else(lower<0,0, lower),
                  upper = if_else(upper<0,0, upper),
                  mean_pred = if_else(mean_pred<0,0, mean_pred))
  res1 %>% write.csv(paste0("PATH_TO_Plot_data\\Plot_Data_",Model_name,Year,"_Recalibration_",Recalibration,"_Age_group_",Age_grp,"_Gen_",Gen,".csv"))
  
  
  p <- ggplot(res1, aes(x = mean_pred, y = observed)) +
    geom_point(size = 1,color="#396742") +
    geom_line(size=0.8, color="#396742") +
    geom_errorbar(aes(ymin = lower, ymax = upper),,color="#396742") +
    geom_ribbon(aes(ymin = lower, ymax = upper), alpha = 0.25, fill = "#396742") +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "gray",lwd=1.2) +
    labs(x = "Predicted risk of hip fracture", y = "Observed Proportion of hip fractures") +
    scale_x_continuous(limits=c(0, xaxismax),
                       labels = function(v) format(v, decimal.mark = "\u00B7"))+
    scale_y_continuous(limits = c(0, yaxismax),
                       labels = function(v) format(v, decimal.mark = "\u00B7"))+
    ggtitle(paste0(Model_namn, " - ", Year, " Years"))+
    theme_minimal()+ 
    theme(text = element_text(family = "Times"),
          plot.title = element_text(size = 16),
          plot.subtitle = element_text(size = 16),
          axis.title = element_text(size = 16,),
          axis.text = element_text(size = 16)
    )      +
    geom_vline(aes(xintercept = cutoffs_sens, color = "Sensitivity (80%)"), linetype="dashed",linewidth=1.2)+
    geom_vline(aes(xintercept = cutoffs_spec, color = "Specificity (80%)"), linetype="dashed",linewidth=1.2)+
    labs(color = NULL, linetype = NULL) +
    theme(legend.position = "bottom")
  
  
  ggsave(paste0(folder_path,Model_name,"\\",Age_grp,"\\", Gen, "\\", "Calibration_", Model_name, Year,"_",Age_grp,"_",Gen,".pdf"), plot = p, width = 8, height = 6,dpi=600)
  
}

############################################  FUNCTION TO CREATE PLOT


create_plot_dev<- function(data = df, Ageg= "All" , Gen= "All", Model_name="DS_35_Year", Year,nbins=8, nboot=100, Recalibration=1){
  message("Creating plot for ", Ageg, " ", Gen, "Model: ", Model_name, " Years : ", Year, " Recalibration: ", Recalibration)
  if (Gen =="Men")   df_temp <- data %>% filter(Sex==1)
  if (Gen =="Women")   df_temp <- data %>% filter(Sex==2)
  if (Ageg =="50 - 64")   df_temp <- df_temp %>% filter(Age>=50 & Age<=64)
  if (Ageg =="65 - 79")   df_temp <- df_temp %>% filter(Age>=65 & Age<=79)
  if (Ageg =="80+") df_temp <- df_temp %>% filter(Age>=80)
  if (Ageg == "All") df_temp <- data
  
  if (Year == 2 & Ageg=="50 - 64") xaxismax<- yaxismax <-0.01
  if (Year == 5 & Ageg=="50 - 64") xaxismax<- yaxismax <-0.016
  if (Year == 10 & Ageg=="50 - 64") xaxismax<- yaxismax <-0.06
  
  if (Year == 2 & Ageg=="65 - 79") xaxismax<- yaxismax <-0.03
  if (Year == 5 & Ageg=="65 - 79") xaxismax<- yaxismax <-0.075
  if (Year == 10 & Ageg=="65 - 79") xaxismax<- yaxismax <-0.13
  
  if (Year == 2 & Ageg=="80+") xaxismax<- yaxismax <-0.11
  if (Year == 5 & Ageg=="80+") xaxismax<- yaxismax <-0.25
  if (Year == 10 & Ageg=="80+") xaxismax<- yaxismax <-0.4
  
  if( Year == 2 & Ageg =="All") xaxismax<- yaxismax <-0.03
  if( Year == 5 & Ageg =="All") xaxismax<- yaxismax <-0.075
  if( Year == 10 & Ageg =="All") xaxismax<- yaxismax <-0.15
  
  if (Recalibration==1){
  create_calibration_plot(data = df_temp   ,
                          Recalibration=Recalibration,
                          Age_grp = Ageg,
                          Gen = Gen,
                          Model_name = Model_name, 
                          Year = Year,
                          nbins = nbins,
                          n_boot = nboot,
                          xaxismax =xaxismax, yaxismax=yaxismax,
                          # Change the folder path
                          folder_path="save_path\\Recalibration\\"
  )
  }
  if (Recalibration==0) {  create_calibration_plot(data = df_temp   ,
                                  Recalibration=Recalibration,
                                  Age_grp = Ageg,
                                  Gen = Gen,
                                  Model_name = Model_name, 
                                  Year = Year,
                                  nbins = nbins,
                                  n_boot = nboot,
                                  xaxismax =xaxismax, yaxismax=yaxismax,
                                  # Change the folder path
                                  folder_path="save_path"
  )}
  if (Recalibration==2) {  create_calibration_plot(data = df_temp   ,
                                                   Recalibration=Recalibration,
                                                   Age_grp = Ageg,
                                                   Gen = Gen,
                                                   Model_name = Model_name, 
                                                   Year = Year,
                                                   nbins = nbins,
                                                   n_boot = nboot,
                                                   xaxismax =xaxismax, yaxismax=yaxismax,
                                                   # Change the folder path
                                                   folder_path="save_path"
  )}
}



#############   CREATE CALIBRATION PLOTS FOR DEVELOPMENT BOTH RECALIBRATED AND ORIGINAL

Years <- c(2,5,10)
Recalibration <- c(0,1)
#Recalibration <-2
################################# DS35 
for (Year in Years){
  for (Rec in Recalibration){
    create_plot_dev(data = df_35_probs , 
                    Recalibration = Rec,
                    Ageg = "All" , Gen="All", Model_name="DS_35_Year", 
                    Year = Year,nbins=8, 
                    nboot=30)
  }
}
################################# DS 2500
for (Year in Years){
  for (Rec in Recalibration){
     create_plot_dev(data = df_2500_probs,
                     Recalibration = Rec,
                    Ageg = "All" ,
                     Gen="All", 
                     Model_name="DS_2500_Year", 
                     Year = Year,
                     nbins=8, 
                     nboot=30)
}
}
################################# DS35 COMP
for (Year in Years){
  for (Rec in Recalibration){
    create_plot_dev(data = df_35_comp_probs,
                    Ageg = "All" ,
                    Gen = "All",
                    Recalibration=Rec,
                    Model_name = "DS_35_COMP_Year", 
                    Year = Year,
                    nbins = 8, 
                    nboot = 30)
  }
}

df_35_COX <- fread("PATH_TO_PROBABILITIES\\COX35_prob.csv")
Years <- c(2,5,10)
df_35_COX <- df_35_COX %>% mutate(Sex = if_else(Sex_2 ==TRUE,2,1))

Recalibration <- c(0,1)

################################# Cox_35
for (Year in Years){
  for (Rec in Recalibration){
    create_plot_dev(data = df_35_COX,
                    Ageg = "All" ,
                    Gen = "All", 
                    Recalibration=Rec,
                    Model_name = "COX_35_Year", 
                    Year = Year,
                    nbins = 8, 
                    nboot = 30)
  }
}

df_400_COX <- fread("PATH_TO_PROBABILITIES\\COX400_prob.csv")
df_400_COX <- df_400_COX %>% mutate(Sex = if_else(Sex_2 ==TRUE,2,1))

################################# Cox_400
for (Year in Years){
  for (Rec in Recalibration){
    create_plot_dev(data = df_400_COX,
                    Ageg = "All" ,
                    Gen = "All", 
                    Recalibration=Rec,
                    Model_name = "COX_400_Year", 
                    Year = Year,
                    nbins = 8, 
                    nboot = 30)
  }
}

################# Merge recalibration


folder_path <- "PATH_TO_Plot data"
# List all CSV files in the folder
csv_files <- list.files(path = folder_path, pattern = "\\.csv$", full.names = TRUE)



merged_df <- csv_files %>%
  lapply(read.csv, stringsAsFactors = FALSE) %>%
  bind_rows()
merged_df <- merged_df %>% mutate(mean_pred = if_else(mean_pred<0, 0,mean_pred))
# Save the merged data to a new CSV file
write.csv(merged_df %>% distinct(), file.path(folder_path, "plot_data_development.csv"), row.names = FALSE)



############################################### merge factors
folder_path <- "PATH_TO_Factors"
# List all CSV files in the folder
csv_files <- list.files(path = folder_path, pattern = "1\\.csv$", full.names = TRUE)


#csv_files
merged_df <- csv_files %>%
  lapply(read.csv, stringsAsFactors = FALSE) %>%
  bind_rows()
merged_df %>% distinct()
# Save the merged data to a new CSV file
write.csv(merged_df %>% distinct(), file.path(folder_path, "factors_development.csv"), row.names = FALSE)























