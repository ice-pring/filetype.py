# -*- coding: utf-8 -*-

import io
import os
import unittest

import filetype
from filetype.types.audio import Wav


FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestWave(unittest.TestCase):
    def test_complete_wave_variants(self):
        # RIFF/RIFX fixtures contain eight mono 16-bit PCM samples at 8000 Hz.
        # RF64 contains eight silent samples, written with FFmpeg -rf64 always.
        for variant in ('riff', 'rifx', 'rf64'):
            with self.subTest(variant=variant):
                path = os.path.join(FIXTURES, 'sample_' + variant + '.wav')
                with open(path, 'rb') as stream:
                    data = stream.read()
                for obj in (path, data, bytearray(data), memoryview(data),
                            io.BytesIO(data)):
                    self.assertEqual(filetype.guess_extension(obj), 'wav')
                    self.assertEqual(filetype.guess_mime(obj), 'audio/x-wav')
                    self.assertTrue(filetype.is_audio(obj))

    def test_truncated_headers(self):
        for magic in (b'RIFF', b'RIFX', b'RF64'):
            header = magic + b'\xff\xff\xff\xffWAVE'
            for length in range(len(header)):
                with self.subTest(magic=magic, length=length):
                    self.assertFalse(Wav().match(header[:length]))
            self.assertTrue(Wav().match(header))

    def test_requires_wave_form_type(self):
        for magic in (b'RIFF', b'RIFX', b'RF64'):
            for form in (b'AVI ', b'WEBP', b'RMID', b'wave'):
                with self.subTest(magic=magic, form=form):
                    self.assertFalse(Wav().match(magic + b'\0' * 4 + form))

    def test_rejects_unknown_container_signatures(self):
        for magic in (b'RIFZ', b'RIFF64', b'riff', b'FORM', b'\0' * 4):
            with self.subTest(magic=magic):
                self.assertFalse(Wav().match(magic + b'\0' * 4 + b'WAVE'))


if __name__ == '__main__':
    unittest.main()
