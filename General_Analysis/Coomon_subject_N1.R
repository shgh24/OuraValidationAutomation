#source("/Users/cnladmin/Desktop/DeZambottidata/ebe2sleep.R")

#setwd("/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3")
#setwd("/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/results/June_13_2023")
library(reshape2); library(ggplot2)
library(boot)
library(PropCIs)

# define path
my_path <- "/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura1/Analysis/deZambotti_Rpackage/sleep-trackers-performance-master/Functions/";

fi<-list.files(path = my_path, pattern = "*.R", all.files = FALSE,
               full.names=T, recursive = FALSE,
               ignore.case = FALSE, include.dirs = FALSE, no.. = FALSE)


# source all files containing the string '.R'

for (f in fi) { source(f) }


ylim_TST=c(-100,250);xlim_TST=c(-100,250)
ylim_WASO=c(-250,100);xlim_WASO=c(5,125)
ylim_Deep=c(-100,150);xlim_Deep=c(20,150)
ylim_Light=c(-100,200);xlim_Light=c(120,360)
ylim_REM=c(-100,100);xlim_REM=c(10,170)
ylim_SOL=c(-100,150);xlim_SOL=c(0,110)
ylim_SE=c(-50,50);xlim_SE=c(60,100)

#plot_name<-"TST_Oura3_PSG_BA.png"

hand=c("R","L")
Day=c("N01","N02")



device <- c("FB", "Dreem", "Oura3")  # Vector of strings
#device <- c( "Dreem")  # Vector of strings
for (name in device) {
  data_dir<-"/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/XXX/Common_Subj_N1"
  #/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/XXX/Common_Subj_N1
  data_dir<- gsub("XXX", name, data_dir)
  working_dir<-"/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/XXX/results/Common_Subj_N1"
  #/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Dreem/results/Common_Subj_N1
  working_dir<-gsub("XXX", name, working_dir)
  setwd(working_dir)
  
  fi_data <- list.files(path = data_dir)
  for (f in fi_data) { 
    ###########################################################################################################################
    
    file_path <- file.path(data_dir, f)
    raw.data <- read.csv(file_path)
    
    
    #(raw.data <- read.csv("/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/Data/combined_data_N02_L.csv"))
    ############################################################################################################################
    (sleep.data <- ebe2sleep(data = raw.data, idCol = "subject", RefCol = "reference", deviceCol = "device",
                             epochLenght = 30, staging = TRUE, stages = c(wake = 0, light = 1, deep = 3, REM = 5), digits = 2))
    
    fi_name <-gsub("combined_data","Individual_Sleep_Measurement" , f)
    #fi_name  <- "Individual_Bias_Day1_L.csv"
    write.csv(sleep.data , fi_name)
    
    ############################################################################################################################
    
    Bias_ind<-indDiscr(data = sleep.data, staging=TRUE, digits=2, doPlot = FALSE)
    fi_name <-gsub("combined_data","Individual_Bias" , f)
    #fi_name  <- "Individual_Bias_Day1_L.csv"
    write.csv(Bias_ind, fi_name)
    
    
    ###########################################################################################################################
    
    Group_Bias<-rbind(groupDiscr(data = sleep.data, measures=c("TST_device","TST_ref"), size="reference", 
                                 CI.type="boot", CI.level=.95, digits=2),
                      groupDiscr(data = sleep.data, measures=c("SE_device","SE_ref"), size="reference", 
                                 CI.type="boot", CI.level=.95, digits=2),
                      groupDiscr(data = sleep.data, measures=c("SOL_device","SOL_ref"), size="reference", 
                                 CI.type="boot", CI.level=.95, digits=2),
                      groupDiscr(data = sleep.data, measures=c("WASO_device","WASO_ref"), size="reference", 
                                 CI.type="boot", CI.level=.95, digits=2),
                      groupDiscr(data = sleep.data, measures=c("Light_device","Light_ref"), size="reference", 
                                 CI.type="boot", CI.level=.95, digits=2),
                      groupDiscr(data = sleep.data, measures=c("Deep_device","Deep_ref"), size="reference", 
                                 CI.type="boot", CI.level=.95, digits=2),
                      
                      # bootstrapped CI on log-transformed data
                      groupDiscr(data = sleep.data, measures=c("REM_device","REM_ref"), size = "reference", logTransf = TRUE, 
                                 CI.type="boot", CI.level=.95, digits=2),
                      groupDiscr(data = sleep.data, measures=c("LightPerc_device","LightPerc_ref"), size = "reference", logTransf = TRUE, 
                                 CI.type="boot",boot.type="basic",CI.level=.95, digits=2),
                      
                      # classic CI on log-transformed data
                      groupDiscr(data = sleep.data, measures=c("DeepPerc_device","DeepPerc_ref"), size  ="reference", logTransf = TRUE, 
                                 CI.type="classic", boot.type="basic", CI.level=.95, digits=2),
                      groupDiscr(data = sleep.data, measures=c("REMPerc_device","REMPerc_ref"), size="reference", logTransf = TRUE, 
                                 CI.type="classic",boot.type="basic",CI.level=.95, digits=2))
    
    fi_name <-gsub("combined_data","Group_Bias" , f)
    write.csv(Group_Bias, fi_name)
    ############################################################################################################################
    
    plot_name<-"TST_XXX_PSG_BA.png"
    plot_name <- gsub("XXX", name , plot_name)
    
    plot_name <- tools::file_path_sans_ext(plot_name)
    
    file_name <- gsub("combined_data_|\\.csv", "", f)
    file_name <- paste("_", file_name, sep = "")
    
    # Concatenate the strings with the "_" separator
    plot_name <- paste(plot_name, file_name, ".png", sep = "")
    
    
    
    png(file= plot_name, width=6, height=4, units="in", res=2000)
    myplot<-BAplot(data=sleep.data,measures=c("TST_device","TST_ref"), logTransf = FALSE,
                   xaxis="reference", CI.type="classic", CI.level=.95,ylim=ylim_TST)
    
    print(myplot)
    dev.off()
    
    plot_name_f<-gsub("TST","SE" , plot_name)
    png(file= plot_name_f, width=6, height=4, units="in", res=2000)
    myplot<-BAplot(data=sleep.data,measures=c("SE_device","SE_ref"), logTransf = FALSE,
                   xaxis="reference", CI.type="classic", CI.level=.95,ylim=ylim_SE)
    print(myplot)
    dev.off()
    
    plot_name_f<-gsub("TST","SOL" , plot_name)
    png(file= plot_name_f, width=6, height=4, units="in", res=2000)
    myplot<-BAplot(data=sleep.data,measures=c("SOL_device","SOL_ref"), logTransf = FALSE,
                   xaxis="reference", CI.type="classic", CI.level=.95,ylim=ylim_SOL)
    print(myplot)
    dev.off()
    
    plot_name_f<-gsub("TST","WASO" , plot_name)
    png(file= plot_name_f, width=6, height=4, units="in", res=2000)
    myplot<-BAplot(data=sleep.data,measures=c("WASO_device","WASO_ref"), logTransf = FALSE,
                   xaxis="reference", CI.type="classic", CI.level=.95,ylim=ylim_WASO)
    print(myplot)
    dev.off()
    
    
    plot_name_f<-gsub("TST","Light" , plot_name)
    png(file= plot_name_f, width=6, height=4, units="in", res=2000)
    myplot<-BAplot(data=sleep.data,measures=c("Light_device","Light_ref"), logTransf = FALSE,
                   xaxis="reference", CI.type="classic", CI.level=.95,ylim=ylim_Light)
    print(myplot)
    dev.off()
    
    plot_name_f<-gsub("TST","Deep" , plot_name)
    png(file= plot_name_f, width=6, height=4, units="in", res=2000)
    myplot<-BAplot(data=sleep.data,measures=c("Deep_device","Deep_ref"), logTransf = FALSE,
                   xaxis="reference", CI.type="classic", CI.level=.95,ylim=ylim_Deep)
    print(myplot)
    dev.off()
    
    plot_name_f<-gsub("TST","REM" , plot_name)
    png(file= plot_name_f, width=6, height=4, units="in", res=2000)
    myplot<-BAplot(data=sleep.data,measures=c("REM_device","REM_ref"), logTransf = FALSE,
                   xaxis="reference", CI.type="classic", CI.level=.95,ylim=ylim_REM)
    
    print(myplot)
    dev.off()
    ##################################################################################################
    
    ERRMTRIX<-errorMatrix(data = raw.data, idCol = "subject", RefCol = "reference", deviceCol = "device",
                          staging = TRUE, stages = c(wake = 0, light = 1, deep = 3, REM = 5), matrixType="prop",
                          CI.type = "boot", boot.type = "basic", boot.R = 10000, CI.level = .95, digits = 2)
    
    # fi_name  <- "ErrorMatrix_Day1_L.csv"
    fi_name <-gsub("combined_data","ErrorMatrix_propertional" , f)
    write.csv( ERRMTRIX, fi_name)
    
    ##################################################################################################
    
    (ebe <- cbind(indEBE(data = raw.data, stage = 0, stageLabel = "wake", doPlot = FALSE, digits = 2),
                  indEBE(data = raw.data, stage = 1, stageLabel = "light", doPlot = FALSE, digits = 2)[,2:4],
                  indEBE(data = raw.data, stage = 3, stageLabel = "deep", doPlot = FALSE, digits = 2)[,2:4],
                  indEBE(data = raw.data, stage = 5, stageLabel = "REM", doPlot = FALSE, digits = 2)[,2:4]))
    
    #fi_name  <- "EBE_individual_Day1_L.csv"
    fi_name <-gsub("combined_data","EBE_individual" , f)
    write.csv(ebe, fi_name)
    
    ###########################################################################################################
    
    library(reshape2); library(ggplot2)
    
    indEBE_melt <- melt(ebe[, c("subject", colnames(ebe)[grepl("sens", colnames(ebe)) == TRUE])])
    indEBE_melt$variable <- as.factor(gsub(" sens","",indEBE_melt$variable))
    ggplot(indEBE_melt,aes(x = variable, y = value, fill = variable)) + xlab("stage") + ylab("Sensitivity (%)") + 
      geom_boxplot(size=1.5, outlier.shape = NA, alpha = .5, width = .5, colour = "black") +
      geom_point(aes(col=variable),position = position_jitter(width = .15), size = 2) + 
      theme(legend.position = "none")
    
    #plot_name <- "Fourstage_Specificity_Day1_L.png"
    
    plot_name2  <-gsub("PSG_BA","" , plot_name_f)
    plot_name  <-gsub("REM","Fourstage_Sensitivity" , plot_name2)
    ggsave(plot_name)
    
    
    
    indEBE_melt <- melt(ebe[, c("subject", colnames(ebe)[grepl("spec", colnames(ebe)) == TRUE])])
    indEBE_melt$variable <- as.factor(gsub(" spec","",indEBE_melt$variable))
    ggplot(indEBE_melt,aes(x = variable, y = value, fill = variable)) + xlab("stage") + ylab("Specifity (%)") + 
      geom_boxplot(size=1.5, outlier.shape = NA, alpha = .5, width = .5, colour = "black") +
      geom_point(aes(col=variable),position = position_jitter(width = .15), size = 2) + 
      theme(legend.position = "none")
    
    plot_name  <-gsub("REM","Fourstage_Specificity" , plot_name2 )
    ggsave(plot_name)
    
    
    ###########################################################################################################
    indEBE(data = raw.data, stage = 0, stageLabel = "wake", doPlot = TRUE, digits = 2)[2]
    
    ###############################################################################################################
    EBE_metric<-rbind(groupEBE(data=raw.data,stage=0,stageLabel="wake",metricsType="avg",CI.type="boot",advancedMetrics=FALSE),
                      groupEBE(data=raw.data,stage=1,stageLabel="light",metricsType="avg",CI.type="boot",advancedMetrics=FALSE),
                      groupEBE(data=raw.data,stage=3,stageLabel="deep",metricsType="avg",CI.type="boot",advancedMetrics=FALSE),
                      groupEBE(data=raw.data,stage=5,stageLabel="REM",metricsType="avg",CI.type="boot",advancedMetrics=FALSE))
    #fi_name  <- "EBE_Group_Day1_L.csv"
    fi_name <-gsub("combined_data","EBE_Group" , f)
    write.csv(EBE_metric, fi_name)
    
    ###########################################################################################################
    
    Result<-rbind(groupEBE(data=raw.data,stage=0,stageLabel="wake",metricsType="avg",CI.type="boot",advancedMetrics=TRUE),
                  groupEBE(data=raw.data,stage=1,stageLabel="light",metricsType="avg",CI.type="boot",advancedMetrics=TRUE),
                  groupEBE(data=raw.data,stage=3,stageLabel="deep",metricsType="avg",CI.type="boot",advancedMetrics=TRUE),
                  groupEBE(data=raw.data,stage=5,stageLabel="REM",metricsType="avg",CI.type="boot",advancedMetrics=TRUE))
    
    
    #fi_name  <- "Advanced_4stage_Day1_L.csv"
    fi_name <-gsub("combined_data","Advanced_4stage" , f)
    write.csv(Result, fi_name)
    
    ###########################################################################################################
    # dichotomic recoding of raw dataset
    dic.data <- raw.data
    dic.data[dic.data$reference!=0,"reference"] = 5 # 5 when sleep
    dic.data[dic.data$reference==0,"reference"] = 10 # 10 when wake
    dic.data[dic.data$device!=0,"device"] = 5
    dic.data[dic.data$device==0,"device"] = 10
    dic.data
    
    
    
    Result<-groupEBE(data=dic.data,stage=10,stageLabel="wake",metricsType="avg",CI.type="boot",advancedMetrics=FALSE)
    #fi_name  <- "Slep-wake-EBE_Day1_L.csv"
    fi_name <-gsub("combined_data","EBE-Sleep-Wake" , f)
    write.csv(Result, fi_name)
    
    
    
    errorMatrix(data = dic.data, idCol = "subject", RefCol = "reference", deviceCol = "device",
                staging = FALSE, stages = c(wake = 10, sleep = 5), matrixType = "sum",
                CI.type = "classic", boot.type = "basic", CI.level = .95, digits = 2)
    
    
    
    
    fi_name <-gsub("combined_data","ErrorMatrix_propertional_SleepWake" , f)
    write.csv( ERRMTRIX, fi_name)
    
    
    
  }


}




















