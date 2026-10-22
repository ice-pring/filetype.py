# -*- coding: utf-8 -*-

from __future__ import absolute_import

import struct
import unittest

import filetype
from filetype.types.archive import Zstd


# A complete Zstandard frame containing an empty raw block.
EMPTY_FRAME = b'\x28\xb5\x2f\xfd\x20\x00\x01\x00\x00'


def skippable(payload=b'', magic=0x184D2A50):
    return struct.pack('<II', magic, len(payload)) + payload


class TestZstd(unittest.TestCase):
    def test_long_skippable_chain(self):
        data = skippable() * 1000 + EMPTY_FRAME
        self.assertLess(len(data), 8192)
        for buffer_type in (bytes, bytearray, memoryview):
            with self.subTest(buffer_type=buffer_type):
                kind = filetype.guess(buffer_type(data))
                self.assertIsNotNone(kind)
                self.assertEqual(kind.mime, 'application/zstd')
                self.assertEqual(kind.extension, 'zst')

    def test_long_chain_without_zstd(self):
        for suffix in (b'', b'invalid', EMPTY_FRAME[:3]):
            with self.subTest(suffix=suffix):
                self.assertIsNone(filetype.guess(skippable() * 1000 + suffix))

    def test_all_skippable_magics(self):
        for magic in range(0x184D2A50, 0x184D2A60):
            with self.subTest(magic=magic):
                data = skippable(b'metadata', magic) + EMPTY_FRAME
                self.assertEqual(filetype.guess_mime(data), 'application/zstd')

    def test_skips_payload_contents(self):
        prefix = skippable(EMPTY_FRAME) + skippable() + skippable(b'metadata')
        self.assertIsNone(filetype.guess(prefix + b'invalid'))
        self.assertEqual(
            filetype.guess_mime(prefix + EMPTY_FRAME), 'application/zstd')

    def test_truncated_skippable_frames(self):
        prefix = skippable(b'metadata')
        tail = skippable(b'payload')
        for length in range(len(tail)):
            with self.subTest(length=length):
                self.assertIsNone(filetype.guess(prefix + tail[:length]))

    def test_invalid_skippable_frames(self):
        for magic in (0x184D2A4F, 0x184D2A60):
            with self.subTest(magic=magic):
                self.assertIsNone(filetype.guess(
                    skippable(magic=magic) + EMPTY_FRAME))
        oversized = struct.pack('<II', 0x184D2A50, 0xFFFFFFFF)
        self.assertIsNone(filetype.guess(
            skippable() + oversized + EMPTY_FRAME))

    def test_preserves_signature_read_limit(self):
        data = skippable() * 1024 + EMPTY_FRAME
        self.assertIsNone(filetype.guess(data))

    def test_legacy_zstd_headers(self):
        for first_byte in range(0x22, 0x29):
            with self.subTest(first_byte=first_byte):
                header = bytearray([first_byte, 0xb5, 0x2f, 0xfd])
                self.assertTrue(Zstd().match(header))
                self.assertTrue(Zstd().match(skippable() + header))
