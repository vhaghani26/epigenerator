# Processing WGBS (Whole Genome Bisulfite Sequencing) Data

## Updates

The original [CpG_Me](https://github.com/ben-laufer/CpG_Me), written by Dr. Ben Laufer, was intended to merge WGBS sequencing lanes and generate cytosine reports to be used in further analysis, such as in DMRichR and Comethyl. Upon trying the pipeline for the first time, I ran into some complications specific to my data (which was not downloaded from SLIMS), and I had the idea to make it more modular and a little easier to use for first-time users. Please note that my use of "local" below refers to `/share/lasallelab/` instead of SLURM. Here are some of the updates I made:

* `FASTQ_Me` has been rewritten as a python script
* Locally downloaded sequencing data can now be used in `FASTQ_Me`
* Users will only interact with command line prompts instead of adapting any of the scripts
* `CpG_Me` can be run locally as a script instead of through SLURM or piecewise at the command line
* `CpG_Me` has been rewritten as a snakemake file, yielding the following advantages:
    * Multi-threading of jobs can be handled locally, increasing the speed at which samples can be processed
    * Jobs remove corrupted intermediate files if they fail
    * Snakemake's "memory" prevents re-running of samples and files that have already been generated

## Project Set-Up

### Setting Up Your Project Directory

When you are getting ready to start processing your WGBS samples, the first thing you should do is enter your home directory `/share/lasallelab/yourname` and clone the repository using your project name:

```
git clone https://github.com/vhaghani26/WGBS_workflow {project_name}
```


(expand here)


### Installing Necessary Software

Run the following command in your project directory. It will clone the conda environment with all dependencies needed in order to run the workflow outlined here. Please note that this may take quite a few minutes to run.

```
conda env create -f environment.yml --name {environment_name}
```

Activate your environment using

```
conda activate {environment_name}
```

Run everything downstream of this point in this conda environment. 


## 1. `FASTQ_Me`

When you receive your sequencing data, the sequencing lanes will need to be merged. FASTQ_Me handles the merging of lanes whether the data is maintained on SLIMS or local.

**SLIMS Data**

If your data is on SLIMS, you will be prompted for your SLIMS string and SLIMS directory. This triggers the data download in your project directory. It also computes the MD5 checksum and compares it to the expected checksum hashes to ensure that the files were not corrupted during download.

**Local Data**

If you've already downloaded your data onto Epigenerate, then you will be prompted to give the absolute path (i.e. starting from `/share/lasallelab/...`) to the raw data. 

**Merging Lanes**

Once `FASTQ_Me` has downloaded or located the data, it will ask some questions about the way your sequence files are named so that it can extrapolate the sample IDs and orientation of the reads (i.e. forward vs. reverse). It will ask for your confirmation along the way to make sure that your samples are being handled correctly. Shortly before merging, it will print out the merge commands (beginning with `cat`) that will be run. If anything is wrong with the way they look, you will need to rename or reorganize your sequence files or try re-entering the metadata in `FASTQ_Me` until the correct merge commands appear. Once you confirm that the merges are correct, they will be carried out. To run `FASTQ_Me`, all you need to do is run:

```
python3 01_FASTQ_Me.py
```

## 2. `CpG_Me`

After entering your metadata when running `FASTQ_Me`, everything is stored and maintained such that it can easily be read into `CpG_Me`. To run `CpG_Me`, you can run the following:

```
snakemake -j {jobs} -p -s 02_CpG_Me_PE_v2
```

The `-j` option for `jobs` means how many jobs are able to be run in parallel. We only have 64 CPUs on Epigenerate, so please be mindful not to use more than half without asking or warning other users in the Epigenerate Slack channel. Running roughly 16 jobs at once is relatively reasonable given our resource allocation. 

`CpG_Me` has been rewritten such that this is all you need to run for your job to run from start to finish. If, for some reason, you are disconnected from Epigenerate or your job fails, re-run the above command and it will pick up where it left off. It even deletes possibly corrupted files from where it was cut off to ensure ALL outputs are properly generated. 

## Acknowledgements

This work was largely adapted from Dr. Ben Laufer's original [CpG_Me Program](https://github.com/ben-laufer/CpG_Me).