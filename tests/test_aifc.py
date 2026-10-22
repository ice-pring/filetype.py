# -*- coding: utf-8 -*-

import io
import os
import unittest

import filetype
from filetype.types.audio import Aiff


FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')
AIFC_FILES = ('sample.aifc', 'sample_ulaw.aifc', 'sample_alaw.aifc')


class TestAifc(unittest.TestCase):
    # Generated with CPython 3.12's aifc writer: mono, 16-bit, 8000 Hz,
    # eight silent frames, using NONE, ULAW and ALAW compression.
    def test_complete_audio_files(self):
        for name in AIFC_FILES:
            with self.subTest(name=name):
                path = os.path.join(FIXTURES, name)
                with open(path, 'rb') as stream:
                    data = stream.read()
                for obj in (path, data, bytearray(data), memoryview(data),
                            io.BytesIO(data)):
                    self.assertEqual(filetype.guess_extension(obj), 'aifc')
                    self.assertEqual(filetype.guess_mime(obj), 'audio/x-aiff')
                    self.assertTrue(filetype.is_audio(obj))

    def test_type_registration(self):
        self.assertTrue(filetype.is_extension_supported('aifc'))
        kind = filetype.get_type(ext='aifc')
        self.assertIsNotNone(kind)
        self.assertEqual(kind.mime, 'audio/x-aiff')

    def test_uncompressed_aiff_keeps_its_extension(self):
        path = os.path.join(FIXTURES, 'sample.aiff')
        self.assertEqual(filetype.guess_extension(path), 'aiff')
        self.assertEqual(filetype.guess_mime(path), 'audio/x-aiff')
        self.assertTrue(filetype.is_audio(path))
        self.assertEqual(filetype.get_type(mime='audio/x-aiff').extension,
                         'aiff')

    def test_truncated_headers(self):
        kind = filetype.get_type(ext='aifc')
        self.assertIsNotNone(kind)
        header = b'FORM\x00\x00\x00\x52AIFC'
        for length in range(len(header)):
            with self.subTest(length=length):
                self.assertFalse(kind.match(header[:length]))
        self.assertTrue(kind.match(header))

    def test_rejects_other_iff_forms(self):
        kind = filetype.get_type(ext='aifc')
        self.assertIsNotNone(kind)
        for form in (b'AIFF', b'8SVX', b'ILBM', b'AIFF-C', b'aifc'):
            with self.subTest(form=form):
                self.assertFalse(kind.match(b'FORM\x00\x00\x00\x52' + form))
        self.assertFalse(kind.match(b'RIFF\x52\x00\x00\x00AIFC'))

    def test_aiff_does_not_match_aifc(self):
        self.assertFalse(Aiff().match(b'FORM\x00\x00\x00\x52AIFC'))


if __name__ == '__main__':
    unittest.main()
