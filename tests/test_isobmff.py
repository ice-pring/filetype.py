# -*- coding: utf-8 -*-

from __future__ import absolute_import

import struct
import unittest

import filetype
from filetype.types.isobmff import IsoBmff


def make_ftyp(major_brand, compatible_brands=(), extended=False):
    payload = major_brand + struct.pack('>I', 0x01020304)
    payload += b''.join(compatible_brands)
    if extended:
        return struct.pack('>I4sQ', 1, b'ftyp', 16 + len(payload)) + payload
    return struct.pack('>I4s', 8 + len(payload), b'ftyp') + payload


class TestIsoBmff(unittest.TestCase):
    def setUp(self):
        self.matcher = IsoBmff('application/octet-stream', 'bin')

    def test_parse_extended_ftyp_fields(self):
        data = make_ftyp(b'avif', (b'mif1', b'avif'), extended=True)
        self.assertTrue(self.matcher._is_isobmff(data))
        self.assertEqual(
            self.matcher._get_ftyp(data),
            ('avif', 0x01020304, ['mif1', 'avif']),
        )

    def check_brands(self, extended):
        cases = (
            (b'avif', (), 'image/avif', 'avif'),
            (b'heic', (), 'image/heic', 'heic'),
            (b'mp42', (), 'video/mp4', 'mp4'),
            (b'qt  ', (), 'video/quicktime', 'mov'),
            (b'mif1', (b'avif',), 'image/avif', 'avif'),
            (b'msf1', (b'heic',), 'image/heic', 'heic'),
            (b'zzzz', (b'mp41',), 'video/mp4', 'mp4'),
        )
        for major, compatible, mime, extension in cases:
            for buffer_type in (bytes, bytearray):
                with self.subTest(major=major, buffer_type=buffer_type):
                    data = buffer_type(make_ftyp(major, compatible, extended))
                    kind = filetype.guess(data)
                    self.assertIsNotNone(kind)
                    self.assertEqual(kind.mime, mime)
                    self.assertEqual(kind.extension, extension)

    def test_guess_extended_brands(self):
        self.check_brands(extended=True)

    def test_guess_standard_brands(self):
        self.check_brands(extended=False)

    def test_rejects_truncated_extended_box(self):
        data = make_ftyp(b'avif', (b'mif1', b'avif'), extended=True)
        for length in range(len(data)):
            with self.subTest(length=length):
                self.assertIsNone(filetype.guess(data[:length]))

    def test_rejects_invalid_extended_size(self):
        payload = b'avif' + struct.pack('>I', 0)
        for size in (0, 8, 16, 23, 25, (1 << 32) + 24):
            with self.subTest(size=size):
                data = struct.pack('>I4sQ', 1, b'ftyp', size) + payload
                self.assertFalse(self.matcher._is_isobmff(data))
                self.assertIsNone(filetype.guess(data))

    def test_stops_at_declared_extended_size(self):
        data = make_ftyp(b'zzzz', extended=True) + b'isom'
        self.assertEqual(
            self.matcher._get_ftyp(data),
            ('zzzz', 0x01020304, []),
        )
        self.assertIsNone(filetype.guess(data))
