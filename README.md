# Epigenerator: A Practical Workflow for Whole Genome Bisulfite Sequencing (WGBS) Analysis

**Please note that currently, this is only compatible with the UC Davis Genome Center HPC. Updates are being made to make it more available for other users**

## Table of Contents

* [Updates](#updates)
* [Project Set-Up](#project-set-up)
	* [Setting Up Your Project Directory](#setting-up-your-project-directory)
	* [Installation](#installation)
	* [Genome Preparation](#genome-preparation)
* [1. `FASTQ_Me2`](#1-fastq_me2)
* [2. `CpG_Me2`](#2-cpg_me2)
	* [Running `CpG_Me2` Locally](#running-cpg_me2-Locally)
	* [Running `CpG_Me2` on SLURM (Recommended)](#Running-CpG_Me2-on-SLURM-Recommended)
* [Interpretting Outputs](#Interpretting-Outputs)
* [Acknowledgements](#acknowledgements)


## Updates

The original [CpG_Me](https://github.com/ben-laufer/CpG_Me), written by Dr. Ben Laufer, was intended to merge WGBS sequencing lanes and generate cytosine reports to be used in further analysis, such as in DMRichR and Comethyl. Upon trying the pipeline for the first time, I ran into some complications specific to my data (which was not downloaded from SLIMS), and I had the idea to make it more modular and a little easier to use for first-time users. Here are some of the updates I made:

* `FASTQ_Me2` has been rewritten as a python script
* Locally downloaded sequencing data can now be used in `FASTQ_Me2`
* Users will only interact with command line prompts instead of adapting any of the scripts
* `CpG_Me2` can be run locally (i.e. on screen or at your terminal) as a script instead of only through SLURM 
* `CpG_Me2` has been written as a snakemake file, yielding the following advantages:
    * Multi-threading of jobs can be handled locally or on SLURM
    * Jobs remove corrupted intermediate files if they fail
    * Snakemake's "memory" prevents re-running of samples and files that have already been generated

## Project Set-Up

### Setting Up Your Project Directory

Clone the repository using your project name in the directory you plan to host the project:

```
git clone https://github.com/vhaghani26/WGBS_workflow {project_name}
```

Enter the directory

```
cd {project_name}
```

### Installation

Run the following command in your project directory. It will clone the conda environment with all dependencies needed in order to run the workflow outlined here. This creates an environment called `epigenerator`. If you would like to change the name, feel free to do so where the command says `epigenerator`. Please note that this may take quite a few minutes to run.

```
conda env create -f 00_software/environment.yml --name epigenerator
```

Activate your environment using

```
conda activate epigenerator
```

Run everything downstream of this point in this conda environment. Note that you must activate this environment every time you restart your terminal.

**For LaSalle Lab**

The environment is already installed and ready in a shared space, so all you will need to do is run:

```
conda activate /share/lasallelab/programs/.conda/epigenerator
```

### Genome Preparation

**1. `01_genomes/` Setup

Several steps require genomes for alignment. One of the steps, FastQ-Screen, allows you to align your reads to multiple genomes to check for sources of contamination. In your project directory, create a subdirectory called `01_genomes/`:

```
mkdir 01_genomes/
```

Within `01_genomes/`, create subdirectories corresponding to each genome of interest. The directory structure should look something like the following:

```
project_directory/
	01_genomes/
		hg38/
		Lamba/
		mm10/
		PhiX/
		rheMac10/
		rn6/
```

Each subdirectory containing your genome of interest should contain the appropriate genome files as described by the [FastQ-Screen documentation](https://stevenwingett.github.io/FastQ-Screen/). Please do not worry about downloading or installing FastQ-Screen. The environment you created has all the software you will need. Activate the environment you created in the previous section, download the reference genome, and index the reference genome using [Bowtie2](https://bowtie-bio.sourceforge.net/bowtie2/manual.shtml#indexing-a-reference-genome).

**2. `fastq_screen.conf` Setup

In the directory `00_software`, locate and open the file `fastq_screen.conf`. Change lines 34+ to reflect the genomes and location of the genomes that you are aligning to. Provided paths can be absolute or relative paths.

**For LaSalle Lab**

Create `01_genomes/`:

```
mkdir 01_genomes
```

Change into the directory:

```
cd 01_genomes
```

Run the following commands to link our standard genome directories into this directory:

```
ln -s /share/lasallelab/genomes/hg38/ .
ln -s /share/lasallelab/genomes/Lambda/ .
ln -s /share/lasallelab/genomes/mm10/ .
ln -s /share/lasallelab/genomes/PhiX/ .
ln -s /share/lasallelab/genomes/rheMac10/ .
ln -s /share/lasallelab/genomes/rn6/ .
```

You do not need to update `fastq_screen.conf`. 

## 1. `FASTQ_Me2`

If you have more than one lane of data, the sequencing lanes will need to be merged. FASTQ_Me2 handles the merging of lanes whether the data is maintained on SLIMS or already downloaded on your system (i.e. local).

**SLIMS Data**

If your data is on SLIMS, you will be prompted for your SLIMS string and SLIMS directory. This triggers the data download in your project directory. It also computes the MD5 checksum and compares it to the expected checksum hashes to ensure that the files were not corrupted during download.

**Local Data**

If you've already downloaded your data, you will be prompted to give the absolute path to the raw data.

**Merging Lanes**

Once `FASTQ_Me2` has downloaded or located the data, it will ask some questions about the way your sequence files are named so that it can extrapolate the sample IDs and orientation of the reads (i.e. forward vs. reverse). It will ask for your confirmation along the way to make sure that your samples are being handled correctly. If you only have one lane, you can either (1) proceed with the merging, which effectively duplicates your data, but handles all of the naming and organization for you or (2) rename your samples in the format of `{sample}_1.fq.gz` and `{sample}_2.fq.gz` and place them in a directory called `01_raw_sequences/`. If you have more than one lane, you should proceed with merging so that the data input structure is compatible with `CpG_Me2`. Shortly before merging, `FASTQ_Me2` will print out the merge commands (beginning with `cat`) that will be run. If anything is wrong with the way they look, you will need to rename or reorganize your sequence files or try re-entering the metadata in `FASTQ_Me2` until the correct merge commands appear. Once you confirm that the merges are correct, they will be carried out. `FASTQ_Me2` will generate a configuration file, `task_samples.yaml`, that gets read into `CpG_Me2`. This `task_samples.yaml` file is **required** before running `CpG_Me2`. 

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

Since all the information setup was done when you run `FASTQ_Me2`, all you have to do now is run the following to run `CpG_Me2` from start to finish:

```
snakemake -j 1 -p -s 02_CpG_Me2_PE
```

The `-j` option for `jobs` means how many jobs are able to be run in parallel. The most resource-intensive step uses ~50-100 GB of RAM per sample, so be mindful of the resources you have available if you choose to run more than one job at a time. If, for some reason, you are disconnected from your terminal or your job fails, re-run the above command and it will pick up where it left off. It even deletes possibly corrupted files from where it was cut off to ensure ALL outputs are properly generated. 

Notice some issues here.

1. Because the alignment step uses so many resources, you are limited by the number of jobs you can run at the same time due to required resource allocations
2. If you get disconnected from your terminal, your job fails. This means that you need to be logged in and have an active terminal for days at a time. This can be circumvented by running `CpG_Me2` in `screen`, but you will still need the proper resource allocation for that length of time.

For the above reasons, it is HIGHLY recommended that you instead run it via SLURM. This is similar to what was initially written by Ben, where individual jobs get submitted to SLURM.

### Running `CpG_Me2` on SLURM (Recommended)

In the directory `00_slurm/`, there is a file named `config.yaml`. You will need to modify two things:

1. Update your SLURM partition for the **two** lines (line 12 and line 17) containing `--partition` by inputting a string. This will look something like `--partition=production` 
2. Change the `conda_prefix` (line 31). It should look something like `/software/anaconda3/4.8.3/lssc0-linux/`, `/home/vhaghani/anaconda3/`, or `/share/lasallelab/programs/.conda/`

Once you have updated `config.yaml`, go back to your project directory. Snakemake manages the submission of jobs, so wherever you run it, it will need to stay open. As such, I recommend running it in [screen](https://linuxize.com/post/how-to-use-linux-screen/). Activate the conda environment (confirm you are in the environment if you are using screen).  When you are ready, run:

```
snakemake -s 02_CpG_Me2_PE --profile 00_slurm/
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