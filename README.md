# Processing WGBS (Whole Genome Bisulfite Sequencing) Data

## Table of Contents

* [Updates](#updates)
* [Project Set-Up](#project-set-up)
	* [Setting Up Your Project Directory](#setting-up-your-project-directory)
	* [Installation](#installation)
* [1. `FASTQ_Me2`](#1-fastq_me2)
* [2. `CpG_Me2`](#2-cpg_me2)
	* [Running `CpG_Me2` Locally](#running-cpg_me2-Locally)
	* [Running `CpG_Me2` on SLURM (Recommended)](#Running-CpG_Me2-on-SLURM-Recommended)
* [Interpretting Outputs](#Interpretting-Outputs)
* [Acknowledgements](#acknowledgements)


## Updates

The original [CpG_Me](https://github.com/ben-laufer/CpG_Me), written by Dr. Ben Laufer, was intended to merge WGBS sequencing lanes and generate cytosine reports to be used in further analysis, such as in DMRichR and Comethyl. Upon trying the pipeline for the first time, I ran into some complications specific to my data (which was not downloaded from SLIMS), and I had the idea to make it more modular and a little easier to use for first-time users. Please note that my use of "local" below refers to `/share/lasallelab/` instead of SLURM. Here are some of the updates I made:

* `FASTQ_Me2` has been rewritten as a python script
* Locally downloaded sequencing data can now be used in `FASTQ_Me2`
* Users will only interact with command line prompts instead of adapting any of the scripts
* `CpG_Me2` can be run locally as a script instead of only through SLURM 
* `CpG_Me2` has been written as a snakemake file, yielding the following advantages:
    * Multi-threading of jobs can be handled locally or on SLURM
    * Jobs remove corrupted intermediate files if they fail
    * Snakemake's "memory" prevents re-running of samples and files that have already been generated

## Project Set-Up

### Setting Up Your Project Directory

When you are getting ready to start processing your WGBS samples, the first thing you should do is enter your home directory `/share/lasallelab/yourname` and clone the repository using your project name:

```
git clone https://github.com/vhaghani26/WGBS_workflow {project_name}
```

Enter the directory

```
cd {project_name}
```

### Installation

Run the following command in your project directory. It will clone the conda environment with all dependencies needed in order to run the workflow outlined here. This creates an environment called `wgbs`. If you would like to change the name, feel free to do so where the command says `wgbs`. Please note that this may take quite a few minutes to run.

```
conda env create -f 00_software/environment.yml --name cpg_me2
```

Activate your environment using

```
conda activate cpg_me2
```

Run everything downstream of this point in this conda environment. Note that you must activate this environment every time you restart your terminal.

**For LaSalle Lab**

The environment is already installed and ready in a shared space, so all you will need to do is run:

```
conda activate /share/lasallelab/programs/.conda/cpg_me2
```


## 1. `FASTQ_Me2`

When you receive your sequencing data, the sequencing lanes will need to be merged. FASTQ_Me2 handles the merging of lanes whether the data is maintained on SLIMS or local.

**SLIMS Data**

If your data is on SLIMS, you will be prompted for your SLIMS string and SLIMS directory. This triggers the data download in your project directory. It also computes the MD5 checksum and compares it to the expected checksum hashes to ensure that the files were not corrupted during download.

**Local Data**

If you've already downloaded your data onto Epigenerate, then you will be prompted to give the absolute path (i.e. starting from `/share/lasallelab/...`) to the raw data.

**Merging Lanes**

Once `FASTQ_Me2` has downloaded or located the data, it will ask some questions about the way your sequence files are named so that it can extrapolate the sample IDs and orientation of the reads (i.e. forward vs. reverse). It will ask for your confirmation along the way to make sure that your samples are being handled correctly. Shortly before merging, it will print out the merge commands (beginning with `cat`) that will be run. If anything is wrong with the way they look, you will need to rename or reorganize your sequence files or try re-entering the metadata in `FASTQ_Me2` until the correct merge commands appear. Once you confirm that the merges are correct, they will be carried out. `FASTQ_Me2` will also ask some information about your user information. This serves to set up a configuration file, `task_samples.yaml`, which contains your user metadata as well as project-specific information. This file gets read into `CpG_Me2` and helps with submission of individual jobs per sample.

**Running `FASTQ_Me2`**

To run `FASTQ_Me2`, all you need to do is run the following in your project directory:

```
python3 01_FASTQ_Me2.py
```

## 2. `CpG_Me2`

`CpG_Me2` carries out a number of steps to process your sample, which can be seen in the figure below.

![Workflow](https://github.com/ben-laufer/CpG_Me/blob/master/Examples/CpG_Me_Flowchart.png)

There are two ways that you can run `CpG_Me2`. 

### Running `CpG_Me2` Locally

Since all the information setup was done when you run `FASTQ_Me2`, all you have to do now is run the following to run `CpG_Me2`:

```
nice -n 10 snakemake -j 3 -p -s 02_CpG_Me2_PE
```

`nice -n 10` means you are assigning your job a lower priority than default jobs, which is good when you are using shared computer resources. The `-j` option for `jobs` means how many jobs are able to be run in parallel. We only have 64 CPUs on Epigenerate, so please be mindful not to use more than half without asking or warning other users in the Epigenerate Slack channel. Running roughly 3 jobs at once is relatively reasonable given our resource allocation since each job can take up to ~75 GB of RAM.

`CpG_Me2` has been written such that this is all you need to run for your job to run from start to finish. If, for some reason, you are disconnected from Epigenerate or your job fails, re-run the above command and it will pick up where it left off. It even deletes possibly corrupted files from where it was cut off to ensure ALL outputs are properly generated. 

Notice some issues here.

1. Because the alignment step uses so many resources, you are limited to running ~3 jobs at a time. When each sample requires 9 jobs, this can easily add up.
2. If you get disconnected from your terminal, your job fails. This means that you need to be logged in and have an active terminal for days at a time.

For the above reasons, it is HIGHLY recommended that you instead run it via SLURM. This is similar to what was initially written by Ben, where individual jobs get submitted to SLURM.

### Running `CpG_Me2` on SLURM (Recommended)

(coming as soon as I figure out how to make this work)

You will need to set up two files in order to run this workflow through slurm.

**1. `slurm-status.py`**

In your home directory, create a directory structure that reflects `~/.config/snakemake/slurm/`. Create a file called `slurm-status.py` in this directory and copy and paste the following into the file:

```
#!/usr/bin/env python

# Example --cluster-status script from docs:
# https://snakemake.readthedocs.io/en/stable/tutorial/additional_features.html#using-cluster-status

import subprocess
import sys

jobid = sys.argv[-1]

if jobid == "Submitted":
    sys.stderr.write("smk-simple-slurm: Invalid job ID: %s\n"%(jobid))
    sys.stderr.write("smk-simple-slurm: Did you remember to add the flag --parsable to your sbatch call?\n")
    sys.exit(1)

output = str(subprocess.check_output("sacct -j %s --format State --noheader | head -1 | awk '{print $1}'" % jobid, shell=True).strip())

running_status=["PENDING", "CONFIGURING", "COMPLETING", "RUNNING", "SUSPENDED"]
if "COMPLETED" in output:
    print("success")
elif any(r in output for r in running_status):
    print("running")
else:
    print("failed")


"""
#!/usr/bin/env python3
import subprocess
import sys
jobid = sys.argv[-1]
output = str(subprocess.check_output("sacct -j %s --format State --noheader | head -1 | awk '{print $1}'" % jobid, shell=True).strip())
running_status=["PENDING", "CONFIGURING", "COMPLETING", "RUNNING", "SUSPENDED", "PREEMPTED"]
if "COMPLETED" in output:
  print("success")
elif any(r in output for r in running_status):
  print("running")
else:
  print("failed")
"""
```

**2. `config.yaml`**

In the same directory as `slurm-status.py` (i.e. `~/.config/snakemake/slurm/`), create a file called `config.yaml`. The only thing you will need to change is the `conda_prefix` (the third to last line). It looks something like `/software/anaconda3/4.8.3/lssc0-linux/`, `/home/vhaghani/anaconda3/`, or `/share/lasallelab/programs/.conda/`.

```
cluster:
  mkdir -p logs/{rule}/ &&
  sbatch
    --cpus-per-task={threads}
    --mem={resources.mem_mb}
    --time={resources.time}
    --job-name=smk-{rule}
    --ntasks={resources.nodes}
    --nodes={resources.nodes}
    --output=logs/{rule}/{jobid}.out
    --error=logs/{rule}/{jobid}.err
    --partition={resources.partition}
    --parsable
default-resources:
  - mem_mb=2000
  - time=60
  - partition=low2
  - threads=1
  - nodes=1
jobs: 50
latency-wait: 60
local-cores: 1
restart-times: 3
max-jobs-per-second: 50
max-status-checks-per-second: 20
keep-going: True
rerun-incomplete: True
printshellcmds: True
scheduler: greedy
use-conda: True
conda-prefix: {conda_prefix}
conda-frontend: conda
cluster-status: ~/.config/snakemake/slurm/slurm-status.py
```

## Interpretting Outputs

The most important outputs you will find are `01_raw_sequences/` and `08_cytosine_reports/`. You can feel free to delete the intermediate files, but they are included for your reference in case something goes wrong when you try to run `CpG_Me2`. The `03_screened` and `09_multiqc` directories may also be good to keep so you can check on the qualities of your samples at various stages. Below is a description of each of the output directories and what is contained in each. Note that the numbers preceding the directory names are reflective of the order they were generated.

### `00_std_err_logs/`

This directory contains the standard error per job per sample. If, for some reason, you encounter an error for a sample, this allows you to view the full error message and debug.

### `00_time_logs/`

This directory documents the time it took each job to run. This could help inform future decisions about time allocations in SLURM should you need to adjust the time for a submitted job.

### `01_raw_sequences/`

This directory contains the merged sequences for each sample, separated into forward (`{sample}_1.fq.gz`) and reverse (`{sample}_2.fq.gz`) reads.

### `02_trimmed/`

This contains the reads after they have been trimmed, meaning that the adapters and low quality base pairs at sequence ends have been removed.

### `03_screened/`

All samples are screened against some different background genomes to determine sample read origins. This could be helpful if you are concerned about possible contamination of your samples.

### `04_aligned/`

This directory contains the aligned sequences, meaning that samples are mapped against your reference genome.

### `05_deduplicated/`

This contains your reads with PCR duplicates removed.

### `06_sorted/`

This contains your aligned and deduplicated sequence reads sorted in chromosome coordinate order.

### `06_nt_coverage/`

Nucleotide coverage of reads are calculated for input BAM files and output here.

### `06_methylation/`

This contains the various outputs of Bismark associated with extracting methylation information from each sample.

### `07_size_metrics/`

According to the documentation, this "provides useful metrics for validating library construction including the insert size distribution and read orientation of paired-end libraries." 

### `08_cytosine_reports/`

This directory contains the cytosine reports that are required for downstream analysis.

### `09_multiqc/`

This contains quality read outs for the eligible files maintained in the other directories. It can be helpful to view if any of your samples are being problematic.

## Acknowledgements

This work was largely adapted from Dr. Ben Laufer's original [CpG_Me Program](https://github.com/ben-laufer/CpG_Me). These updates could not have been made without the help of Jules Mouat and Aron Mendiola.