#!/bin/bash python3 

import os

# Prepare user
print("Please ensure that you are in your project directory before proceeding. If you are not, please make your project directory using 'mkdir project_name' and enter it using 'cd project_name'.")

# Determine if data is maintained locally or on SLIMS
data_location = input("Is your data maintained on SLIMS or locally downloaded? Please answer with 'slims' or 'local': ")

#########################
## Download SLIMS Data ##
#########################

# Set data_location variable to 'slims' if slims 
data_location = data_location.lower()

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
    
#######################
## Handle Local Data ##
#######################
