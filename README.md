# gr-aausat
GNUradio decoder for AAUSAT

This is an unofficial decoder for the AAUSAT satellites based on
[software from the Aalborg university](https://github.com/aausat/aausat4_beacon_parser).

Currently, it only works with AAUSAT-4.

There is a complete telemetry decoder based on this software in
[gr-satellites](https://github.com/daniestevez/gr-satellites).

**Features:**
  * FEC decoding from Aalborg bbctl software
  * CSP header parsing using gr-csp
  * Beacon parsing of EPS and COM fields (format take from the university team parser)
  * Beacon parsing of ADCS and some AIS2 fields (format reverse engineered)

**Prerequisites:**
You need to install [gr-csp](https://github.com/daniestevez/gr-csp)
and [gr-synctags](https://github.com/daniestevez/gr-synctags).

**Installation:**
```bash
 mkdir build
 cd build
 cmake ..
 make
 sudo make install
 sudo ldconfig
 ```
 
 Then you can open `examples/aausat-4.grc` to test that the decoder is working.
