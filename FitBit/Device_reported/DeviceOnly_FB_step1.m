%This script truncates PSG scoring data to lights-On and Lights-off and
%match it with FB data

clc;clear all;
%PSG, scoring and timing files:
addpath('/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/NFS5/Analysis/Fitbit/ProcessSleepJSON')
PSG_dir='/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Consensus_score/';
FB_dir='/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Fitbit';

FB_Output_dir='/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/Fitbit/DeviceOnly/';
% NUS3002_v1.2_sleep_2023-03-02_2023-03-04.json

timing=readtable('/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Timings/OURA3_ManualTimingLog.xlsx');

% /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Domino_EDF/epoched/NUS3006_N2_epoched_\(1\).edf
scoring_list=dir([FB_dir '/NUS*']);
PSG_list=dir([PSG_dir '/NUS*']);
output_PSG = extractBefore({PSG_list.name}, 11);
%%
for i=1:size(scoring_list,1)

  timing_id=find(ismember([timing.ID],(scoring_list(i).name)));
    

     %Save truncated scoring data 
    for night=1:2
        
    if i~=34
        
     if night==1   
         PSG_SleepDate=timing.N1_Date(timing_id);% day subject came to lab(N1date)
         lights_off = [char(timing.N1Lightsoff(timing_id)) '00']; 
         lights_on= [char(timing.N1Lightson(timing_id)) '00'];
         
         
         PSG_id=find(ismember(output_PSG',([scoring_list(i).name,'_N1'])));
         id=[scoring_list(i).name,'_N1'];
         
     elseif night==2
         PSG_SleepDate=timing.N2_Date(timing_id);% day subject came to lab(N2date)
         
         lights_off = [char(timing.N2Lightsoff_OR_GetinBed(timing_id)) '00'];
         lights_on= [char(timing.N2Lightson_OR_Getoutofbed(timing_id)) '00'];
         
         
         PSG_id=find(ismember(output_PSG',([scoring_list(i).name,'_N2'])));
         id=[scoring_list(i).name,'_N2'];

     end
     
  %%   



     
        % Split the input string into pairs of characters
        
            charPairs_On = reshape(lights_on, 2, [])';

            % Convert each pair of characters into a number and store in a numeric array
            lights_on = arrayfun(@(x) str2double(charPairs_On(x, :)), 1:size(charPairs_On, 1));
            
            
            charPairs_Off = reshape( lights_off, 2, [])';

            % Convert each pair of characters into a number and store in a numeric array
             lights_off = arrayfun(@(x) str2double(charPairs_Off(x, :)), 1:size(charPairs_Off, 1));
            %Lights Off change to 24 if after midnight 

         if lights_off(1)<4 % Past midnight
             
            lights_off(1) =lights_off(1)+24;
         end
    
            %Lights On change to 24 if after midnight     
        if lights_on(1)<12  % For nocturnal sleep only
           lights_on(1) = lights_on(1)+24;
        end
        
        if length(lights_on)>=4
           lights_on(4) =lights_on(3)*60;
           lights_on(3)=[];
        end
        
        if length(lights_off)>=4
           lights_off(4) =lights_off(3)*60;
           lights_off(3)=[];
        end
            

       %Wake date of subject
        PSG_wakeDate=datetime(PSG_SleepDate,'InputFormat','yyyy-MM-dd')+1;
        epochlength = 30;
  


        %% Load FB data 
         prism_file = dir(fullfile(FB_dir,scoring_list(i).name, [scoring_list(i).name '_v1.2_sleep_*.json']));
%            if i==61
%              jsontext = importdata('/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Fitbit/NUS3063/NUS3063_v1.2_sleep_2023-05-18_2023-05-20.json')

             
         if ~isempty(prism_file)
            jsontext = importdata(fullfile(FB_dir,scoring_list(i).name, prism_file.name));
             values = jsondecode(jsontext{1});
             jsondata=values.sleep;



            Y=cellfun(@(x) x(1:10), {jsondata.endTime},'UniformOutput',false);
            FB_D=cellfun(@datetime, Y);

            ind=find(ismember(FB_D,PSG_wakeDate) & [jsondata.isMainSleep]);


        if ~isempty(ind) 

            
            if ~any(strcmp({jsondata(ind).levels.data.level }, 'restless'))

            [curr_epoch curr_timestamp] = ConvertToEpochs(jsondata(ind).levels);
            

            DIFF=length(curr_epoch)-length(curr_timestamp);
            epochs_stages = cat(2, curr_timestamp, curr_epoch(1:end-DIFF)); 
           
%             fname = [scoring_list(i).name  '_N' num2str(night) '.mat'];
            [FB_data] =Oura_epoch_reshap(epochs_stages);
            
            outdir_FB = fullfile(FB_Output_dir);                       
            if (~exist(outdir_FB, 'dir')); mkdir(outdir); end
            base_path_FB= outdir_FB;
%             save(fullfile(base_path,fname),'epochs_stages');

             fname = [scoring_list(i).name  '_N' num2str(night) '.csv'];
              csvwrite(fullfile(base_path_FB,fname), FB_data);

            %%
  
            


     end
    end
    
        
        
    end
    
    
    
 

    end
    end
end


%%
function  [epochs_stages] =Oura_epoch_reshap(Output)
% 0 = wake, 1 = light sleep (N1 or N2), 2 = deep sleep (N3), and 3 = REM sleep
%ep_time=Output.timestamp;  
ed_data=Output(:,2);           
ed_data(strcmp(ed_data,'wake'))={0};%Wake
ed_data(strcmp(ed_data,'rem'))={5};%REM
ed_data(strcmp(ed_data,'deep'))={3};%Deep
ed_data(strcmp(ed_data,'light'))={1};%Light
epochs_stages=cell2mat(ed_data);
                                                
end

