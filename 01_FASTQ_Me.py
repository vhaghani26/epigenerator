#!/bin/bash python3 

import sys
import os

# Ensure user is in proper working directory.
proper_dir = input("Are you currently in your project directory? (y/n) ")

if proper_dir.lower() == "no" or proper_dir.lower() == "n":
    print("Please make your project directory using 'mkdir project_name' and enter it using 'cd project_name' and then try again.")
    sys.exit()

# Determine if data is maintained locally or on SLIMS
data_location = input("Is your data maintained on SLIMS or locally downloaded? (slims/local) ")

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

    # Start download
    os.system(f"echo 'Downloading fastq files for {SLIMSstring}'")
    os.system(f"rsync -avL slimsdata.genomecenter.ucdavis.edu::slims/{SLIMSstring}/ .")

    # Confirm proper transfer
    os.system(f"Carrying out MD5 Checksum to ensure that the files have properly transferred")
    os.chdir(f"{SLIMSdir}")    
    
    # Move undetermined files
    os.system("echo 'Moving undetermined files'")
    newpath = 'Other'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.system("mv Undetermined* Other")
    
    # Determine forward vs. reverse read notation  
    f_r_delim = input("Does your data separate forward and reverse reads using the R1/R2 system or _1/_2 system? (R/_) ")
    
    while f_r_delim != "R" and f_r_delim != "_":
        print("Please specify the system using either R for the R1/R2 system or _ for the _1/_2 system.")
        f_r_delim = input("Does your data separate forward and reverse reads using the R1/R2 system or _1/_2 system? (R/_) ")
    
    # Determine delimiter for sample IDs
    samp_id_delim = input("In most cases, your sample ID will be followed (i.e. delimited by) an underscore. Is this true for your data? If you are unsure, the answer is likely yes. (y/n) ")
    
    if samp_id_delim.lower() == "no" or samp_id_delim.lower() == "n":
        samp_id_delim = input("What is your delimiter (i.e. what character separates your sample ID from the rest of the file name)? ")
    else:
        samp_id_delim = "_"
    
    os.system("echo 'Checking for the right number of unique sample IDs for the forward and reverse reads'")
    os.system(f"countFASTQ(){{awk -F '{samp_id_delim}' '{{print $1}}' | sort -u | wc -l }}'")

################
## Local Data ##
################

# Set data_location variable to 'slims' if slims 
if data_location[1:-1] == 'local':
    data_location = data_location[1:-1]

if data_location == 'local':
    raw_data = input("What is the absolute path that contains your raw data? ")
    
    # Ensure that path exists
    isExist = os.path.exists(raw_data)
    while not isExist:
        raw_data = input("This directory could not be found. Please check to make sure that the directory is correct and try again: ")
        isExist = os.path.exists(raw_data)

    # Determine forward vs. reverse read notation  
    f_r_delim = input("Does your data separate forward and reverse reads using the R1/R2 system or _1/_2 system? (R/_) ")

    while f_r_delim != "R" and f_r_delim != "_":
        print("Please specify the system using either R for the R1/R2 system or _ for the _1/_2 system.")
        f_r_delim = input("Does your data separate forward and reverse reads using the R1/R2 system or _1/_2 system? (R/_) ")

    # Determine delimiter for sample IDs
    samp_id_delim = input("In most cases, your sample ID will be followed (i.e. delimited by) an underscore. Is this true for your data? If you are unsure, the answer is likely yes. (y/n) ")

    if samp_id_delim.lower() == "no" or samp_id_delim.lower() == "n":
        samp_id_delim = input("What is your delimiter (i.e. what character separates your sample ID from the rest of the file name)? ")
    else:
        samp_id_delim = "_"

    print('Checking for the right number of unique sample IDs for the forward and reverse reads')
    
    # Add all data files to list
    raw_files = {}
    for path, subdirs, files in os.walk(raw_data):
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
        
    # Verify that the sample IDs are correct    
    for samp in sample_ids:
        print(samp)
    
    samp_names = input("Please check the sample IDs above. Are they correct? (y/n) ")
    if samp_num.lower() == "no" or samp_num.lower() == "n":
        print("An error has occured. Please try entering your project metadata again.")
        sys.exit()  
    
    # Remove task_samples.txt if it already exists
    isExist = os.path.isfile("task_samples.txt")
    if isExist:
        os.system("rm -f task_samples.txt")
    
    # Create task_samples.txt 
    print("Creating task_samples.txt, which will contain all unique sample IDs and get used in further analysis.")
    file = "task_samples.txt"
    os.system(f"touch {file}")
    # Saving reference of standard output
    original_stdout = sys.stdout
    # Write sample IDs into task_samples.txt
    with open(file, "a") as f:
        sys.stdout = f
        for samp in sample_ids:
            print(samp)
    # Reset standard output
    sys.stdout = original_stdout
    
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
    
    # Begin process of merging lanes
    # Make raw_sequences directory
    isExist = os.path.exists("raw_sequences")
    if not isExist:
        os.system("mkdir raw_sequences")
    
    # Check file extension
    ext = input("What is your sequence file extension? (fq.gz/fastq.gz) ")
    while ext.lower() != "fq.gz" and ext.lower() != "fastq.gz":
        print("Please specify your sequence extension. Your files should end with either 'fq.gz' or 'fastq.gz'.")
        ext = input("What is your sequence file extension? (fq.gz/fastq.gz) ")
    
    print(f_r_delim, ext.lower())
    
    # Confirm merges look correct
    for key, value in files_per_samp.items():
        if f_r_delim == "R" and ext.lower() == "fq.gz":
            os.system(f"echo")
        elif f_r_delim == "R" and ext.lower() == "fastq.gz":
            print("2")
        elif f_r_delim == "_" and ext.lower() == "fq.gz":
            os.system(f"echo {print(*value)}")
        elif f_r_delim == "_" and ext.lower() == "fastq.gz":
            print("4")
        else:
            print("5")
            
#cat ${i}\_*_R1_001.fastq.gz \> ${i}\_1.fq.gz

# val in value is file path

####################################
## Handle Incorrect Data Location ##
####################################

else:
    print("Please try again with either 'slims' or 'local'.")