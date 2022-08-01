import argparse
from quickatac.base import add_default_input, add_default_output

def _get_allowed_barcodes(barcode_input):
    return {
        barcode : True for barcode in map(lambda x : x.strip(), barcode_input)
    }

def _apply_filter(fragments, allowed_values, colnum):

    values_dict = _get_allowed_barcodes(allowed_values)

    for fragment in fragments:
        fields = fragment.strip().split('\t')
        if fields[colnum] in values_dict:
            yield fragment.strip()


def add_arguments(parser):

    add_default_input(parser)
    parser.add_argument('--barcodes', '-bc', type = argparse.FileType('r'), required = True)
    add_default_output(parser)
    

def main(args):

    for fragment in _apply_filter(args.fragments, args.barcodes, 3):
        args.outfile.write(fragment + '\n')