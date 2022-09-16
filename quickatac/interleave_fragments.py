
from quickatac.base import OptionalGzipFiletype, add_default_output

class SkipRecordException(Exception):
    pass

class BedFileRecord:

    def __init__(self, fields):
        self.fields = fields.decode().strip().split('\t')
        try:
            self.chr, self.start, self.end = self.fields[0], int(self.fields[1]), int(self.fields[2])
        except (IndexError, TypeError) as err:
            raise SkipRecordException() from err


    def __gt__(self, other):
        return self.chr > other.chr or \
            (self.chr == other.chr and self.start > other.start)

    def __ge__(self, other):
        return (self > other) or (self == other)

    def __eq__(self, other):
        return self.chr == other.chr and self.start == other.start

    def __str__(self):
        return '\t'.join(self.fields)


def sorted_iterator(iter):

    for curr in iter:

        try:
            _prev
        except UnboundLocalError:
            _prev = curr
        else:
            if not curr >= _prev:
                raise ValueError('Items are out of order, {} greater than {}'\
                        .format(str(curr), str(_prev))
                    )
            
            _prev = curr

        yield curr


def convert_or_skip(iter, _type):

    for x in iter:
        try:
            yield _type(x)
        except SkipRecordException:
            pass


class PeekIterator:

    def __init__(self, iterator):
        self._iterator = iterator
        self._depleted = False
        try:
            self._next = self._get_next()
        except StopIteration:
            self._depleted = True

    def _get_next(self):
        return next(self._iterator)
        
    def __next__(self):

        if self._depleted:
            raise StopIteration()            

        ret_value = self._next 
        
        try:
            self._next = self._get_next()
        except StopIteration:
            self._depleted = True
        
        return ret_value

    def peek(self):
        if self._depleted:
            raise StopIteration()

        return self._next

    def has_next(self):
        return not self._depleted

    def __eq__(self, other):
        return self.peek() == other.peek()

    def __gt__(self, other):
        return self.peek() > other.peek()


def interleave_sorted_frags(*stream_handles):

    print(next(stream_handles[0]))

    streams = [
        PeekIterator(sorted_iterator(convert_or_skip(stream, BedFileRecord)))
        for stream in stream_handles
    ]


    while True:

        streams = [stream for stream in streams if stream.has_next()]
        
        if len(streams) == 0:
            break
        else:
            yield next(min(streams))


def add_arguments(parser):

    parser.add_argument('fragmentfiles', nargs = '+', type = OptionalGzipFiletype('rb'),
        help = 'List of paths to fragment files. Any file may be gzipped or not. All must be sorted.')
    add_default_output(parser)


def main(args):

    for fragment in interleave_sorted_frags(*args.fragmentfiles):
        args.outfile.write(str(fragment) + '\n')
    