# gr-aausat
GNUradio decoder for AAUSAT

This is an unofficial decoder for the AAUSAT satellites based on software
from the Aalborg university https://github.com/aausat/aausat4_beacon_parser

Features:
- FEC decoding from Aalborg bbctl software
- CSP header parsing
- Beacon parsing of EPS and COM fields
- The remaining fields of the beacon are not parsed, since I do not have the details of the format.
  I am trying to see if the university team can send me some details.

Installation:
 mkdir build
 cd build
 cmake ..
 make
 sudo make install
 
 Then you can open examples/oz4cub.grc with GNURadio Companion and adapt it to your needs.
