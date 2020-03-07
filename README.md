# NCBI Genome Submission Protocol

Steps to submit custom (eg: `Prokka`) annotations to NCBI.

Things to note before starting:

1. Use the latest `Prokka` v1.13
2. Python 3.6 or greater is required for custom python script
3. Install tbl2asn (I used minconda)
4. Generate sbt file template (needed for tbl2asn): https://submit.ncbi.nlm.nih.gov/genbank/template/submission/

### 1. Contamination Check.

NCBI will perform a detailed contamination check via blasting your sequences against a custom db called UniVec or UniVec_Core. More info here: https://www.ncbi.nlm.nih.gov/tools/vecscreen/univec/ 
You can replicate this step inhouse to save time before uploading to NCBI. Contamination includes sequence adapters and PHIX. Usually these are removed in the trimming step but not always.  

Command:

    YOUR_INSTALL/ncbi-blast-2.7.1/bin/blastn -query INPUT.FASTA  \
    -reward 1 -penalty -5 -gapopen 3 -gapextend 3 -dust yes -soft_masking true \
    -evalue 700 -searchsp 1750000000000 -num_threads 4 \
    -db ~YOUR_INSTALL/ncbi-blast-2.7.1/data/UniVec_Core -outfmt 6 -out OUTPUT.FASTA

Output:

Standard BLAST output. Manually remove any contaminants found.

### 2. Run Prokka.

Command:

    prokka --compliant --proteins Z.fa --outdir X --locustag ORG \
    --genus GENUS --species SPECIES --strain Y --prefix Y --gram neg --cpus 4 W.fasta

Note: Prokka lies, the `--compliant` flag is not really compliant! Prokka is not at fault due to the ever changing requirements of NCBI submission process

Where:

  `Z.fa` is the annotated amino acid sequences of your reference genome
  
  `X` is your output directory
  
  `Y` is your isolate/strain ID (eg: 60051 BAL Hi1)
  
  `W.fasta` is the assembly fasta file for annotation

Outputs:
  
  `.gbk`: human readable format, looks exactly like NCBI nuccore

  `.tbl`: for downstream processing using tbl2asn 

  `.fsa`: prokka reorders contigs and renames, therefore the fasta file generated here is in a different order to the inputed fasta file. Annotations are in reference to this fasta file

  `.sqn`: ignore! do not use this .sqn. tbl2asn generates a new one
  
  Ignore the rest, these are the most important
  

### 3. File shuffling for tbl2asn.

  * Create folder for each isolate/strain
  * Move/Copy the following prokka-generated files into said folder: 
  
    `.fsa`
    
    `.tbl` 
    
    `.sbt` genearted from https://submit.ncbi.nlm.nih.gov/genbank/template/submission/
    

### 4. Run `tbl2asn`. 

tbl2asn is run on each Prokka output separately. This is important because tbl2asn can process multiple files at once if it detects them. Never looked into this unfortunately. You may want to modify the -a flag to specify the contig gaps (NNN) used. 
More info on `tbl2asn` https://www.ncbi.nlm.nih.gov/genbank/tbl2asn2/

Command:

    tbl2asn -V vb -M n -a r10k -y 'Annotated using Prokka v1.13 \
    from https://github.com/tseemann/prokka' -t X.sbt -i Y.fsa -Z error.tmp

Where: 

  `X.sbt` is the file generated from #3 above
  
  `Y.fsa` is the fasta file prokka generates
  
  `.tbl` file is detected automatically

Output:

  `.gbf`: genbank file (not including annotations) for viewing meta data
  
  `.sqn`: Important! the file uploaded to NCBI Genome
  
  `summary.val`: summary of errors encountered 
  
  `.val`: list of every error encountered by tbl2asn. "warnings" are errors too. Very detailed!
  

### 5. Run `tbl_cleanup.py` python script.

You will encounter heaps of errors from the tbl2asn tool. Hopefully this script will fix the majority. Some errors require manual correction (see below). Best to create a subfolder for this step.

Command (needs to be run on each .tbl file created above):

    tbl_cleanup.py inFile outFile
    
    tbl_cleanup.py 60051_BAL_Hi1.tbl 60051_BAL_Hi1_cor.tbl 

Where:

  `inFile`: input .tbl file 
  `outFile`: name of output .tbl file
  
Output:

   Clean .tbl file (hopefully)
   

### 6. Rerun `tbl2asn` (step 2)

If any errors are present, manually correct (see below). The .val file MUST contain no errors or warnings. 


#### 7. Submit .sqn files to NCBI Genome https://submit.ncbi.nlm.nih.gov/subs/genome/

Correct errors encountered and resubmit.


### 8. (Optional) Types of errors encountered that require manual fixing:		

* Unknown `NNNs`

The `tbl2asn` `-a` flag is relevant to this error. See above.

You may encounter an error regarding unknown number of `NNNs` (or incorrect number of `NNNs`). This is caused by the assembly pipeline stitching contigs together and adding `NNNs` or possibly due to bad/no coverage resulting in a known number of `NNNs` being produced. If encountered, `.val` file will contain an error with # of `NNNs` and location. Use a fasta editor (eg: UGENE) to locate these `NNNs` in the `.fsa` file and replace with `>?#`. Where # is the number of `NNNs`. 

Actual example:

  CGATGGCCCTTCCATTCAGAACCACCGGATCACTATGACCTACTTTCGTACCTGCTCGAC
  TTGTCTGTCTCGCAGTTAAGCTTGCTTATACCTGTCTCTTATACACATCTGACGCTGCC
  
  \>?145
  
  AGACAGGTGCAGGTCGGAACTTACCCGACAAGGAATTTCGCTACCTTAGGACCGTTAT
  AGTTACGGCCGCCGTTTACTGGGGCTTCGATCAGGTGCTTCTCTTGCGATGACACCATCA

* Adapters/spikes. See step 0 above. 

Extra links for more information:

https://www.ncbi.nlm.nih.gov/genbank/genomesubmit/ - prokaryotic genome submission guidelines
https://www.ncbi.nlm.nih.gov/genbank/genome_validation - for Submit portal errors
https://www.ncbi.nlm.nih.gov/tools/vecscreen/contam/ - for contamination errors
https://www.ncbi.nlm.nih.gov/genbank/asndisc.examples/ - example error report
https://www.ncbi.nlm.nih.gov/genbank/asndisc/#fatal - example error report
