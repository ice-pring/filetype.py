# -*- coding: utf-8 -*-

import io
import os
import struct
import unittest

import filetype
from filetype.types.font import Otf, Ttf


FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestSfnt(unittest.TestCase):
    def test_complete_fonts_with_256_tables(self):
        # Generated with FontTools: two glyphs (.notdef and a triangle A),
        # with custom Xnnn tables added to reach 256 tables in each font.
        for ext in ('ttf', 'otf'):
            with self.subTest(ext=ext):
                path = os.path.join(FIXTURES, 'sample_256_tables.' + ext)
                with open(path, 'rb') as stream:
                    data = stream.read()
                self.assertEqual(struct.unpack('>H', data[4:6])[0], 256)
                for obj in (path, data, bytearray(data), memoryview(data),
                            io.BytesIO(data)):
                    self.assertEqual(filetype.guess_extension(obj), ext)
                    self.assertEqual(filetype.guess_mime(obj),
                                     'application/font-sfnt')
                    self.assertTrue(filetype.is_font(obj))

    def test_table_count_is_not_part_of_signature(self):
        for matcher, version in ((Ttf(), b'\x00\x01\x00\x00'),
                                 (Otf(), b'OTTO')):
            for count in (1, 16, 255, 256, 257, 511, 4095):
                with self.subTest(ext=matcher.extension, count=count):
                    power = 1 << (count.bit_length() - 1)
                    header = version + struct.pack(
                        '>HHHH', count, power * 16,
                        power.bit_length() - 1, (count - power) * 16)
                    for buf in (header, bytearray(header), memoryview(header)):
                        self.assertTrue(matcher.match(buf))
                    self.assertEqual(filetype.guess_extension(header),
                                     matcher.extension)

    def test_truncated_signatures(self):
        for matcher, header in ((Ttf(), b'\x00\x01\x00\x00\x01\x00'),
                                (Otf(), b'OTTO\x01\x00')):
            for length in range(5):
                with self.subTest(ext=matcher.extension, length=length):
                    self.assertFalse(matcher.match(header[:length]))

    def test_rejects_other_sfnt_versions(self):
        for version in (b'ttcf', b'wOFF', b'wOF2', b'\x00\x02\x00\x00',
                        b'otto'):
            with self.subTest(version=version):
                header = version + b'\x01\x00' + b'\x00' * 6
                self.assertFalse(Ttf().match(header))
                self.assertFalse(Otf().match(header))


if __name__ == '__main__':
    unittest.main()
