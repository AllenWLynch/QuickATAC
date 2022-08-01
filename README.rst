
QuickATAC
*********

About
-----

A package for manipulation of fragment files, envisioned as a superset of bedtools. 
The goal of this package is to provide a set of portable command-line based tools that, like bedtools,
are individually simple but compose to enable powerful manipulation of scATAC-seq fragment files. 

Most scripts are designed to stream in data, manipulate, then stream out, which works naturally within
the UNIX environment and reduces memory overhead.

Dependencies
------------

The only dependencies are **scipy**, **Bedtools** and **python**. 
**Make sure Bedtools is already installed and on your PATH before running QuickATAC**.

Installation
------------

For now, please install the package through github:

.. code-block:: bash

    $ https://github.com/AllenWLynch/QuickATAC.git
    $ cd QuickATAC
    $ pip install .

This will add the **quick** command to your *PATH*.

Usage
-----

The star of the show is the **agg-countmatrix** command, which takes a fragment file,
genome file (also called a chrom sizes file), and a set of peaks called via CellRanger
or MACS2, and outputs a 10X mtx-style countmatrix showing fragment counts at each peak for 
each barcode.

.. code-block:: bash

    usage: quick agg-countmatrix [-h] --fragment-file FRAGMENT_FILE --genome-file
                             GENOME_FILE --peaks-file PEAKS_FILE --out-prefix
                             OUT_PREFIX
                             [--chrom-match-string CHROM_MATCH_STRING]

    -h, --help            show this help message and exit
    --fragment-file FRAGMENT_FILE, -f FRAGMENT_FILE
                            scATAC-seq fragment file, tab-separated with five
                            columns: chrom, start, end, barcode, count.May be
                            gzipped, MUST BE SORTED!
    --genome-file GENOME_FILE, -g GENOME_FILE
                            Genome file (also called chromlengths file). Tab
                            separated with two columns: chrom, length
    --peaks-file PEAKS_FILE, -p PEAKS_FILE
                            File of peaks or genomic intervals with which to to
                            intersect fragments.Must be a tab-separated bed file
                            with atleast three columns.The first three must be:
                            chrom, start, end, followed by any number of columns.
    --out-prefix OUT_PREFIX, -o OUT_PREFIX
                            Output prefix for writing count matrix.The count
                            matrix is saved as three files: barcodes.tsv.gz,
                            features.tsv.gz, and matrix.mtx.gzout-prefix may be a
                            prefix string or a directory name.

    optional arguments:
    --chrom-match-string CHROM_MATCH_STRING, -m CHROM_MATCH_STRING
                            Filter out chromosomes that do not match this regex
                            string. The default allows counting for only major
                            numbered and sex chromosomes, so alternate contigs
                            will be removed.

**Example:**

.. code-block:: bash

    $ quick agg-countmatrix \
        -f atac_fragments.tsv.gz \
        -g genome.txt \
        -p peaks.bed \
        -o counts/
    Aggregating fragments: 100%|████████████████████████████████| 1.03M/1.03M [00:00<00:00, 3.88MB/s]
    $ ls counts/
    barcodes.tsv.gz  features.tsv.gz  matrix.mtx.gz

**Other cool scripts:**

**merge-peaks:** implements an algorithm for constructing a master peak set from a list of peak files.
This is useful for merging the results of multiple peak calls (perhaps on subclusters of a dataset
or from multiple samples and batches). *Unlike consensus clustering, this algorithm will include 
sample or batch-specific peaks in the master peakset, preserving potential biological diversity.*

**interleave-fragments:** from multiple sorted fragment files, interleave them to produce one big 
sorted fragment file!

**filter-chroms:** filter a fragment file given a whitelist of chromosomes.

**label-fragments:** append a sample name to the barcode of each fragment in a fragment file.
This is useful for retaining sample-of-origin information when merging fragment files.

Contributing
------------

There are many other fragment file manipulations that could be included, and a robust, minimal
library of tools could serve everybody well. If you would like to add a tool, just submit a 
pull request to this repo.

**Adding a tool**

A tool should get its own **.py** file, and should implement  **add_arguments** and **main** methods,
along with whatever else is needed to make that tool work (See **quickatac/label_fragments.py** for a
documented example). Ideally, the tool can stream in and stream out data, which should then be the 
default options for the CLI. 

Then, in **quckatac/cli.py**, import that tool:

.. code-block:: python

    from quickatac import label_fragments

And register a subcommand for the tool via:

.. code-block:: python

    add_subcommand(label_fragments, 'label-fragments')

The first parameter is the tool, and the second parameter is the name of the subcommand
in the CLI.
