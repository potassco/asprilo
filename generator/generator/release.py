# -*- coding: utf-8 -*-
"""Release information for the ASPRILO Instance Generator"""

name = 'gen'

_version_major = 0
_version_minor = 3
_version_patch = 1
_version_extra = '' #' (release)' '.dev'
_ver=[_version_major, _version_minor, _version_patch]
__version__ = '.'.join(map(str, _ver))
if _version_extra:
    __version__ = __version__ + _version_extra

description = "gen: asprilo instance generator"
