# -*- coding: utf-8 -*-

import io
import os
import struct
import unittest

import filetype


FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestCaf(unittest.TestCase):
    def test_complete_audio_files(self):
        # Generated with FFmpeg: mono, 8000 Hz, eight silent samples,
        # using 16-bit PCM and Apple Lossless (ALAC), respectively.
        for name in ('sample.caf', 'sample_alac.caf'):
            with self.subTest(name=name):
                path = os.path.join(FIXTURES, name)
                with open(path, 'rb') as stream:
                    data = stream.read()
                for obj in (path, data, bytearray(data), memoryview(data),
                            io.BytesIO(data)):
                    self.assertEqual(filetype.guess_extension(obj), 'caf')
                    self.assertEqual(filetype.guess_mime(obj), 'audio/x-caf')
                    self.assertTrue(filetype.is_audio(obj))

    def test_registration(self):
        self.assertTrue(filetype.is_extension_supported('caf'))
        self.assertTrue(filetype.is_mime_supported('audio/x-caf'))
        kind = filetype.get_type(ext='caf')
        self.assertIsNotNone(kind)
        self.assertIs(kind, filetype.get_type(mime='audio/x-caf'))

    def test_truncated_headers(self):
        kind = filetype.get_type(ext='caf')
        self.assertIsNotNone(kind)
        header = b'caff\x00\x01\x00\x00'
        for length in range(len(header)):
            with self.subTest(length=length):
                self.assertFalse(kind.match(header[:length]))
        self.assertTrue(kind.match(header))

    def test_reserved_flags_are_ignored(self):
        # Apple requires readers to accept unknown flags for valid CAF v1.
        kind = filetype.get_type(ext='caf')
        self.assertIsNotNone(kind)
        for flags in (0, 1, 256, 65535):
            with self.subTest(flags=flags):
                header = b'caff\x00\x01' + struct.pack('>H', flags)
                for buf in (header, bytearray(header), memoryview(header)):
                    self.assertTrue(kind.match(buf))

    def test_rejects_invalid_magic_and_version(self):
        kind = filetype.get_type(ext='caf')
        self.assertIsNotNone(kind)
        for header in (b'CAFF\x00\x01\x00\x00',
                       b'caff\x00\x00\x00\x00',
                       b'caff\x00\x02\x00\x00',
                       b'caff\x01\x00\x00\x00',
                       b'caffeinated drink'):
            with self.subTest(header=header):
                self.assertFalse(kind.match(header))


if __name__ == '__main__':
    unittest.main()
