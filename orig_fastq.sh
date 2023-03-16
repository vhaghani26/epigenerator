genome=hg38
programsPATH=/share/lasallelab/programs

if md5sum -c \@md5Sum.md5
then
    echo
    echo "All files have the correct md5sum"
else
    echo "ERROR: Some files are corrupt or missing"
    exit 1
fi

echo "Merging lanes"



countFASTQ(){awk -F '_' '{print $1}' | sort -u | wc -l }
export -f countFASTQ

R1=`ls -1 *R1*.gz | countFASTQ`
R2=`ls -1 *R2*.gz | countFASTQ`

if [ ${R1} = ${R2} ]
then
        lanes=`ls -1 *R1*.gz | \
        awk -F '_' '{print $1}' | \
        sort | \
        uniq -c | \
        awk -F ' ' '{print $1}' | \
        sort -u`
        echo "${R1} samples sequenced across ${lanes} lanes identified for merging"
else
        echo "ERROR: There are ${R1} R1 files and ${R2} R2 files"
        exit 1
fi

echo "Creating a file of unique IDs based on first string from underscore delimiter"
ls -1 *fastq.gz | \
awk -F '_' '{print $1}' | \
sort -u > \
task_samples.txt

echo "Printing merge commands"
mergeLanesTest(){
	i=$1
	echo cat ${i}\_*_R1_001.fastq.gz \> ${i}\_1.fq.gz
	echo cat ${i}\_*_R2_001.fastq.gz \> ${i}\_2.fq.gz
}
export -f mergeLanesTest
cat task_samples.txt | parallel --jobs 6 --will-cite mergeLanesTest

echo "Merging ${lanes} lanes for ${R1} samples"
mergeLanes(){
	i=$1
	cat ${i}\_*_R1_001.fastq.gz > ${i}\_1.fq.gz
	cat ${i}\_*_R2_001.fastq.gz > ${i}\_2.fq.gz
}
export -f mergeLanes
cat task_samples.txt | parallel --jobs 6 --verbose --will-cite  mergeLanes

echo "Creating directories for CpG_Me"
mkdir ../../raw_sequences
mv task_samples.txt ../..
mv *.fq.gz ../../raw_sequences

echo "Checking read pairs"
cd ../../raw_sequences
pairedReads=$(($(ls | wc -l)/2))
if [ ${pairedReads} = ${R1} ]
then
        echo "${pairedReads} will be aligned using CpG_Me"
else
        echo "ERROR: Incorrect number of merged read pairs in raw_sequences"
        echo "There are ${pairedReads} but there should be ${R1}"
        exit 1
fi

echo "Submitting $genome alignment command to cluster for ${project}"
cd ..
