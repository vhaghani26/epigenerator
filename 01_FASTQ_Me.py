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

#########################
## Download SLIMS Data ##
#########################

# Set location variable 
data_location = data_location.lower()

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
    
##############################################
## Start Merging Lanes for SLIMS/Local Data ##
##############################################

# Determine forward vs. reverse read notation  
f_r_delim = input("Does your data separate forward and reverse reads using the R1/R2 system or _1/_2 system? (R/_) ")

while f_r_delim != "R" and f_r_delim != "_":
    print("Please specify the system using either R for the R1/R2 system or _ for the _1/_2 system.")
    f_r_delim = input("Does your data separate forward and reverse reads using the R1/R2 system or _1/_2 system? (R/_) ")

# Determine delimiter for sample IDs
samp_id_delim = input("In most cases, your sample ID will be followed (i.e. delimited by) an underscore. Is this true for your data? (y/n) "

if samp_id_delim.lower() == "no" or samp_id_delim.lower() == "n":
    samp_id_delim = input("What is your delimiter (i.e. what character separates your sample ID from the rest of the file name)?" )
else:
    samp_id_delim = "_"
    
print(samp_id_delim)

#"What delimiter (i.e. character) separates your sample ID from the rest of the file name? In most cases, it will be an underscore: _.  

os.system("echo 'Checking for the right number of unique sample IDs for the forward and reverse reads'")
#os.sytem(f"countFASTQ(){awk -F '_' '{print $1}' | sort -u | wc -l }")
