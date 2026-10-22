# -*- coding: utf-8 -*-
from __future__ import absolute_import
import codecs

from .base import Type


class IsoBmff(Type):
    """
    Implements the ISO-BMFF base type.
    """
    def __init__(self, mime, extension):
        super(IsoBmff, self).__init__(
            mime=mime,
            extension=extension
        )

    def _is_isobmff(self, buf):
        if len(buf) < 16 or buf[4:8] != b'ftyp':
            return False
        ftyp_len = int(codecs.encode(buf[0:4], 'hex'), 16)
        if ftyp_len == 1:
            # Extended-size boxes have a 16-byte header before the payload.
            if len(buf) < 24:
                return False
            ftyp_len = int(codecs.encode(buf[8:16], 'hex'), 16)
            if ftyp_len < 24:
                return False
        if len(buf) < ftyp_len:
            return False
        return True

    def _get_ftyp(self, buf):
        ftyp_len = int(codecs.encode(buf[0:4], 'hex'), 16)
        brand_offset = 8
        if ftyp_len == 1:
            ftyp_len = int(codecs.encode(buf[8:16], 'hex'), 16)
            brand_offset = 16
        major_brand = buf[brand_offset:brand_offset+4].decode(errors='ignore')
        minor_version = int(codecs.encode(
            buf[brand_offset+4:brand_offset+8], 'hex'), 16)
        compatible_brands = []
        for i in range(brand_offset + 8, ftyp_len, 4):
            compatible_brands.append(buf[i:i+4].decode(errors='ignore'))

        return major_brand, minor_version, compatible_brands
