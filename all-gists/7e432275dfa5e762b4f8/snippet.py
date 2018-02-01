#!/usr/bin/env python3
"""
Running this script is (intended to be) equivalent to running the following Snakefile:

include: "pipeline.conf"  # Should be an empty file

shell.prefix("set -euo pipefail;")

rule all:
    input:
        "reads.counts"


rule unpack_fastq:
    '''Unpack a FASTQ file'''
    output: "{file}.fastq"
    input: "{file}.fastq.gz"
    resources: time=60, mem=100
    params: "{file}.params"
    threads: 8
    log: 'unpack.log'
    shell:
        '''zcat {input} > {output}
        echo finished 1>&2 {log}
        '''


rule count:
    '''Count reads in a FASTQ file'''
    output: counts="{file}.counts"
    input: fastq="{file}.fastq"
    run:
        n = 0
        with open(input.fastq) as f:
            for _ in f:
                n += 1
        with open(output.counts, 'w') as f:
            print(n / 4, file=f)

"""
from snakemake.workflow import Workflow, Rules
import snakemake.workflow
from snakemake import shell
from snakemake.logging import setup_logger

setup_logger()

workflow = Workflow(__file__)
snakemake.workflow.rules = Rules()
snakemake.workflow.config = dict()


### Output from snakemake --print-compilation follows (reformatted)

workflow.include("pipeline.conf")

shell.prefix("set -euo pipefail;")

@workflow.rule(name='all', lineno=6, snakefile='.../Snakefile')
@workflow.input("reads.counts")
@workflow.norun()
@workflow.run
def __all(input, output, params, wildcards, threads, resources, log, version):
    pass


@workflow.rule(name='unpack_fastq', lineno=17, snakefile='.../Snakefile')
@workflow.docstring("""Unpack a FASTQ file""")
@workflow.output("{file}.fastq")
@workflow.input("{file}.fastq.gz")

@workflow.resources(time=60, mem=100)
@workflow.params("{file}.params")
@workflow.threads(8)
@workflow.log('unpack.log')
@workflow.shellcmd(
    """zcat {input} > {output}
        echo finished 1>&2 {log}
        """
)
@workflow.run
def __unpack_fastq(input, output, params, wildcards, threads, resources, log, version):
    shell("""zcat {input} > {output}
        echo finished 1>&2 > {log}
        """
)


@workflow.rule(name='count', lineno=52, snakefile='.../Snakefile')
@workflow.docstring("""Count reads in a FASTQ file""")
@workflow.output(counts = "{file}.counts")
@workflow.input(fastq = "{file}.fastq")
@workflow.run
def __count(input, output, params, wildcards, threads, resources, log, version):
    n = 0
    with open(input.fastq) as f:
        for _ in f:
            n += 1
    with open(output.counts, 'w') as f:
        print(n / 4, file=f)


### End of output from snakemake --print-compilation


workflow.check()
print("Dry run first ...")
workflow.execute(dryrun=True, updated_files=[])
print("And now for real")
workflow.execute(dryrun=False, updated_files=[], resources=dict())
