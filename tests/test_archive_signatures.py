# -*- coding: utf-8 -*-

from __future__ import absolute_import

import io
import itertools
import os
import sqlite3
import tempfile
import unittest
import zipfile

import filetype


SQLITE_HEADER = b'SQLite format 3\x00'
ZIP_HEADERS = (b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08')


class TestArchiveSignatures(unittest.TestCase):
    def test_zip_signature_pairs(self):
        for third, fourth in itertools.product((3, 5, 7), (4, 6, 8)):
            data = bytes(bytearray([0x50, 0x4b, third, fourth]))
            with self.subTest(data=data):
                expected = 'application/zip' if data in ZIP_HEADERS else None
                self.assertEqual(filetype.guess_mime(data), expected)

    def test_zip_truncated_signatures(self):
        for header in ZIP_HEADERS:
            for length in range(4):
                with self.subTest(header=header, length=length):
                    self.assertIsNone(filetype.guess(header[:length]))

    def test_real_zip_archives(self):
        for populated in (False, True):
            for compression in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                with self.subTest(
                        populated=populated, compression=compression):
                    buffer = io.BytesIO()
                    with zipfile.ZipFile(buffer, 'w', compression) as archive:
                        if populated:
                            archive.writestr('sample.txt', 'hello')
                    data = buffer.getvalue()
                    self.assertTrue(zipfile.is_zipfile(io.BytesIO(data)))
                    kind = filetype.guess(data)
                    self.assertIsNotNone(kind)
                    self.assertEqual(kind.mime, 'application/zip')
                    self.assertEqual(kind.extension, 'zip')

    def test_sqlite_signature(self):
        for buffer_type in (bytes, bytearray, memoryview):
            with self.subTest(buffer_type=buffer_type):
                kind = filetype.guess(buffer_type(SQLITE_HEADER))
                self.assertIsNotNone(kind)
                self.assertEqual(kind.mime, 'application/x-sqlite3')
                self.assertEqual(kind.extension, 'sqlite')

    def test_sqlite_truncated_signatures(self):
        for length in range(len(SQLITE_HEADER)):
            with self.subTest(length=length):
                self.assertIsNone(filetype.guess(SQLITE_HEADER[:length]))

    def test_sqlite_plain_text(self):
        for text in (b'SQLite is a database library', b'SQLi example',
                     b'SQLite format 3\n'):
            with self.subTest(text=text):
                self.assertIsNone(filetype.guess(text))

    def test_sqlite_signature_mutations(self):
        for index in range(len(SQLITE_HEADER)):
            with self.subTest(index=index):
                data = bytearray(SQLITE_HEADER)
                data[index] ^= 1
                self.assertIsNone(filetype.guess(data))

    def test_real_sqlite_database(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'sample.sqlite')
            connection = sqlite3.connect(path)
            try:
                connection.execute('CREATE TABLE sample (value INTEGER)')
                connection.execute('INSERT INTO sample VALUES (42)')
                connection.commit()
                self.assertEqual(
                    connection.execute('SELECT value FROM sample').fetchone(),
                    (42,),
                )
            finally:
                connection.close()
            kind = filetype.guess(path)
            self.assertIsNotNone(kind)
            self.assertEqual(kind.mime, 'application/x-sqlite3')
            self.assertEqual(kind.extension, 'sqlite')
