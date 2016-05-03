add_library(bbfec SHARED randomizer.c rs.c viterbi.c)
install(TARGETS bbfec DESTINATION lib)
