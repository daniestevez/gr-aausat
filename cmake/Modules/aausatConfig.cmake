INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_AAUSAT aausat)

FIND_PATH(
    AAUSAT_INCLUDE_DIRS
    NAMES aausat/api.h
    HINTS $ENV{AAUSAT_DIR}/include
        ${PC_AAUSAT_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    AAUSAT_LIBRARIES
    NAMES gnuradio-aausat
    HINTS $ENV{AAUSAT_DIR}/lib
        ${PC_AAUSAT_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(AAUSAT DEFAULT_MSG AAUSAT_LIBRARIES AAUSAT_INCLUDE_DIRS)
MARK_AS_ADVANCED(AAUSAT_LIBRARIES AAUSAT_INCLUDE_DIRS)

