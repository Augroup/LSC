# LSC: a long read error correction tool. It offers fast correction with high sensitivity.

# Getting Started
These simple steps will help you integrate LSC into your transcriptomics analysis pipeline.

* Read the LSC_requirements for running LSC.
* Download and set-up the LSC package.
* Follow the tutorial to see how LSC works on some example data.
* Read the manual if anything is unclear.
* You're ready, Happy LSCing!

# Latest publication
Kin Fai Au, Jason Underwood, Lawrence Lee and Wing Hung Wong 
Improving PacBio Long Read Accuracy by Short Read Alignment [Manuscript] 
PLoS ONE 2012. 7(10): e46679. doi:10.1371/journal.pone.0046679

# Latest News
04-11-2016: Major update version 2.0

*Updates:*
* Added Command line argument support.
* Multi-stage execution modes.
* Support for parallelization. Now execution proceeds in batches of long reads the size of which can be set by --long_read_batch_size N.
* Better compressed intermediate files.
* Added utilities folder.
* Added support for multiple short read files.
* Removed use of configuration file.
* Removed support for BWA, RazerS3, and Novoalign. We are happy to support these if there is interest so please contact us if you prefer them over bowtie2. Bowtie2 is the prefered supported aligner in this release.
* Removed the requirement for long reads to be in PacBio format.

**02-02-2015: Minor updates and bug fixes LSC 1.beta**

*Feature Updates:*

* Updating aligners default command options to gain better performance.
	* Updated Novoalign command options (tested with >= novocraftV3.02.04 version)
	* Updated RazerS3 command options to be compatible with latest version (razers3 3.1.1)
* Added extra clean_up option value to remove all generated intermiediate files in case of issues w/ disk space

*Bug Fixes:*

* Fix a bug in generating full_LR.fa sequences causing some full read sequences to miss couple of bases
 
 12-01-2013: Faster and much less memory-required LSC 1.alpha is released
 
In the LSC 0.3.0 or 0.3.1, we optimized the setting of bowtie2 and BWA to get much more short read alignment, which improve the the accuracy of error correction a lot/ However, the increase of alignments also requires much more running time (on both alignment and the following error correction step) and memory usage. Therefore, a few users met difficulty of running LSC 0.3.0 or 0.3.1.

In LSC 1.alpha, we apply probabilistic algorithm ("SCD" option) to select ""enough" short read alignment for error correction. LSC 1.alpha does NOT sacrifice the error correction performace (sensitivity and specificity). Please see http://www.augroup.org/LSC/LSC_manual.html#aligner Thus, we save running time and memory usage significantly. The running time is 30-50% of LSC 0.3.1. The peak memory usage decreases to ~10G regardless of the data size.

*New features:*

* Added probabilistic algorithm ("SCD" option) to pre-select SR alignments results based on LR-SR alignment coverage depth (Significant improvement in running time and memory usage)
* Removed requirement for loading SR dataset in memory to generate LR-SR mapping file (Significant improvement in memory usage)
* Added option "sort_max_mem" in run.cfg to control maximum memory used by unix sort command to avoid unexpected Mem crash

*Miscellaneous changes:*
* Fixed a bug in generating FASTQ file (it affected some of QualityValue computation results)

If you want to see the manual and tutorial of the old LSC (before 1.alpha), we keep the links of its the Old manual and Old tutorial in the right side bar.

**09-30-2013: More robust and faster LSC 0.3.1**

In LSC 0.3.1, we don't have pseudo chromosome, the alignment time reduced to ~10% (in Bowtie2 mode). And you can re-run some crashed jobs easily now.

*New features:*

* Remove pseudo-chr processing
* Accept compressed SR as input (should be named SR.fa.cps/SR.fa.cps.idx in any folder)
* Added "runLSC -cleanup" option to remove redundant files (per thread split, remaining _tmp files) if the run was successful at the end.
* Changed convertNav to sort reads and then generate LR_SR.map (memory optimization instead of loading all alignments in memory)

*Miscellaneous changes:*

* Changed "print" to system.echo (messages were not printed out in qsub output files)
* Changed a little bit "cleanup" option to keep per thread data (*.aa, *.ab, ..). It was useful when one thread was crashed and we wanted to just re-run that at the end
 
**08-07-2013: Big changes in LSC 0.3**
 
In LSC 0.3, we have a few updates. They are very IMPORTANT updates, new features and small fixes

*Very IMPORTANT updates:*

* Support for Bowtie2 and RazerS3 as initial aligners. Now, BWA, Bowtie2, RazerS3 and Novoalign work in LSC. Please see the comparison details of aligners in the "Short read - Long read aligner#manual".
* Added SR length coverage percentage on LR (SR-covered length/full length of corrected LR) to corrected_LR output file. Here is an example, where the last number 0.82 is the SR length coverage percentage on LR:
```>m111006_202713_42141_c100202382555500000315044810141104_s1_p0/18941/365_1361|0.82```
* Added support for three modes for step-wise runs:

	mode 0: end-to-end
	
	mode 1: generating LR_SR.map file
	
	mode 2: correction step
	
* Generating FASTQ output format based on correction probability given short read coverage. Please refer to LSC paper and manual page for more details. You can select well-corrected reads for downstream analyses by using the quality in FASTQ output or SR length coverage percentage above. Please the the filtering in the "Output#manual".

*New features:*

* Used the python path in the cfg file instead of default user/bin path
* Added option (-clean_up) to remove intermediate files or not (Note: important/useful ones will still be there in temp folder)
* Support for input fastq format for LR (long reads) and/or SR (short reads)
* Updated default BWA and novoalign commands options
* Printing out original LR names in the output file
* Support for printing out version number using -v/-version option

*Small bug fixed:*

* Fixed in removing XZ pattern printed out at the end of some uncorrected_LR sequences
* Fixed samParser bug (which was ignoring some valid alignments in BWA output)

**06-09-2013: BWA is accepted in LSC 0.2.4**
 
We use a short read aligner in the first step of LSC. By default, Novoaligner is used. You can use BWA to run this process as well, which could be much faster. Please find the new aligner options in the webpage ".cfg file format"

The default settings of Novoalign options are:
	```-r All -F FA  -n 300 -o sam -o FullNW ```
    
The default settings of BWA options are:
	```-n 0.08 -o 10 -e 3 -d 0 -i 0 -M 1 -O 1 -E  1 -N ```
    
You can change these aligner setting. The details of these options can be found in the aligners' home page.
In addition, a bug is fixed:

some uncertain corrections may exist at the right ends of the long reads in the old LSC. LSC 0.2.4 settles this problem and likely improves the accuracy further.

**02-06-2013: a bin path bug is fixed in LSC 0.2.2**
If you run LSC at the bin folder (the bin folder is the work directory) or set the bin as the default path, then you may meet this bug. LSC 0.2.3 fixes this bug of finding the correct bin folder. You can download the LSC 0.2.3 
 
**10-17-2012: LSC 0.2.2 Released and a RemoveBothTail bug is fixed**
LSC 0.2.2 fixes the bug of the option "I_RemoveBothTails". LSC 0.2.1 ran this option even if you set "N". It may halt the process in LSC 0.2.1 because the read name does not allow "RemoveBothTails". Now you can choose to use this option or not. 
 
**10-13-2012: The manual and a tutorial are released**
The manual is released and you can also learn LSC by running the example in the tutorial. 
 
**10-4-2012: LSC paper is released**
Kin Fai Au, Jason Underwood, Lawrence Lee and Wing Hung Wong 
**Improving PacBio Long Read Accuracy by Short Read Alignment**
 
**8-12-2012 - LSC 0.2.1 Released**
LSC 0.2.1 fixes the bug of python path. Another bug of removing redundant reads is also fixed. LSC takes a long read data sets (>=100bp) and a short reads data sets (50 - 100bp) as input. They should be in FASTA format. Running time is almost linear with the the number of threads.

* Python (version 2.6 or higher) should be installed in the default user bin "#!/usr/bin/python"
* Novoalign should be in your default path. The version V2.07.10 is recommended.
* A new option of using nonredandunt reads that save ~40% running time

**8-7-2012: some bugs are found**

* Great thanks to Hans Jansen@SEQanswers for testing LSC 0.2. Some bugs of python and novoalign path setting will be fix in the coming verison very soon. The thread in SEQanswers may be helpful for your questions: http://seqanswers.com/forums/showthread.php?p=80859#post80859

If you need to run LSC 0.2 now, please add novoalign in your default path and change the first lines of all scripts 
"#!/home/stow/swtree/bin/python2.6" to "#!/usr/bin/python".

**5-2-2012: LSC 0.2 Released**
LSC 0.2 takes a long read data sets (>=100bp) and a short reads data sets (50 - 100bp) as input. They should be in FASTA format. Running time is almost linear with the the number of threads.

* More optional for raw data prefilter
* Multi-threading is available
* Reduced redundant temp files
For detailed information about this release, please see the release notes.

# Release notes

**LSC 2.0 - Release Notes**

* Removed the requirement for long reads to be in a Pacific Biosciences format.
* Removed PacBio specific long read processing.
* Removed support for aligners BWA, RazerS3 and Novoalign. Please contact us if these would be useful.
* Removed the use of run.cfg files.
* Removed support for Mac OSX. Nothing specifically was written to specifically disable Mac functionality, but use on Mac OSX functionality has not been tested for this version and should not be expected to function.
* Added command line argument support. runLSC.py could minimally be run with --long_reads and --short_reads and --output specified. Access to other parameters are available through command line arguments.
* Added a multi-stage execution modes. This makes parallelization on a cluster much easier to implement.

	0: default – end to end run
	
	1: Prepare compressed short reads, and compressed and indexed batches of long reads.
	
	2: Execute correction on all the batches. or (alternate) use --parallelized_mode_2 X: Execute correction on one batch (X).
	3: Combine outputs from mode 2 to produce final outputs.
	
* Added the parameter --long_read_batch_size X option so that you can specify how many long reads will be corrected in each batch.
* Added support for hisat, but parameters have not been optimized and bowtie2 performs best.
* Added samtools as a requirement, that is also included as a linux executable binary. If the software is not installed under 'samtools' or specified by the user, then the packaged version of samtools will be used. This drastically reduces the size of intermediate files produced from alignments.
* Added options for a specific temporary directory --specific_tempdir that can be used to specify where to store intermediate files if you want to keep them. This parameter is required when running in step-by-step modes i.e. 1,2,3 rather than just 0. Otherwise --tempdir can be used to specify where to store temporary files that will eventually be removed. If neither are specified the /tmp directory will be used by default.
* Added a utilities folder. Now it is the new home of filter_corrected_reads.py, and some sequence parsing files called by the main LSC program.

**LSC 1.beta - Release Notes** 

*Feature Updates:*

* Updating aligners default command options to gain better performance.
	* Updated Novoalign command options (tested with >= novocraftV3.02.04 version)
	* Updated RazerS3 command options to be compatible with latest version (razers3 3.1.1)
* Added extra clean_up option value to remove all generated intermiediate files in case of issues w/ disk space

*Bug Fixes:*

* Fix a bug in generating full_LR.fa sequences causing some full read sequences to miss couple of bases


**LSC 1.alpha - Release Notes**

* In the LSC 0.3.0 or 0.3.1, we optimized the setting of bowtie2 and BWA to get much more short read alignment, which improve the the accuracy of error correction a lot/ However, the increase of alignments also requires much more running time (on both alignment and the following error correction step) and memory usage. Therefore, a few users met difficulty of running LSC 0.3.0 or 0.3.1.

* In LSC 1.alpha, we apply probabilistic algorithm ("SCD" option) to select ""enough" short read alignment for error correction. LSC 1.alpha does NOT sacrifice the error correction performace (sensitivity and specificity). Please see http://www.augroup.org/LSC/LSC_manual.html#aligner Thus, we save running time and memory usage significantly. **The running time is 30-50% of LSC 0.3.1. The peak memory usage decreases to ~10G regardless of the data size.**

*New features:*

* Added probabilistic algorithm ("SCD" option) to pre-select SR alignments results based on LR-SR alignment coverage depth (Significant improvement in running time and memory usage)
* Removed requirement for loading SR dataset in memory to generate LR-SR mapping file (Significant improvement in memory usage)
* Added option "sort_max_mem" in run.cfg to control maximum memory used by unix sort command to avoid unexpected Mem crash

*Miscellaneous changes:*

* Fixed a bug in generating FASTQ file (it affected some of QualityValue computation results)

If you want to see the manual and tutorial of the old LSC (before 1.alpha), we keep the links of its the Old manual and Old tutorial in the right side bar.

**LSC 0.3.1 - Release Notes**
In LSC 0.3.1, we don't have pseudo chromosome, the alignment time reduced to ~10% (in Bowtie2 mode). And you can re-run some crashed jobs easily now.

*New features:*

* Remove pseudo-chr processing
* Accept compressed SR as input (should be named SR.fa.cps/SR.fa.cps.idx in any folder)
* Added "runLSC -cleanup" option to remove redundant files (per thread split, remaining _tmp files) if the run was successful at the end.
* Changed convertNav to sort reads and then generate LR_SR.map (memory optimization instead of loading all alignments in memory)

*Miscellaneous changes:*

* Changed "print" to system.echo (messages were not printed out in qsub output files)
* Changed a little bit "cleanup" option to keep per thread data (*.aa, *.ab, ..). It was useful when one thread was crashed and we wanted to just re-run that at the end

**LSC 0.3 - Release Notes**
In LSC 0.3, we have a few updates. They are very IMPORTANT updates, new features and small fixes

*Very IMPORTANT updates:*

* Support for RazerS3 and Bowtie2 as initial aligners. Now, BWA, Bowtie2, RazerS3 and Novoalign work in LSC.
* Added SR length coverage percentage on LR (SR-covered length/full length of corrected LR) to corrected_LR output file. Here is an example, where the last number 0.82 is the SR length coverage percentage on LR:
```>m111006_202713_42141_c100202382555500000315044810141104_s1_p0/18941/365_1361|0.82```
* Added support for three modes for step-wise runs:

	mode 0: end-to-end
	
	mode 1: generating LR_SR.map file
	
	mode 2: correction step
	
* Generating fastq output format:

Using the correction probability given coverage in the LSC paper and fitted a log function to it and then used the probability values to compute Sanger quality score: 33 - 10 * log10(1 - p). For the locations:

- without any SR coverage I used the default quality score of p = 0.725 (the same in your paper).

- with SR coverage but without any correction point, I used the number of covered SRs

- with SR coverage in a correction point (either because of compression or mismatch), I used number of SRs that had similar sequence with the substitute bases (i.e. the number of covered SRs that have the max number of similar sequence not the total number covered SRs.)

*New features:*

* Used the python path in the cfg file instead of default user\bin path
* Added option (-clean_up) to remove intermediate files or not (Note: important/useful ones will still be there in temp folder)
* Support for input fastq format for LR (long reads) and/or SR (short reads)
* Updated default BWA and novoalign commands options
* Printing out original LR names in the output file
* Support for printing out version number and (-v/-version) option

*Small fixes:*

* Fixed in removing XZ pattern from end of uncorrected_LR file
* Fixed samParser bug (which was ignoring some valid alignments in case of BWA)

**LSC 0.2.4 - Release Notes**

1. Besides the default aligner Novoalign, BWA can be also used as the initial aligner from this version. Please find the new aligner options in the webpage ".cfg file format"

2. Some uncertain corrections may exsit at the right ends of the long reads in the old LSC. LSC 0.2.4 settles this problem and likely improves the accuracy further.

**LSC 0.2.3 - Release Notes**

If you run LSC at the bin folder (the bin folder is the work directory) or set the bin as the default path, then you may meet a bug. LSC 0.2.3 fixes this bug of finding the correct bin folder. 

**LSC 0.2.2 - Release Notes**

LSC 0.2.2 fixes the bug of the option "I_RemoveBothTails". LSC 0.2.1 ran this option even if you set "N". It may halt the process in LSC 0.2.1 because the read name does not allow "RemoveBothTails". Now you can choose to use this option or not.

**LSC 0.2.1 - Release Notes**

LSC 0.2.1 fixes the bug of python path. Another bug of removing redundant reads is also fixed. LSC takes a long read data sets (>=100bp) and a short reads data sets (50 - 100bp) as input. They should be in FASTA format. Running time is almost linear with the the number of threads.

* Python (version 2.6 or higher) should be installed in the default user bin ```"#!/usr/bin/python"```
* Novoalign should be in your default path. The version V2.07.10 is recommended.
* A new option of using nonredandunt reads that save ~40% running time

**LSC 0.2 - Release Notes**

LSC 0.2 takes a long read data sets (>=100bp) and a short reads data sets (50 - 100bp) as input. They should be in FASTA format. Running time is almost linear with the the number of threads.

* More optional for raw data prefilter
* Multi-threading is avaiable
* Reduced redundant temp files
