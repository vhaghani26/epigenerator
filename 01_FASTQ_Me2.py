#!/bin/bash python3 

import sys
import os
import re

# Ensure user is in proper working directory.
proper_dir = input("Are you currently in your project directory? (y/n) ")

if proper_dir.lower() == "no" or proper_dir.lower() == "n":
    print("Please make your project directory using 'mkdir project_name' and enter it using 'cd project_name' and then try again.")
    sys.exit()

print("\n")

# Store project directory
project_dir = os.getcwd()

# Determine if data is maintained locally or on SLIMS
data_location = input("Is your data maintained on SLIMS or locally downloaded? (slims/local) ")

print("\n")

# Set location variable 
data_location = data_location.lower()

################
## SLIMS Data ##
################

# Set data_location variable to 'slims' if slims 
if data_location[1:-1] == 'slims':
    data_location = data_location[1:-1]

if data_location == 'slims':

    # Get SLIMS metadata to prepare for download   
    SLIMSstring = input("What is your SLIMS string? ")
    SLIMSdir = input("What is your SLIMS directory? ")
    data_dir = SLIMSdir
    
    # Start download
    os.system(f"echo 'Downloading fastq files for {SLIMSstring}'")
    os.system(f"rsync -avL slimsdata.genomecenter.ucdavis.edu::slims/{SLIMSstring}/ .")

    # Confirm proper transfer
    os.system(f"Carrying out MD5 Checksum to ensure that the files have properly transferred")
    os.chdir(f"{SLIMSdir}")            
    os.system(
    '''
    if md5sum -c \@md5Sum.md5
    then
        echo
        echo "All files have the correct md5sum"
    else
        echo "ERROR: Some files are corrupt or missing. Please re-run this script before continuing."
        exit 1
    fi
    ''')
 
    # Move undetermined files
    os.system("echo 'Moving undetermined files'")
    newpath = 'Other'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.system("mv Undetermined* Other")
    
    # Change back into original directory
    os.chdir(project_dir)
    
################
## Local Data ##
################

# Set data_location variable to 'slims' if slims 
if data_location[1:-1] == 'local':
    data_location = data_location[1:-1]

if data_location == 'local':
    data_dir = input("What is the absolute path that contains your raw data? ")
    
    # Ensure that path exists
    isExist = os.path.exists(data_dir)
    while not isExist:
        data_dir = input("This directory could not be found. Please check to make sure that the directory is correct and try again: ")
        isExist = os.path.exists(data_dir)

####################################
## Handle Incorrect Data Location ##
####################################

if data_location != 'slims' and data_location != 'local':
    print("Please try again with either 'slims' or 'local'.")

print("\n")
    
#################################
## Identify Samples and Genome ##
#################################

# Determine forward vs. reverse read notation  
f_r_delim = input("Does your data separate forward and reverse reads using the R1/R2 system or _1/_2 system? (R/_) ")

while f_r_delim != "R" and f_r_delim != "_":
    print("Please specify the system using either R for the R1/R2 system or _ for the _1/_2 system.")
    f_r_delim = input("Does your data separate forward and reverse reads using the R1/R2 system or _1/_2 system? (R/_) ")

print("\n")

# Determine delimiter for sample IDs
samp_id_delim = input("In most cases, your sample ID will be followed (i.e. delimited by) an underscore. Is this true for your data? If you are unsure, the answer is likely yes. (y/n) ")

print("\n")

if samp_id_delim.lower() == "no" or samp_id_delim.lower() == "n":
    samp_id_delim = input("What is your delimiter (i.e. what character separates your sample ID from the rest of the file name)? ")
else:
    samp_id_delim = "_"

# Add all data files to list
print("Checking for the right number of unique sample IDs for the forward and reverse reads")

raw_files = {}
for path, subdirs, files in os.walk(data_dir):
    for name in files:
        filepath = os.path.join(path, name)
        if filepath.endswith('fastq.gz') or filepath.endswith('fq.gz'):
            raw_files[name] = filepath

# Get sample IDs
sample_ids = []
for key in raw_files.keys():
    sample_id = key.split(f"{samp_id_delim}")
    sample_ids.append(sample_id[0])
sample_ids = set(sample_ids)

# Verify that the number of samples are correct
samp_num = input(f"According to your inputs, you have {len(sample_ids)} samples. Is this correct? (y/n) ")

if samp_num.lower() == "no" or samp_num.lower() == "n":
    print("An error has occured. Please try entering your project metadata again.")
    sys.exit()
    
print("\n")
    
# Verify that the sample IDs are correct    
for samp in sample_ids:
    print(samp)

print("\n")

samp_names = input("Please check the sample IDs above. Are they correct? (y/n) ")
if samp_num.lower() == "no" or samp_num.lower() == "n":
    print("An error has occured. Please try entering your project metadata again.")
    sys.exit()  

print("\n")

# Determine genome
genome = input("Please input the primary genome you will align your files to. This will need to match the name of the genome subdirectory you created in 01_genomes/ ")

print("\n")

######################
## Make Config File ##
######################

# Remove task_samples.yaml if it already exists
isExist = os.path.isfile("task_samples.yaml")
if isExist:
    os.system("rm -f task_samples.yaml")

# Create task_samples.yaml 
print("Creating task_samples.yaml, which will contain all unique sample IDs and get used in further analysis.")
file = "task_samples.yaml"
os.system(f"touch {file}")
# Saving reference of standard output
original_stdout = sys.stdout
# Write sample IDs into task_samples.yaml
with open(file, "a") as f:
    sys.stdout = f
    print("---")
    print(f"sequence_data: {data_dir}")
    print(f"genome: {genome}")
    print("samples:")
    for samp in sample_ids:
        print(f"  - {samp}")
    
# Reset standard output
sys.stdout = original_stdout
print("task_samples.yaml has been created.")

# Restructure dictionary to contain full file paths of files with same sample IDs
files_per_samp = {}
for samp in sample_ids:
    files_per_samp[samp] = []
    for key, value in raw_files.items():
        if key.startswith(f'{samp}{samp_id_delim}'):                
            files_per_samp[samp].append(value)

# Save space
del raw_files
del sample_ids

#################
## Merge Lanes ##
#################

ready_or_not = input("Are you ready to merge lanes? (y/n) ")
if ready_or_not.lower() == "no" or ready_or_not.lower() == "n":
    print("Please try again when you're ready.")
    sys.exit()
print("\n")

# Make 01_raw_sequences directory
print("Preparing to merge lanes\n")
isExist = os.path.exists("01_raw_sequences")
if not isExist:
    os.system("mkdir 01_raw_sequences")

# Create separated forward and reverse reads
print("Parsing forward vs. reverse reads for lanes\n")
for_vs_rev = {}
for key, value in files_per_samp.items():
    for_vs_rev[key] = {"Forward": [], "Reverse": []}
    for val in value:
        cols = re.split(r'[_.]', val)
        # Ensure files are gzipped
        if not cols[-1] == "gz":
            print("Please gzip your files before proceeding.")
            sys.exit()        
        # Assign forward vs reverse reads     
        if f_r_delim == "R":
            if "R1" in cols:
                for_vs_rev[key]["Forward"].append(val)
            elif "R2" in cols:
                for_vs_rev[key]["Reverse"].append(val)
            else: 
                print("1. Could not determine forward vs. reverse reads. Please consider renaming your files and try again.")
                sys.exit()
        elif f_r_delim == "_":
            if "1" in cols[-3]:
                for_vs_rev[key]["Forward"].append(val)
            elif "2" in cols[-3]:
                for_vs_rev[key]["Reverse"].append(val)
            else: 
                print("2. Could not determine forward vs. reverse reads. Please consider renaming your files and try again.")
                sys.exit()
        else:   
            print("3. Could not determine forward vs. reverse reads. Please consider renaming your files and try again.")
            sys.exit()

# Confirm merging looks correct (edited for renaming instead of merging)
for key, value in for_vs_rev.items():
    print(f"Sample: {key}")
    print("Forward reads:")
    for forward_read in value["Forward"]:
        print("\t", forward_read)
    print("Reverse reads:")
    for reverse_read in value["Reverse"]:
        print("\t", reverse_read)
    print()

proceed = input("Do the files look correctly parsed? (y/n) ")
if proceed.lower() == "no" or proceed.lower() == "n":
    print("Please consider renaming your files such that the forward and reverse strands are more clear and try again.")
    sys.exit()

# Merge lanes
print("Merging lanes")
for key, value in for_vs_rev.items():
   for direction, files in value.items():
       if direction == "Forward":
            source_files = " ".join(for_vs_rev[key]["Forward"])
            destination_file = f"{key}_1.fq.gz"
            os.system(f"cat {source_files} > 01_raw_sequences/{destination_file}")
       if direction == "Reverse":
            source_files = " ".join(for_vs_rev[key]["Reverse"])
            destination_file = f"{key}_2.fq.gz"
            os.system(f"cat {source_files} > 01_raw_sequences/{destination_file}")
           
print("Done merging lanes!")