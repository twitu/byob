#!/usr/bin/env python2.7
# Copyright 2013 Virantha Ekanayake All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import smtplib
import argparse
import sys
import os
import traceback
import time
import logging
import shutil
import glob
import itertools
from functools import wraps

from PIL import Image

from pypdfocr.pypdfocr_pdf import PyPdf
from pypdfocr.pypdfocr_tesseract import PyTesseract
from pypdfocr.pypdfocr_gs import PyGs
from pypdfocr.pypdfocr_preprocess import PyPreprocess


def error(text):
    print(("ERROR: %s" % text))
    sys.exit(-1)

# decorator to retry multiple times


def retry(count=5, exc_type=Exception):
    def decorator(func):
        @wraps(func)
        def result(*args, **kwargs):
            for _ in range(count):
                try:
                    return func(*args, **kwargs)
                except exc_type:
                    pass
                raise
        return result
    return decorator


@retry(count=6, exc_type=IOError)
def open_file_with_timeout(parser, arg):
    f = open(arg, 'r')
    return f


"""
    Make scanned PDFs searchable using Tesseract-OCR and autofile them
.. automodule:: pypdfocr
    :private-members:
"""


class PyPDFOCR(object):
    """
        The main clas.  Performs the following functions:

        * Parses command line options
        * Optionally just watches a directory for new PDF's to OCR; once a file appears, it does the next step
        * Runs a single file conversion:
            * Runs ghostscript to get tiff/jpg
            * Runs Tesseract-OCR to do the actual OCR
            * Takes the HOCR from Tesseract and creates a new PDF with the text overlay
        * Files the OCR'ed file in the proper place if specified
        * Files the original file if specified
        * 
    """

    def __init__(self):
        """ Initializes the GhostScript, Tesseract, and PDF helper classes.
        """
        self.config = {}

    def get_options(self, argv):
        """
            Parse the command-line options and set the following object properties:

            :param argv: usually just sys.argv[1:]
            :returns: Nothing

            :ivar debug: Enable logging debug statements
            :ivar verbose: Enable verbose logging
            :ivar enable_filing: Whether to enable post-OCR filing of PDFs
            :ivar pdf_filename: Filename for single conversion mode
            :ivar watch_dir: Directory to watch for files to convert
            :ivar config: Dict of the config file
            :ivar watch: Whether folder watching mode is turned on

        """
        p = argparse.ArgumentParser(
            description="Convert scanned PDFs into their OCR equivalent.  Depends on GhostScript and Tesseract-OCR being installed.",
            epilog="PyPDFOCR version"
        )

        p.add_argument('-d', '--debug', action='store_true',
                       default=False, dest='debug', help='Turn on debugging')

        p.add_argument('-v', '--verbose', action='store_true',
                       default=False, dest='verbose', help='Turn on verbose mode')

        p.add_argument('-m', '--mail', action='store_true',
                       default=False, dest='mail', help='Send email after conversion')

        p.add_argument('-l', '--lang',
                       default='eng', dest='lang', help='Language(default eng)')

        p.add_argument('--preprocess', action='store_true',
                       default=False, dest='preprocess', help='Enable preprocessing.  Not really useful now with improved Tesseract 3.04+')

        p.add_argument('--skip-preprocess', action='store_true',
                       default=False, dest='skip_preprocess', help='DEPRECATED: always skips now.')

        # ---------
        # Single or watch mode
        # --------
        single_or_watch_group = p.add_mutually_exclusive_group(required=True)
        # Positional argument for single file conversion
        single_or_watch_group.add_argument(
            "pdf_filename", nargs="?", help="Scanned pdf file to OCR")
        # Watch directory for watch mode
        single_or_watch_group.add_argument('-w', '--watch',
                                           dest='watch_dir', help='Watch given directory and run ocr automatically until terminated')

        # -----------
        # Filing options
        # ----------
        filing_group = p.add_argument_group(title="Filing optinos")
        filing_group.add_argument('-f', '--file', action='store_true',
                                  default=False, dest='enable_filing', help='Enable filing of converted PDFs')
        # filing_group.add_argument('-c', '--config', type = argparse.FileType('r'),
        filing_group.add_argument('-c', '--config', type=lambda x: open_file_with_timeout(p, x),
                                  dest='configfile', help='Configuration file for defaults and PDF filing')
        filing_group.add_argument('-n', action='store_true',
                                  default=False, dest='match_using_filename', help='Use filename to match if contents did not match anything, before filing to default folder')

        # Add flow option to single mode extract_images,preprocess,ocr,write

        args = p.parse_args(argv)

        self.debug = args.debug
        self.verbose = args.verbose
        self.pdf_filename = args.pdf_filename
        self.lang = args.lang
        self.watch_dir = args.watch_dir
        self.enable_email = args.mail
        self.match_using_filename = args.match_using_filename

        # Deprecating skip_preprocess to make skipping the default (always true). Tesseract 3.04 is so much better now
        # at handling non-ideal inputs and lines
        if args.skip_preprocess:
            pass
        self.skip_preprocess = True

        if args.preprocess:
            self.skip_preprocess = False

        if self.debug:
            logging.basicConfig(level=logging.DEBUG, format='%(message)s')

        if self.verbose:
            logging.basicConfig(level=logging.INFO, format='%(message)s')

        self.enable_evernote = False

        if args.enable_filing:
            self.enable_filing = True
            if not args.configfile:
                p.error(
                    "Please specify a configuration file(CONFIGFILE) to enable filing")
        else:
            self.enable_filing = False

        self.watch = False

        if args.watch_dir:
            logging.debug("Starting to watch")
            self.watch = True

        if self.enable_email:
            if not args.configfile:
                p.error(
                    "Please specify a configuration file(CONFIGFILE) to enable email")

    def _clean_up_files(self, files):
        """
            Helper function to delete files
            :param files: List of files to delete
            :type files: list
            :returns: None
        """
        for f in files:
            try:
                os.remove(f)
            except:
                logging.debug("Error removing file %s .... continuing" % f)


    def _setup_external_tools(self):
        """
            Instantiate the external tool wrappers with their config dicts
        """

        self.gs = PyGs(self.config.get('ghostscript', {}))
        self.ts = PyTesseract(self.config.get('tesseract', {}))
        self.pdf = PyPdf(self.gs)
        self.preprocess = PyPreprocess(self.config.get('preprocess', {}))

        return

    def run_conversion(self, pdf_filename):
        """
            Does the following:

            - Convert the PDF using GhostScript to TIFF and JPG
            - Run Tesseract on the TIFF to extract the text into HOCR (html)
            - Use PDF generator to overlay the text on the JPG and output a new PDF
            - Clean up temporary image files

            :param pdf_filename: Scanned PDF
            :type pdf_filename: string
            :returns: OCR'ed PDF
            :rtype: filename string
        """
        print(("Starting conversion of %s" % pdf_filename))
        try:
            # Make the images for Tesseract
            img_dpi, glob_img_filename = self.gs.make_img_from_pdf(
                pdf_filename)

            fns = glob.glob(glob_img_filename)

        except Exception:
            raise

        try:
            # Preprocess
            if not self.skip_preprocess:
                preprocess_imagefilenames = self.preprocess.preprocess(fns)
            else:
                logging.info("Skipping preprocess step")
                preprocess_imagefilenames = fns
            # Run teserract
            self.ts.lang = self.lang
            hocr_filenames = self.ts.make_hocr_from_pnms(
                preprocess_imagefilenames)

            # Generate new pdf with overlayed text
            #ocr_pdf_filename = self.pdf.overlay_hocr(tiff_dpi, hocr_filename, pdf_filename)
            ocr_pdf_filename = self.pdf.overlay_hocr_pages(
                img_dpi, hocr_filenames, pdf_filename)

        finally:
            # Clean up the files
            time.sleep(1)
            if not self.debug:
                # Need to clean up the original image files before preprocessing
                if "fns" in locals():  # Have to check if this was set before exception raised
                    logging.info("Cleaning up %s" % fns)
                    self._clean_up_files(fns)

                if "preprocess_imagefilenames" in locals():  # Have to check if this was set before exception raised
                    logging.info("Cleaning up %s" % preprocess_imagefilenames)
                    # splat the hocr_filenames as it is a list of pairs
                    self._clean_up_files(preprocess_imagefilenames)
                    for ext in [".hocr", ".html", ".txt"]:
                        fns_to_remove = [os.path.splitext(
                            fn)[0]+ext for fn in preprocess_imagefilenames]
                        logging.info("Cleaning up %s" % fns_to_remove)
                        # splat the hocr_filenames as it is a list of pairs
                        self._clean_up_files(fns_to_remove)
                    # clean up the hocr input (jpg) and output (html) files
                    # self._clean_up_files(itertools.chain(*hocr_filenames)) # splat the hocr_filenames as it is a list of pairs
                    # Seems like newer tessearct > 3.03 is now creating .txt files with the OCR text?/?
                    #self._clean_up_files([x[1].replace(".hocr", ".txt") for x in hocr_filenames])

        print(("Completed conversion successfully to %s" % ocr_pdf_filename))
        return ocr_pdf_filename


    def go(self, filename):

        # setup arguments
        self.skip_preprocess = False
        self.debug = False
        self.lang = "eng"

        # Setup tesseract and ghostscript
        self._setup_external_tools()

        # Will only receive filename as argument
        self.run_conversion(filename)
