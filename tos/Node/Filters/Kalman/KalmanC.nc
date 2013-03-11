// -*- c -*- 
#include <stdint.h>
#include "Filter.h"
//#define DEFAULT_ACCEL_COV 1e-5;


generic module KalmanC(float x_init, 
		       float dx_init, 
		       bool x_init_provided,
		       float accel_init,
		       float R_init,
		       float p_covar)
			   
{
  provides interface Filter;
  provides interface Predict;
}
implementation
{
  float accel = accel_init;
  float R = R_init;
  vec2 xhat = {x_init, dx_init};
  bool xhat_init = x_init_provided;
  mat22 P = {{p_covar, 0.},{0.,p_covar}};
  vec2 H = {1,0};
  uint32_t current_time = 0;
  mat22 F = {{1., 1.},{0., 1.}};
  mat22 FT = {{1., 0.},{1., 1.}};
  vec2 G = {1., 1.};
  mat22 I = {{1.,0.},{0.,1.}};

  uint32_t subtract_time(uint32_t new_time, uint32_t old_time)
  {
    if (new_time < old_time) // deal with overflow
      return ((UINT32_MAX - old_time) + new_time + 1);
    else
      return (new_time - old_time);
  }
	
  command void Filter.filter(float z, uint32_t t, vec2 v)
  {
    mat22 Q,Pminus;
    vec2 xhatminus, K;
    float y;
    float S;
    float deltaT;		
    vec2 v_temp;
    mat22 m_temp, m_temp2;
			
		
    //time update
    deltaT = (float) (subtract_time(t, current_time) / 1024.);
    current_time = t;
    if (! xhat_init) { 
      xhat_init = TRUE;
      xhat[0] = z;
      xhat[1] = 0.;
      mat22_copy_v(xhat, v);
      return;
    }
		
    //sort out F,FT,G,GT
    F[0][1] = FT[1][0] = deltaT;
    G[0] = deltaT * deltaT / 2.;
    G[1] = deltaT;


    // Q = G . accel . G^T
    mat22_dot_vs(G, accel, v_temp);
    mat22_dot_vvt(v_temp, G, Q); 
		

    // xhatminus = F . xhat
    // (2x1) = (2x2) x (2x1)
    mat22_dot_mv(F, xhat, xhatminus);
		
    // Pminus = F . P . F^T + Q
    //(2x2) = (2x2) x (2x2) x (2x2) + (2x2)
    mat22_mult(F, P, m_temp);
    mat22_mult(m_temp, FT, m_temp2);
    mat22_add(m_temp2, Q, Pminus);
		
    // y = z - H . xhatminus
    //(1x1) = (1x1) - (1x2)*(2x1)
    y = z - mat22_dot_vtv(H, xhatminus);

    // S = H . Pminus . H^T + R
    //(1x1) = ((1x2) x (2x2)) x (2x1) + (1x1)
    mat22_dot_mv(Pminus, H, v_temp);
    S = mat22_dot_vtv(H, v_temp) + R;

    // K = Pminus . H^T .  S^-1
    // (2x1) = (2x2) x (2x1) x (1x1)
    mat22_dot_vs(v_temp, 1/S, K);

    // xhat = xhatminus + K . y
    //(2x1) = (2x1) + (2x1) x (1x1)
    mat22_dot_vs(K, y, v_temp);
    mat22_add_v(xhatminus, v_temp, xhat);

    // P = (I - K . H) . Pminus
    //(2x2) = ((2x2) - (2x1) x (1x2)) x (2x2)
    mat22_dot_vvt(K, H, m_temp);
    mat22_sub(I, m_temp, m_temp2);
    mat22_mult(m_temp2, Pminus, P);
   
    xhat[1]=xhat[1];
    mat22_copy_v(xhat, v);
  }
  

  /**
   * Get prediction of state based on a past state and current time.
   * @param fs "ONE FilterState *" state to use as basis for prediction
   * @param t time to predict for (usually the current time or the sense time)
   */
  command float Predict.predictState(FilterState *fs, uint32_t t)
  {
    float deltaT;
    deltaT = (float) subtract_time(t, fs->time) / 1024.0;
    return fs->x + fs->dx * deltaT;
  }		
}
