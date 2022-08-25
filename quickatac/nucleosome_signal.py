from quickatac.filter_fragsize import filter_fragsize
from quickatac.count_occurences import count_occurences
from collections import defaultdict
from quickatac.base import enforce_string, add_default_input, add_default_output


def nucleosome_signal(fragments):

    try:
        fragments.seek(0,0)
    except Exception:
        raise ValueError(
            'This function requires an iterator that implements "seek", so it may not be used as part of a PIPE.'
        )

    def collect_fragments(min_size, max_size):

        return count_occurences(
                filter_fragsize(fragments, 
                    min_size = min_size, max_size = max_size
                ), 
                column = 4, # count barcode
                sep = '\t'
            )
        

    short = collect_fragments(0, 147)

    fragments.seek(0,0)

    long = collect_fragments(148, 294)

    all_barcodes = set(
        [*short.keys(), *long.keys()]
    )

    for barcode in all_barcodes:
        yield barcode, (short[barcode] + 1)/(long[barcode] + 1), short[barcode], long[barcode]


def add_arguments(parser):
    add_default_input(parser)    
    add_default_output(parser)


def main(args):

    args.outfile.write(
        'barcode\tnucleosome_signal\tlt_147bp\tgt_147bp\n'
    )
    for fields in nucleosome_signal(args.fragments):
        args.outfile.write(
            '\t'.join(map(str, fields)) + '\n'
        )