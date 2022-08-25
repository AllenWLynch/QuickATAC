

import os
import subprocess
import sys
import argparse
from quickatac.base import is_gzipped

def countmatrix(*,
    fragment_file, peaks_file, genome_file, out_prefix,
    chrom_match_string = "^(chr)[(0-9)|(X,Y)]+$",
    min_fragsize = 15, 
    max_fragsize = 294
    ):

    try:
        size = os.path.getsize(fragment_file.name)
        is_file = True
    except OSError:
        is_file = False
        gzipped_file = False

    if is_file:

        with open(fragment_file.name, 'rb') as f:
            gzipped_file = is_gzipped(f)

        tqdm_command = subprocess.Popen(
            ['tqdm','--total', str(size), '--bytes',
            '--desc', 'Aggregating fragments'],
            stdin= fragment_file, 
            stdout= subprocess.PIPE,
        )
        fragment_file = tqdm_command.stdout

        if gzipped_file:

            gzip_command = subprocess.Popen(
                ['gzip','-c', '-d'], 
                stdin = tqdm_command.stdout,
                stdout= subprocess.PIPE,
            )
            fragment_file = gzip_command.stdout
    
    check_command = subprocess.Popen(
        ['quick','check-format'],
        stdin = fragment_file, stdout=subprocess.PIPE,
    )

    filter_command = subprocess.Popen(
        ['quick','filter-chroms',
        '--genome', genome_file,
        '--chr-match-string', chrom_match_string],
        stdin = check_command.stdout, 
        stdout= subprocess.PIPE,
    )

    fragsize_command = subprocess.Popen(
        ['quick','filter-fragsize',
        '-min', str(min_fragsize),
        '-max', str(max_fragsize)],
        stdin = filter_command.stdout,
        stdout= subprocess.PIPE,
    )

    intersect_command = subprocess.Popen(
        ['bedtools','intersect','-a','-','-b', peaks_file,
        '-loj','-sorted','-wa','-wb'],
        stdin = fragsize_command.stdout, stdout = subprocess.PIPE,
    )

    count_command = subprocess.Popen(
        ['quick','count-intersection',
        '-','-o', out_prefix,
        '-nc', '5'],
        stdin= intersect_command.stdout, stdout= subprocess.PIPE
    )

    count_command.communicate()
    check_command.wait()
    intersect_command.wait()
    filter_command.wait()
    
    if is_file:
        tqdm_command.wait()
        
        if gzipped_file:
            gzip_command.wait()
            

def main(args):

    countmatrix(
        fragment_file = args.fragments,
        peaks_file = args.peaks_file,
        genome_file = args.genome_file,
        out_prefix = args.out_prefix,
        chrom_match_string = args.chrom_match_string,
        min_fragsize=args.min_fragsize,
        max_fragsize=args.max_fragsize,
    )

def add_arguments(parser):

    parser.add_argument('fragments', 
            nargs = '?', 
            default = sys.stdin.buffer,
            type = argparse.FileType('rb'),
            help = 'scATAC-seq fragment file, tab-separated with five columns: chrom, start, end, barcode, count.'
                    'May be gzipped, MUST BE SORTED! If provided via stdin, must be uncompressed.'
        )

    parser.add_argument('--genome-file','-g', type = str, 
        help = 'Genome file (also called chromlengths file). Tab separated with two columns: chrom, length', required = True)

    parser.add_argument('--peaks-file','-p', required = True, type = str,
        help = 'File of peaks or genomic intervals with which to to intersect fragments.'
               'Must be a tab-separated bed file with atleast three columns.'
               'The first three must be: chrom, start, end, followed by any number of columns.')

    parser.add_argument('--out-prefix','-o',required=True, type = str,
        help = 'Output prefix for writing count matrix.'
               'The count matrix is saved as three files: barcodes.tsv.gz, features.tsv.gz, and matrix.mtx.gz'
               'out-prefix may be a prefix string or a directory name.')

    parser.add_argument('--chrom-match-string','-m', type = str,
        default = "^(chr)[(0-9)|(X,Y)]+$",
        help = 'Filter out chromosomes that do not match this regex string. The default allows counting for'
               'Only major numbered and sex chromosomes, so alternate contigs will be removed.')

    parser.add_argument('--min-fragsize','-min',type = int, default = 15,
        help = 'Minimum fragment length to count')

    parser.add_argument('--max-fragsize','-max',type = int, default = 294,
        help = 'Maximum fragment length to count')
    