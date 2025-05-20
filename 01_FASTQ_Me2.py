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
    
###################
## Assign Genome ##
###################

# Determine genome
genome = input("Please input the primary genome you will align your files to. This will need to match the name of the genome subdirectory you created in 01_genomes/ ")

print("\n")

#########################
## Identify Data Files ##
#########################

# Determine unique data files
raw_files = []
first_file_dir = None

for path, subdirs, files in os.walk(data_dir):
    for name in files:
        # Check if the file has the correct extension
        if name.endswith('fastq.gz') or name.endswith('fq.gz'):
            full_file_path = os.path.join(path, name)
            
            # If this is the first file, store its directory
            if first_file_dir is None:
                first_file_dir = path
            
            # Check if the current file's directory matches the first file's directory
            if path != first_file_dir:
                print("Error: All files must be in the same directory. Please move all files to the same directory and try again.")
                sys.exit(1)
            
            # Append only the file name to the raw_files list
            raw_files.append(os.path.basename(full_file_path))

# Get sample IDs
sample_ids = []
for file in raw_files:
    # Remove file extension and read direction
    if file.endswith("_1.fq.gz") or file.endswith("_2.fq.gz"):
        file = file[:-8]
    elif file.endswith("_1.fastq.gz") or file.endswith("_2.fastq.gz"):
        file = file[:-11]
    elif file.endswith("_R1.fq.gz") or file.endswith("_R2.fq.gz"):
        file = file[:-9]
    elif file.endswith("_R1.fastq.gz") or file.endswith("_R2.fastq.gz"):
        file = file[:-12]
    elif file.endswith("_R1_001.fq.gz") or file.endswith("_R2_001.fq.gz"):
        file = file[:-13]    
    elif file.endswith("_R1_001.fastq.gz") or file.endswith("_R2_001.fastq.gz"):
        file = file[:-16]
    # Add sample ID
    sample_ids.append(file)

# Convert to set to get only unique values (since F/R reads have same sample ID)
sample_ids = set(sample_ids)
 
# Verify that the sample IDs are correct    
for samp in sample_ids:
    print(samp)

print("\n")

samp_names = input("Please check the sample IDs above. This should include lane information if you have multiple lanes. Are they correct? (y/n) ")
if samp_names.lower() == "no" or samp_names.lower() == "n":
    print("An error has occured. Please try entering your project metadata again.")
    sys.exit()  

print("\n")

######################
## Make Config File ##
######################

# Remove task_samples.yaml if it already exists
isExist = os.path.isfile("task_samples.yaml")
if isExist:
    os.system("rm -f task_samples.yaml")

# Create task_samples.yaml 
print("Creating task_samples.yaml, which will contain a list of file names to be used in the rest of the pipeline")
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