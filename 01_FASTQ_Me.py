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
    
######################
## Identify Samples ##
######################

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

######################
## Make Config File ##
######################

# Determine genome
genome = input("Please select the genome you would like to align your files to. (hg19/hg38/mm10/GRCm38) ")
while genome != "hg38" and genome != "mm10" and genome != "hg19" and genome != "GRCm38":
    print("You must select hg19, hg38, mm10, or GRCm38. Please try again.")
    genome = input("What genome are you using? (hg19/hg38/mm10/GRCm38) ")

print("\n")

# Incorporate further configuration information
print("The following questions are going to help create the configuration file to be used and submitted in CpG_Me.")

print("\n")

user = input("What is your username on the Cluster? This can be determined by running 'echo $USER' at the terminal if you are unsure. ")

print("\n")

mail_type = input("When jobs are submitted for CpG_Me, would you like to be notified when a job begins, ends, fails, or all of the above? If you want the least notifications as possible, the best choice would be 'FAIL'. (BEGIN/END/FAIL/ALL) ")
while mail_type != "BEGIN" and mail_type != "END" and mail_type != "FAIL" and mail_type != "ALL":
    mail_type = input("Make sure you are using all uppercase letters. Would you like to be notified when a job begins, ends, fails, or all of the above? (BEGIN/END/FAIL/ALL) ")

print("\n")
    
mail_user = input("What email would you like to receive notifications at? ")

print("\n")

partition = input("What partition are you using when you submit jobs to SLURM? If you do not know, then use 'production'. ")

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
    print(f"user: {user}")
    print(f"mail_user: {mail_user}")
    print(f"mail_type: {mail_type}")
    print(f"partition: {partition}")
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
        if key.startswith(samp):                
            files_per_samp[samp].append(value)

# Save space
del raw_files
del sample_ids

#################
## Merge Lanes ##
#################

# Make 01_raw_sequences directory
print("Preparing to merge lanes")
isExist = os.path.exists("01_raw_sequences")
if not isExist:
    os.system("mkdir 01_raw_sequences")

# Create separated forward and reverse reads
print("Parsing forward vs. reverse reads for lanes")
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

# Confirm merging looks correct
for key, value in for_vs_rev.items():
   for direction, files in value.items():
       if direction == "Forward":
           print("cat", " ".join(for_vs_rev[key]["Forward"]), f"> {key}_1.fq.gz")
       elif direction == "Reverse":
           print("cat", " ".join(for_vs_rev[key]["Reverse"]), f"> {key}_2.fq.gz")
       else:
           print("Could not determine forward vs. reverse reads. Please consider renaming your files and try again.")
           sys.exit()

proceed = input("Do the above merges look correct? (y/n) ")
if proceed.lower() == "no" or proceed.lower() == "n":
    print("Please consider renaming your files such that the forward and reverse strands are more clear and try again.")
    sys.exit()

# Merge lanes
print("Merging lanes")
for key, value in for_vs_rev.items():
   for direction, files in value.items():
       if direction == "Forward":
           os.system(f"cat {' '.join(for_vs_rev[key]['Forward'])} > 01_raw_sequences/{key}_1.fq.gz")
       if direction == "Reverse":
           os.system(f"cat {' '.join(for_vs_rev[key]['Reverse'])} > 01_raw_sequences/{key}_1.fq.gz")
           
print("Done merging lanes!")