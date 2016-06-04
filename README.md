# gr-aausat
GNUradio decoder for AAUSAT

This is an unofficial decoder for the AAUSAT satellites based on software
from the Aalborg university https://github.com/aausat/aausat4_beacon_parser

Features:
- FEC decoding from Aalborg bbctl software
- CSP header parsing using gr-csp
- Beacon parsing of EPS and COM fields (format take from the university team parser)
- Beacon parsing of ADCS and some AIS2 fields (format reverse engineered)

Prerequisites:
 You need to install https://github.com/daniestevez/gr-csp and https://github.com/daniestevez/gr-synctags

Installation:
 mkdir build
 cd build
 cmake ..
 make
 sudo make install
 
 Then you can open examples/oz4cub.grc with GNURadio Companion and adapt it to your needs.
