#!/usr/bin/env python

#######################
# Copyright Author: Hareesh Mandalapu.

# Code creates the multilingual voice impersonation dataset developed in the paper: "H.Mandalapu R. Raghavednra and C. Busch, Multilingual Voice Impersonation Dataset and Evaluation, 3rd International Conference on Intelligent Technologies and Applications (INTAP) 2020 Gjøvik, Norway."

# See README.txt for requirements

# Usage: python create_dataset.py 

#######################

import os
import numpy as np
import csv
import sys


# get identities of the subjects
with open('id_names.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=' ')
    identities = {}
    
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            titles = [row[0],row[1],row[2]]
            line_count += 1
        else:
            identities[row[2]] = [row[1],row[0]]
            line_count += 1

# get output path to save the segmented audio file
def get_output(given_path):
    names = given_path.split("/")
    sub_name = names[1].split("_")[0]
    part = names[1].split("_")[1]
    num = names[1].split("_")[2]

    sub_id = identities[sub_name][1]
    lang = identities[sub_name][0]
    
    if part == "real":
        output_path = lang+"/"+sub_id+"/"+part            
    else:
        output_path = lang+"/"+sub_id+"/attack"
    
    try:
        os.makedirs(root_path+"/audio_data/"+output_path)
    except OSError:
        count = 1
    
    final_path = output_path+"/"+sub_id+"_"+num
    
    return final_path


root_path = "."                 # change this to save the dataset in different location
partitions_path = os.path.join(root_path,"audio_scripts")

missed_videos = []
# file to save the unavailable videos
missed_file = open(os.path.join(root_path,"unavailable_videos.txt"),"w")

to_delete = "random"

languages = [f for f in os.listdir(partitions_path) if os.path.isdir(os.path.join(partitions_path,f))]
for l in languages:
    lang_path = os.path.join(partitions_path, l)
    files = [f for f in os.listdir(lang_path) if os.path.isfile(os.path.join(lang_path,f))]
    for f in files:
        if f.endswith(".txt"):
            sub_name = f.split(".")[0]
            file_path = os.path.join(lang_path,f)
            file_data = open(file_path,"r")
            for line in file_data:
                contents = line.split(' ')
                y_name = contents[0]
                if not os.path.isfile(y_name+".wav"):
                    full_file_wav = r'"'+y_name+r'.%(ext)s"'
                    try:
                        os.system("youtube-dl --extract-audio --audio-format wav --audio-quality 1 --output "+full_file_wav+" "+y_name)                     # download and convert the youtube video to wav
                    except:
                        print("Cannot download the video: "+y_name)
                        missed_videos.append(y_name)
                        missed_file.write(y_name+'\n')
                                            
                if os.path.isfile(y_name+".wav"):
                    output_path = "impersonation_data/"+get_output(contents[3])
                    try:                    
                        os.system("ffmpeg -y -i "+r'"'+y_name+r'.wav"'+" -ss "+ contents[1] +" -to "+contents[2]+" "+output_path)                    # segment the audio file according to the scripts
                    except:
                        count = 1
                else:
                    if not y_name in missed_videos:
                        missed_videos.append(y_name)
                        print("YouTube video "+y_name+" not found!")
                        missed_file.write(y_name+'\n')
                if not y_name == to_delete:
                    if not to_delete == "random":
                        try:
                            os.remove(to_delete+".wav")       # delete the original audio after saving segments
                        except:
                            count = 1
                to_delete = y_name
            file_data.close()

missed_file.close()


# remove the temporary files 
files_left = [f for f in os.listdir(root_path) if os.path.isfile(os.path.join(root_path,f))]

for f in files_left:
    if f.endswith(".wav"):
        os.remove(f)



