/*
 * K=7 r=1/2 Viterbi decoder in portable C
 * Copyright Feb 2004, Phil Karn, KA9Q
 * May be used under the terms of the GNU Lesser General Public License (LGPL)
 */

#ifndef VITERBI_H_
#define VITERBI_H_

#include <stdint.h>

#define VITERBI_CONSTRAINT	7
#define VITERBI_TAIL		1
#define VITERBI_RATE		2

void *create_viterbi(int16_t len);
int init_viterbi(void *vp,int starting_state);
int update_viterbi(void *vp, unsigned char sym[], uint16_t npairs);
int chainback_viterbi(void *vp, unsigned char *data, unsigned int nbits,unsigned int endstate);
void delete_viterbi(void *vp);
void encode_viterbi(unsigned char * channel, unsigned char * data, int framebits);

#endif // VITERBI_H_
