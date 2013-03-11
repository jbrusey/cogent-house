/* horner.c
** Mth 351 Summer 2001
** Bent Petersen
**
** The numbers can be all on one line, or several lines,
** as long as they are separated by white space. Blank
** lines are ignored.
**
** Microsoft C/C++    cl horner.c
** GNU Project GCC    gcc -i horner.c -o horner

** coeefs order from c...x^4....x^n
*/

#include "horner.h"

float horner( int degree, float * coefs, float abscissa ) {

	float x;
	int k;

	x = coefs[degree];

	for ( k=degree-1; k>=0; k-- )
		x = x * abscissa + coefs[k];

	return x;
}
/*** END ***/

