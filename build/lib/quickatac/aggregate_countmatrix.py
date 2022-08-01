import argparse
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from scipy import sparse
from scipy.io import mmwrite
import sys
import os
import gzip

def try_file(path):

    try:
        f = open(path, 'w')
    except OSError:
        return False
    else:
        f.close()
        os.remove(path)
        return True


def name_formatter(prefix, filename):

    if os.path.isdir(prefix):
       return os.path.join(prefix, filename)  
    else:
        return prefix + '_' + filename


def count_peaks(*, input_stream, 
    num_fragment_file_columns = 5,
    count_duplicates = False):
    
    assert(num_fragment_file_columns>=5)

    barcode_dict = {}
    
    peak_dict = {'background' : 0}
    
    peak_indices, barcode_indices, counts = [],[],[]
    
    i = 0
    for i, line in enumerate(input_stream):
            
        line = line.strip().split('\t')

        try:
            frag_chrom, frag_start, frag_end, barcode, count = line[:num_fragment_file_columns]
            peak_chrom, peak_start, peak_end = line[num_fragment_file_columns:num_fragment_file_columns+3]
        except ValueError as err:
            raise ValueError('Line {} of fragment file may have the wrong number of columns.'.format(str(i))) from err
        
        if peak_chrom == '.' or peak_start == '-1':
            peak_idx = peak_dict['background']
        else:

            peak_key = (peak_chrom, int(peak_start), int(peak_end))

            if peak_key in peak_dict:
                peak_idx = peak_dict[peak_key]
            else:
                peak_idx = len(peak_dict)
                peak_dict[peak_key] = peak_idx
            
        if barcode in barcode_dict:
            barcode_idx = barcode_dict[barcode]
        else:
            barcode_idx = len(barcode_dict)
            barcode_dict[barcode] = barcode_idx
        
        peak_indices.append(peak_idx)
        barcode_indices.append(barcode_idx)
        if count_duplicates:
            counts.append(int(count))
        else:
            counts.append(1)
        
    logger.info('Done reading fragments.')
    logger.info('Formatting counts matrix ...')

    return sparse.coo_matrix((counts, (barcode_indices, peak_indices)), 
        shape = (len(barcode_dict), len(peak_dict))).tocsc(), list(barcode_dict.keys()), list(peak_dict.keys()) 


def addline(file, *fields):
    file.write(
        ('\t'.join(map(str, fields)) + '\n').encode()
    )

def write_barcodes(outfile, barcodes, n_background):

    for bc, n in zip(barcodes, n_background):
        addline(outfile, bc)

def write_features(outfile, peaks):

    for i, (chr, start, end) in enumerate(peaks):

        stringified = map(str, [chr, start, end])
        addline(
            outfile, '{}:{}-{}'.format(*stringified), 'peak_' + str(i), 'Peak'
        )
            
def write_data(prefix, mtx, barcodes, peaks):

    n_background = mtx[:,0].toarray()
    mtx = mtx[:,1:] # remove the background count from the matrix
    peaks = peaks[1:]
    
    logger.info('Writing barcodes file.')
    with gzip.open(name_formatter(prefix, 'barcodes.tsv.gz'), 'wb') as f:
        write_barcodes(f, barcodes, n_background)
    
    logger.info('Writing features file.')
    with gzip.open(name_formatter(prefix, 'features.tsv.gz'), 'wb') as f:
        write_features(f, peaks)
    
    logger.info('Writing matrix file.')
    with gzip.open(name_formatter(prefix, 'matrix.mtx.gz'), 'wb') as f:
        mmwrite(f, mtx.T)
    

def add_arguments(parser):
    
    parser.add_argument('input', type = argparse.FileType('r'), default = sys.stdin)
    parser.add_argument('--out-prefix','-o',required=True, type = str,
        help = 'Output filename for adata object.')
    parser.add_argument('--num-fragment-file-columns', '-nc', type = int, default = 5)


def main(args):

    assert try_file(name_formatter(args.out_prefix, 'test.tsv.gz')), 'Failed to create mock file, make sure "--out-prefix" gives a valid path or directory.'

    write_data(
        args.out_prefix,
        *count_peaks(
            input_stream=args.input,
            num_fragment_file_columns = args.num_fragment_file_columns,
        )
    )