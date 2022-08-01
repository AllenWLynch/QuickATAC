import gzip
import argparse
import sys

def enforce_string(b, encoding = 'utf-8'):

    if isinstance(b, bytes):
        try:
            return b.decode(encoding)
        except UnicodeDecodeError as err:
            raise UnicodeDecodeError('Error decoding bytes to string, you probably passed a gzipped file into a command through stdin without decompressing it first.') from err
    else:
        return b

def is_gzipped(fragment_file):
    
    try:
        gzip.GzipFile(fileobj = fragment_file, mode = 'rb').peek(1)
    except OSError:
        return False
    else:
        return True
    finally:
        fragment_file.seek(0,0)


class OptionalGzipFiletype(argparse.FileType):

    def __call__(self, string):

        fileobj = super().__call__(string)

        return gzip.GzipFile(fileobj = fileobj, mode = self._mode) if is_gzipped(fileobj) \
            else fileobj


def add_default_input(parser):

    parser.add_argument('fragments', 
            nargs = '?', 
            default = sys.stdin.buffer,
            type = OptionalGzipFiletype('rb'),
            help = 'scATAC-seq fragment file, tab-separated with five columns: chrom, start, end, barcode, count.'
                    'May be gzipped, MUST BE SORTED! If provided via stdin, must be uncompressed.'
        )

def add_default_output(parser):
    parser.add_argument('--outfile', '-o', type = argparse.FileType('w'), default = sys.stdout)