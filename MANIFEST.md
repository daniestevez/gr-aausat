title: Unofficial AAUSAT decoder module
brief: AUUSAT decoder module based on software from the Aalborg university team
tags:
  - sdr
author:
  - Daniel Estevez <daniel@destevez.net>
copyright_owner:
  - Daniel Estevez
license: MIT
repo: https://github.com/daniestevez/gr-aausat/
website: http://destevez.net/
#icon: <icon_url> # Put a URL to a square image here that will be used as an icon on CGRAN
---
This is an unofficial GNURadio decoder for AAUSAT-4 based on software
published by Aalborg university.

Features:
- FEC decoding from Aalborg bbctl software
- CSP header parsing
- Beacon parsing of EPS and COM fields
- The remaining fields of the beacon are not parsed, since I do not have the details of the format
---
