# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import unittest

import filetype
from filetype.types.audio import Aac

# Absolute path to fixtures directory
FIXTURES = os.path.dirname(os.path.abspath(__file__)) + '/fixtures'


class TestFileType(unittest.TestCase):
    def test_guess_jpeg(self):
        img_path = FIXTURES + '/sample.jpg'
        with open(img_path, 'rb') as fp:
            for obj in (img_path, fp):
                kind = filetype.guess(obj)
                self.assertTrue(kind is not None)
                self.assertEqual(kind.mime, 'image/jpeg')
                self.assertEqual(kind.extension, 'jpg')
            # reset reader position test
            kind = filetype.guess(fp)
            self.assertTrue(kind is not None)
            self.assertEqual(kind.mime, 'image/jpeg')
            self.assertEqual(kind.extension, 'jpg')

    def test_guess_jpx(self):
        kind = filetype.guess(FIXTURES + '/sample.jpx')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'image/jpx')
        self.assertEqual(kind.extension, 'jpx')

    def test_guess_jxl(self):
        kind = filetype.guess(FIXTURES + '/sample.jxl')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'image/jxl')
        self.assertEqual(kind.extension, 'jxl')

    def test_guess_gif(self):
        kind = filetype.guess(FIXTURES + '/sample.gif')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'image/gif')
        self.assertEqual(kind.extension, 'gif')

    def test_guess_heic(self):
        kind = filetype.guess(FIXTURES + '/sample.heic')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'image/heic')
        self.assertEqual(kind.extension, 'heic')

    def test_guess_avif(self):
        kind = filetype.guess(FIXTURES + '/sample.avif')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'image/avif')
        self.assertEqual(kind.extension, 'avif')

    def test_guess_dds(self):
        kind = filetype.guess(FIXTURES + '/sample.dds')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'image/dds')
        self.assertEqual(kind.extension, 'dds')

    def test_guess_m4a(self):
        kind = filetype.guess(FIXTURES + '/sample.m4a')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'audio/mp4')
        self.assertEqual(kind.extension, 'm4a')

    def test_guess_aac_with_crc(self):
        for header in (b'\xff\xf0', b'\xff\xf8'):
            kind = filetype.guess(header)
            self.assertIsNotNone(kind)
            self.assertEqual(kind.mime, 'audio/aac')
            self.assertEqual(kind.extension, 'aac')

    def test_guess_aac_without_crc(self):
        for header in (b'\xff\xf1', b'\xff\xf9'):
            kind = filetype.guess(header)
            self.assertIsNotNone(kind)
            self.assertEqual(kind.mime, 'audio/aac')
            self.assertEqual(kind.extension, 'aac')

    def test_aac_rejects_invalid_headers(self):
        matcher = Aac()
        for header in (b'', b'\xff', b'\xfe\xf0', b'\xff\xe0',
                       b'\xff\xf2', b'\xff\xf3', b'\xff\xf4',
                       b'\xff\xf6', b'\xff\xfa', b'\xff\xfb',
                       b'\xff\xfc', b'\xff\xfe'):
            self.assertFalse(matcher.match(bytearray(header)))

    def test_guess_mp4(self):
        kind = filetype.guess(FIXTURES + '/sample.mp4')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'video/mp4')
        self.assertEqual(kind.extension, 'mp4')

    def test_guess_png(self):
        kind = filetype.guess(FIXTURES + '/sample.png')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'image/png')
        self.assertEqual(kind.extension, 'png')

    def test_guess_tif(self):
        kind = filetype.guess(FIXTURES + '/sample.tif')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'image/tiff')
        self.assertEqual(kind.extension, 'tif')

    def test_guess_mov(self):
        kind = filetype.guess(FIXTURES + '/sample.mov')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'video/quicktime')
        self.assertEqual(kind.extension, 'mov')

    def test_guess_zstd(self):
        for name in 'sample.zst', 'sample_skippable.zst':
            kind = filetype.guess(FIXTURES + '/' + name)
            self.assertTrue(kind is not None)
            self.assertEqual(kind.mime, 'application/zstd')
            self.assertEqual(kind.extension, 'zst')

    def test_guess_doc(self):
        for name in 'sample.doc', 'sample_1.doc', 'sample_2.doc':
            kind = filetype.guess(os.path.join(FIXTURES, name))
            self.assertIsNotNone(kind)
            self.assertEqual(kind.mime, 'application/msword')
            self.assertEqual(kind.extension, 'doc')

    def test_guess_docx(self):
        for name in 'sample.docx', 'sample_1.docx':
            kind = filetype.guess(os.path.join(FIXTURES, name))
            self.assertTrue(kind is not None)
            self.assertEqual(kind.mime, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.assertEqual(kind.extension, 'docx')

    def test_guess_odt(self):
        kind = filetype.guess(FIXTURES + '/sample.odt')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'application/vnd.oasis.opendocument.text')
        self.assertEqual(kind.extension, 'odt')

    def test_guess_xls(self):
        kind = filetype.guess(FIXTURES + '/sample.xls')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'application/vnd.ms-excel')
        self.assertEqual(kind.extension, 'xls')

    def test_guess_xlsx(self):
        kind = filetype.guess(FIXTURES + '/sample.xlsx')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertEqual(kind.extension, 'xlsx')

    def test_guess_ods(self):
        kind = filetype.guess(FIXTURES + '/sample.ods')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'application/vnd.oasis.opendocument.spreadsheet')
        self.assertEqual(kind.extension, 'ods')

    def test_guess_ppt(self):
        kind = filetype.guess(FIXTURES + '/sample.ppt')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'application/vnd.ms-powerpoint')
        self.assertEqual(kind.extension, 'ppt')

    def test_guess_pptx(self):
        kind = filetype.guess(FIXTURES + '/sample.pptx')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'application/vnd.openxmlformats-officedocument.presentationml.presentation')
        self.assertEqual(kind.extension, 'pptx')

    def test_guess_odp(self):
        kind = filetype.guess(FIXTURES + '/sample.odp')
        self.assertTrue(kind is not None)
        self.assertEqual(kind.mime, 'application/vnd.oasis.opendocument.presentation')
        self.assertEqual(kind.extension, 'odp')
