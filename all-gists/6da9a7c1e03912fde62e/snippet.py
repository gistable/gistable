import luigi
from luigis_monkey_wrench import *

REF='human_17_v37.fasta'
INDIVIDUALS=['NA06984','NA07000']
SAMPLES=['1','2']
BASENAME='.ILLUMINA.low_coverage.17q_'
PICARDDIR='/sw/apps/bioinfo/picard/1.69/kalkyl/'
KNOWNSITES='/proj/g2014207/labs/gatk/ALL.chr17.phase1_integrated_calls.20101123.snps_indels_svs.genotypes.vcf'

class GATKWorkflow(WorkflowTask):

    def requires(self):
        for i in INDIVIDUALS:
            # Workflow definition
            # ---------------------------------------------------------------------------------
            # files() will return a pseudo task that just outputs an existing file,
            #         while not running anything.
            # shell() will create a new task with a command that can take inputs
            #         and outputs.
            fq1 = file('fastq:{i}/{i}{b}1.fq'.format(i=i,b=BASENAME))
            fq2 = file('fastq:{i}/{i}{b}2.fq'.format(i=i,b=BASENAME))

            # Step 2 in [1]--------------------------------------------------------------------
            aln1 = shell('bwa aln {ref} <i:fastq> > <o:sai:<i:fastq>.sai>'.format(ref=REF))
            aln1.inports['fastq'] = fq1.outport('fastq')

            aln2 = shell('bwa aln {ref} <i:fastq> > <o:sai:<i:fastq>.sai>'.format(ref=REF))
            aln2.inports['fastq'] = fq2.outport('fastq')

            # Step 3 in [1]--------------------------------------------------------------------
            merg = shell('bwa sampe {ref} <i:sai1> <i:sai2> <i:fq1> <i:fq2> > <o:merged:{i}/{i}{b}.merged.sam>'.format(
                ref=REF,
                i=i,
                b=BASENAME))
            merg.inports['sai1'] = aln1.outport('sai')
            merg.inports['sai2'] = aln2.outport('sai')
            merg.inports['fq1'] = fq1.outport('fastq')
            merg.inports['fq2'] = fq2.outport('fastq')

            # Step 4a in [1]------------------------------------------------------------------
            mergbam = shell('''
            java -Xmx2g -jar {p}/AddOrReplaceReadGroups.jar
                INPUT=<i:sam>
                OUTPUT=<o:bam:<i:sam>.bam>
                SORT_ORDER=coordinate
                RGID={sample}-id
                RGLB={sample}-lib
                RGPL=ILLUMINA
                RGPU={sample}-01
                RGSM={sample}
            '''.format(
                 p=PICARDDIR,
                 sample=i))
            mergbam.inports['sam'] = merg.outport('merged')

            # Step 4b in [1] -----------------------------------------------------------------
            index_mergbam = shell('''
            java -Xmx2g -jar
                /sw/apps/bioinfo/picard/1.69/kalkyl/BuildBamIndex.jar
                INPUT=<i:bamr
                # <o:bai:<i:bam:.bam|.bai>>
            ''')
            index_mergbam.inports['bam'] = mergbam.outport('bam')

            # Step 5a in [1]------------------------------------------------------------------
            local_realign = shell('''
            java -Xmx2g -jar /sw/apps/bioinfo/GATK/1.5.21/GenomeAnalysisTK.jar
                -I <i:bam>
                -R {ref}
                -T RealignerTargetCreator
                -o <o:intervals:<i:bam>.intervals>
            '''.format(
               ref=REF))
            local_realign.inports['bam'] = mergbam.outport('bam')

            # Step 5b in [1]-----------------------------------------------------------------
            actual_realign = shell('''
            java -Xmx2g -jar /sw/apps/bioinfo/GATK/1.5.21/GenomeAnalysisTK.jar
                -I <i:bam>
                -R {ref}
                -T IndelRealigner
                -o <o:realigned_bam:<i:intervals>.realign.bam>
                -targetIntervals <i:intervals>
                # <o:realigned_bai:<i:intervals>.realign.bai>
            '''.format(
                ref=REF))
            actual_realign.inports['bam'] = mergbam.outport('bam')
            actual_realign.inports['intervals'] = local_realign.outport('intervals')

            # Step 5c in [1]-----------------------------------------------------------------
            mark_dupes = shell('''
            java -Xmx2g -jar /sw/apps/bioinfo/picard/1.69/kalkyl/MarkDuplicates.jar '
                INPUT=<i:bam> '
                OUTPUT=<o:marked_bam:<i:bam>.marked.bam> '
                METRICS_FILE=<o:metrics:<i:bam>.marked.metrics>
            ''')
            mark_dupes.inports['bam'] = actual_realign.outport('realigned_bam')

            # Step 5d in [1], Index bam (picard does not do that automatically)---------------
            index_marked_bam = shell(('java -Xmx2g -jar /sw/apps/bioinfo/picard/1.69/kalkyl/BuildBamIndex.jar '
                                 'INPUT=<i:bam> '
                                 '# <o:bai:<i:bam:.bam|.bai>>'))
            index_marked_bam.inports['bam'] = mark_dupes.outport('marked_bam')

            # Step 5e in [1], quality recalibration with GATK---------------------------------
            count_covar = shell('''
            java -Xmx2g -jar /sw/apps/bioinfo/GATK/1.5.21/GenomeAnalysisTK.jar
                -T CountCovariates -I <i:bam>
                -R {ref}
                -knownSites {sites}
                -cov ReadGroupCovariate
                -cov CycleCovariate
                -cov DinucCovariate
                -cov QualityScoreCovariate
                -recalFile <o:covariate:<i:bam>.covar>
            '''.format(
                ref=REF,
                sites=KNOWNSITES))
            count_covar.inports['bam'] = mark_dupes.outport('marked_bam')

            # Step 5f in [1]-----------------------------------------------------------------
            table_recalib = shell('''
            java -Xmx2g -jar /sw/apps/bioinfo/GATK/1.5.21/GenomeAnalysisTK.jar
                -T TableRecalibration
                -I <i:bam>
                -R {ref}
                -recalFile <i:calib>
                -o <o:calibrated_bam:<i:calib>.bam>
            '''.format(ref=REF))
            table_recalib.inports['bam'] = mark_dupes.outport('marked_bam')
            table_recalib.inports['calib'] = count_covar.outport('covariate')

            yield table_recalib


if __name__ == '__main__':
    luigi.run()

# REFERENCES
# ----------
# [1] http://uppnex.se/twiki/do/view/Courses/NgsIntro1502/ResequencingAnalysis