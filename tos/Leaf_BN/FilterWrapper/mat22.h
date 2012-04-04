#ifndef MAT22_H
#define MAT22_H

typedef float mat22[2][2];
typedef float vec2[2];

inline void mat22_mult(mat22 in, mat22 mult, mat22 out)
{
  out[0][0] = in[0][0]*mult[0][0] + in[0][1]*mult[1][0];
  out[0][1] = in[0][0]*mult[0][1] + in[0][1]*mult[1][1];
  out[1][0] = in[1][0]*mult[0][0] + in[1][1]*mult[1][0];
  out[1][1] = in[1][0]*mult[0][1] + in[1][1]*mult[1][1];
  
}

inline int mat22_equals(mat22 a, mat22 b) 
{
  int i, j;
  for (i = 0; i < 2; i++) { 
    for (j = 0; j < 2; j++) { 
      if (a[i][j] != b[i][j])
	return 0;
    }
  }
  return 1;
}

inline void mat22_add(mat22 in, mat22 plus, mat22 out)
{
  out[0][0] = in[0][0] + plus[0][0];
  out[0][1] = in[0][1] + plus[0][1];
  out[1][0] = in[1][0] + plus[1][0];
  out[1][1] = in[1][1] + plus[1][1];
}

inline void mat22_dot_vs(vec2 in, float s, vec2 out)
{
  out[0] = s * in[0];
  out[1] = s * in[1];
}

inline float mat22_dot_vtv(vec2 a, vec2 b) 
{
  return a[0] * b[0] + a[1] * b[1];
}

inline void mat22_dot_vvt(vec2 in, vec2 vt, mat22 m) 
{
  m[0][0] = in[0] * vt[0];
  m[0][1] = in[0] * vt[1];
  m[1][0] = in[1] * vt[0];
  m[1][1] = in[1] * vt[1];
}

inline void mat22_dot_mv(mat22 a, vec2 b, vec2 c) 
{
  c[0] = a[0][0] * b[0] + a[0][1]*b[1];
  c[1] = a[1][0] * b[0] + a[1][1]*b[1];
}

inline void mat22_add_v(vec2 a, vec2 b, vec2 c) 
{
  c[0] = a[0] + b[0];
  c[1] = a[1] + b[1];
}

inline void mat22_copy_v(vec2 a, vec2 b) 
{
  b[0] = a[0] ;
  b[1] = a[1] ;
}

inline int mat22_equals_v(vec2 a, vec2 b)
{
  return a[0] == b[0] && a[1] == b[1];
}

inline void mat22_sub(mat22 a, mat22 b, mat22 c)
{
  int i, j;
  for (i = 0; i < 2; i++) { 
    for (j = 0; j < 2; j++) {
      c[i][j] = a[i][j] - b[i][j];
    }
  }
}

inline void mat22_copy(mat22 a, mat22 b)
{
  int i, j;
  for (i = 0; i < 2; i++) { 
    for (j = 0; j < 2; j++) {
      b[i][j] = a[i][j];
    }
  }
}



#endif
