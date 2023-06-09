#!/bin/bash
cd /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Domino_EDF/epoched
export USLEEP_API_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2ODUwNDI5MzksImlhdCI6MTY4NDk5OTczOSwibmJmIjoxNjg0OTk5NzM5LCJpZGVudGl0eSI6ImUwY2RlM2IyYzUxOSJ9.d96FmpCq6gbGg1lQdDCgsxDF4Ru4OuvNdQhLt2uYfQY
# Loop over all .edf files in the directory and call the curl and usleep-api commands
for edf_file in *.edf; do
  # Generate new file name with a .tsv extension
  tsv_file="${edf_file%.edf}.tsv"
  # Call the curl command with the file names
  curl -s -X GET -H "Authorization: Bearer $USLEEP_API_TOKEN" https://sleep.ai.ku.dk/api/v1/info/model_names
  if [ ! -f "$tsv_file" ]; then
    usleep-api "$edf_file" "$tsv_file" --anonymize
  fi
done
#Call the Python script to transform tsv to csv
python /Users/shohreh/Documents/GitHub/OuraValidationAutomation/PSG_scoring_Download_Upload/transform_tsv2csv.py
for csv_file in *.csv; do
  mv "$csv_file" /Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/data_raw/Sleep_Staging/UsleepScored
done

echo "Done! Scored files transfered to Scores_csv folder!"
