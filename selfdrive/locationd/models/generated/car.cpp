#include "car.h"

namespace {
#define DIM 9
#define EDIM 9
#define MEDIM 9
typedef void (*Hfun)(double *, double *, double *);

double mass;

void set_mass(double x){ mass = x;}

double rotational_inertia;

void set_rotational_inertia(double x){ rotational_inertia = x;}

double center_to_front;

void set_center_to_front(double x){ center_to_front = x;}

double center_to_rear;

void set_center_to_rear(double x){ center_to_rear = x;}

double stiffness_front;

void set_stiffness_front(double x){ stiffness_front = x;}

double stiffness_rear;

void set_stiffness_rear(double x){ stiffness_rear = x;}
const static double MAHA_THRESH_25 = 3.8414588206941227;
const static double MAHA_THRESH_24 = 5.991464547107981;
const static double MAHA_THRESH_30 = 3.8414588206941227;
const static double MAHA_THRESH_26 = 3.8414588206941227;
const static double MAHA_THRESH_27 = 3.8414588206941227;
const static double MAHA_THRESH_29 = 3.8414588206941227;
const static double MAHA_THRESH_28 = 3.8414588206941227;
const static double MAHA_THRESH_31 = 3.8414588206941227;

/******************************************************************************
 *                       Code generated with SymPy 1.12                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_1823493661961729959) {
   out_1823493661961729959[0] = delta_x[0] + nom_x[0];
   out_1823493661961729959[1] = delta_x[1] + nom_x[1];
   out_1823493661961729959[2] = delta_x[2] + nom_x[2];
   out_1823493661961729959[3] = delta_x[3] + nom_x[3];
   out_1823493661961729959[4] = delta_x[4] + nom_x[4];
   out_1823493661961729959[5] = delta_x[5] + nom_x[5];
   out_1823493661961729959[6] = delta_x[6] + nom_x[6];
   out_1823493661961729959[7] = delta_x[7] + nom_x[7];
   out_1823493661961729959[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_7001705699576052991) {
   out_7001705699576052991[0] = -nom_x[0] + true_x[0];
   out_7001705699576052991[1] = -nom_x[1] + true_x[1];
   out_7001705699576052991[2] = -nom_x[2] + true_x[2];
   out_7001705699576052991[3] = -nom_x[3] + true_x[3];
   out_7001705699576052991[4] = -nom_x[4] + true_x[4];
   out_7001705699576052991[5] = -nom_x[5] + true_x[5];
   out_7001705699576052991[6] = -nom_x[6] + true_x[6];
   out_7001705699576052991[7] = -nom_x[7] + true_x[7];
   out_7001705699576052991[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_4716016119777539041) {
   out_4716016119777539041[0] = 1.0;
   out_4716016119777539041[1] = 0;
   out_4716016119777539041[2] = 0;
   out_4716016119777539041[3] = 0;
   out_4716016119777539041[4] = 0;
   out_4716016119777539041[5] = 0;
   out_4716016119777539041[6] = 0;
   out_4716016119777539041[7] = 0;
   out_4716016119777539041[8] = 0;
   out_4716016119777539041[9] = 0;
   out_4716016119777539041[10] = 1.0;
   out_4716016119777539041[11] = 0;
   out_4716016119777539041[12] = 0;
   out_4716016119777539041[13] = 0;
   out_4716016119777539041[14] = 0;
   out_4716016119777539041[15] = 0;
   out_4716016119777539041[16] = 0;
   out_4716016119777539041[17] = 0;
   out_4716016119777539041[18] = 0;
   out_4716016119777539041[19] = 0;
   out_4716016119777539041[20] = 1.0;
   out_4716016119777539041[21] = 0;
   out_4716016119777539041[22] = 0;
   out_4716016119777539041[23] = 0;
   out_4716016119777539041[24] = 0;
   out_4716016119777539041[25] = 0;
   out_4716016119777539041[26] = 0;
   out_4716016119777539041[27] = 0;
   out_4716016119777539041[28] = 0;
   out_4716016119777539041[29] = 0;
   out_4716016119777539041[30] = 1.0;
   out_4716016119777539041[31] = 0;
   out_4716016119777539041[32] = 0;
   out_4716016119777539041[33] = 0;
   out_4716016119777539041[34] = 0;
   out_4716016119777539041[35] = 0;
   out_4716016119777539041[36] = 0;
   out_4716016119777539041[37] = 0;
   out_4716016119777539041[38] = 0;
   out_4716016119777539041[39] = 0;
   out_4716016119777539041[40] = 1.0;
   out_4716016119777539041[41] = 0;
   out_4716016119777539041[42] = 0;
   out_4716016119777539041[43] = 0;
   out_4716016119777539041[44] = 0;
   out_4716016119777539041[45] = 0;
   out_4716016119777539041[46] = 0;
   out_4716016119777539041[47] = 0;
   out_4716016119777539041[48] = 0;
   out_4716016119777539041[49] = 0;
   out_4716016119777539041[50] = 1.0;
   out_4716016119777539041[51] = 0;
   out_4716016119777539041[52] = 0;
   out_4716016119777539041[53] = 0;
   out_4716016119777539041[54] = 0;
   out_4716016119777539041[55] = 0;
   out_4716016119777539041[56] = 0;
   out_4716016119777539041[57] = 0;
   out_4716016119777539041[58] = 0;
   out_4716016119777539041[59] = 0;
   out_4716016119777539041[60] = 1.0;
   out_4716016119777539041[61] = 0;
   out_4716016119777539041[62] = 0;
   out_4716016119777539041[63] = 0;
   out_4716016119777539041[64] = 0;
   out_4716016119777539041[65] = 0;
   out_4716016119777539041[66] = 0;
   out_4716016119777539041[67] = 0;
   out_4716016119777539041[68] = 0;
   out_4716016119777539041[69] = 0;
   out_4716016119777539041[70] = 1.0;
   out_4716016119777539041[71] = 0;
   out_4716016119777539041[72] = 0;
   out_4716016119777539041[73] = 0;
   out_4716016119777539041[74] = 0;
   out_4716016119777539041[75] = 0;
   out_4716016119777539041[76] = 0;
   out_4716016119777539041[77] = 0;
   out_4716016119777539041[78] = 0;
   out_4716016119777539041[79] = 0;
   out_4716016119777539041[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_8418266052988918400) {
   out_8418266052988918400[0] = state[0];
   out_8418266052988918400[1] = state[1];
   out_8418266052988918400[2] = state[2];
   out_8418266052988918400[3] = state[3];
   out_8418266052988918400[4] = state[4];
   out_8418266052988918400[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_8418266052988918400[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_8418266052988918400[7] = state[7];
   out_8418266052988918400[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6406240497487519515) {
   out_6406240497487519515[0] = 1;
   out_6406240497487519515[1] = 0;
   out_6406240497487519515[2] = 0;
   out_6406240497487519515[3] = 0;
   out_6406240497487519515[4] = 0;
   out_6406240497487519515[5] = 0;
   out_6406240497487519515[6] = 0;
   out_6406240497487519515[7] = 0;
   out_6406240497487519515[8] = 0;
   out_6406240497487519515[9] = 0;
   out_6406240497487519515[10] = 1;
   out_6406240497487519515[11] = 0;
   out_6406240497487519515[12] = 0;
   out_6406240497487519515[13] = 0;
   out_6406240497487519515[14] = 0;
   out_6406240497487519515[15] = 0;
   out_6406240497487519515[16] = 0;
   out_6406240497487519515[17] = 0;
   out_6406240497487519515[18] = 0;
   out_6406240497487519515[19] = 0;
   out_6406240497487519515[20] = 1;
   out_6406240497487519515[21] = 0;
   out_6406240497487519515[22] = 0;
   out_6406240497487519515[23] = 0;
   out_6406240497487519515[24] = 0;
   out_6406240497487519515[25] = 0;
   out_6406240497487519515[26] = 0;
   out_6406240497487519515[27] = 0;
   out_6406240497487519515[28] = 0;
   out_6406240497487519515[29] = 0;
   out_6406240497487519515[30] = 1;
   out_6406240497487519515[31] = 0;
   out_6406240497487519515[32] = 0;
   out_6406240497487519515[33] = 0;
   out_6406240497487519515[34] = 0;
   out_6406240497487519515[35] = 0;
   out_6406240497487519515[36] = 0;
   out_6406240497487519515[37] = 0;
   out_6406240497487519515[38] = 0;
   out_6406240497487519515[39] = 0;
   out_6406240497487519515[40] = 1;
   out_6406240497487519515[41] = 0;
   out_6406240497487519515[42] = 0;
   out_6406240497487519515[43] = 0;
   out_6406240497487519515[44] = 0;
   out_6406240497487519515[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_6406240497487519515[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_6406240497487519515[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6406240497487519515[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6406240497487519515[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_6406240497487519515[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_6406240497487519515[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_6406240497487519515[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_6406240497487519515[53] = -9.8000000000000007*dt;
   out_6406240497487519515[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6406240497487519515[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6406240497487519515[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6406240497487519515[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6406240497487519515[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6406240497487519515[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6406240497487519515[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6406240497487519515[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6406240497487519515[62] = 0;
   out_6406240497487519515[63] = 0;
   out_6406240497487519515[64] = 0;
   out_6406240497487519515[65] = 0;
   out_6406240497487519515[66] = 0;
   out_6406240497487519515[67] = 0;
   out_6406240497487519515[68] = 0;
   out_6406240497487519515[69] = 0;
   out_6406240497487519515[70] = 1;
   out_6406240497487519515[71] = 0;
   out_6406240497487519515[72] = 0;
   out_6406240497487519515[73] = 0;
   out_6406240497487519515[74] = 0;
   out_6406240497487519515[75] = 0;
   out_6406240497487519515[76] = 0;
   out_6406240497487519515[77] = 0;
   out_6406240497487519515[78] = 0;
   out_6406240497487519515[79] = 0;
   out_6406240497487519515[80] = 1;
}
void h_25(double *state, double *unused, double *out_9109286272586353339) {
   out_9109286272586353339[0] = state[6];
}
void H_25(double *state, double *unused, double *out_449787556617676611) {
   out_449787556617676611[0] = 0;
   out_449787556617676611[1] = 0;
   out_449787556617676611[2] = 0;
   out_449787556617676611[3] = 0;
   out_449787556617676611[4] = 0;
   out_449787556617676611[5] = 0;
   out_449787556617676611[6] = 1;
   out_449787556617676611[7] = 0;
   out_449787556617676611[8] = 0;
}
void h_24(double *state, double *unused, double *out_789680335081929477) {
   out_789680335081929477[0] = state[4];
   out_789680335081929477[1] = state[5];
}
void H_24(double *state, double *unused, double *out_2622437155623176177) {
   out_2622437155623176177[0] = 0;
   out_2622437155623176177[1] = 0;
   out_2622437155623176177[2] = 0;
   out_2622437155623176177[3] = 0;
   out_2622437155623176177[4] = 1;
   out_2622437155623176177[5] = 0;
   out_2622437155623176177[6] = 0;
   out_2622437155623176177[7] = 0;
   out_2622437155623176177[8] = 0;
   out_2622437155623176177[9] = 0;
   out_2622437155623176177[10] = 0;
   out_2622437155623176177[11] = 0;
   out_2622437155623176177[12] = 0;
   out_2622437155623176177[13] = 0;
   out_2622437155623176177[14] = 1;
   out_2622437155623176177[15] = 0;
   out_2622437155623176177[16] = 0;
   out_2622437155623176177[17] = 0;
}
void h_30(double *state, double *unused, double *out_3170343761152063974) {
   out_3170343761152063974[0] = state[4];
}
void H_30(double *state, double *unused, double *out_4977483886745284809) {
   out_4977483886745284809[0] = 0;
   out_4977483886745284809[1] = 0;
   out_4977483886745284809[2] = 0;
   out_4977483886745284809[3] = 0;
   out_4977483886745284809[4] = 1;
   out_4977483886745284809[5] = 0;
   out_4977483886745284809[6] = 0;
   out_4977483886745284809[7] = 0;
   out_4977483886745284809[8] = 0;
}
void h_26(double *state, double *unused, double *out_1831329506508781671) {
   out_1831329506508781671[0] = state[7];
}
void H_26(double *state, double *unused, double *out_4191290875491732835) {
   out_4191290875491732835[0] = 0;
   out_4191290875491732835[1] = 0;
   out_4191290875491732835[2] = 0;
   out_4191290875491732835[3] = 0;
   out_4191290875491732835[4] = 0;
   out_4191290875491732835[5] = 0;
   out_4191290875491732835[6] = 0;
   out_4191290875491732835[7] = 1;
   out_4191290875491732835[8] = 0;
}
void h_27(double *state, double *unused, double *out_4107613004925507694) {
   out_4107613004925507694[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7152247198545709720) {
   out_7152247198545709720[0] = 0;
   out_7152247198545709720[1] = 0;
   out_7152247198545709720[2] = 0;
   out_7152247198545709720[3] = 1;
   out_7152247198545709720[4] = 0;
   out_7152247198545709720[5] = 0;
   out_7152247198545709720[6] = 0;
   out_7152247198545709720[7] = 0;
   out_7152247198545709720[8] = 0;
}
void h_29(double *state, double *unused, double *out_470163476671485344) {
   out_470163476671485344[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4467252542430892625) {
   out_4467252542430892625[0] = 0;
   out_4467252542430892625[1] = 1;
   out_4467252542430892625[2] = 0;
   out_4467252542430892625[3] = 0;
   out_4467252542430892625[4] = 0;
   out_4467252542430892625[5] = 0;
   out_4467252542430892625[6] = 0;
   out_4467252542430892625[7] = 0;
   out_4467252542430892625[8] = 0;
}
void h_28(double *state, double *unused, double *out_5051122857827170129) {
   out_5051122857827170129[0] = state[0];
}
void H_28(double *state, double *unused, double *out_2503622270865566374) {
   out_2503622270865566374[0] = 1;
   out_2503622270865566374[1] = 0;
   out_2503622270865566374[2] = 0;
   out_2503622270865566374[3] = 0;
   out_2503622270865566374[4] = 0;
   out_2503622270865566374[5] = 0;
   out_2503622270865566374[6] = 0;
   out_2503622270865566374[7] = 0;
   out_2503622270865566374[8] = 0;
}
void h_31(double *state, double *unused, double *out_1346021015765680898) {
   out_1346021015765680898[0] = state[8];
}
void H_31(double *state, double *unused, double *out_4817498977725084311) {
   out_4817498977725084311[0] = 0;
   out_4817498977725084311[1] = 0;
   out_4817498977725084311[2] = 0;
   out_4817498977725084311[3] = 0;
   out_4817498977725084311[4] = 0;
   out_4817498977725084311[5] = 0;
   out_4817498977725084311[6] = 0;
   out_4817498977725084311[7] = 0;
   out_4817498977725084311[8] = 1;
}
#include <eigen3/Eigen/Dense>
#include <iostream>

typedef Eigen::Matrix<double, DIM, DIM, Eigen::RowMajor> DDM;
typedef Eigen::Matrix<double, EDIM, EDIM, Eigen::RowMajor> EEM;
typedef Eigen::Matrix<double, DIM, EDIM, Eigen::RowMajor> DEM;

void predict(double *in_x, double *in_P, double *in_Q, double dt) {
  typedef Eigen::Matrix<double, MEDIM, MEDIM, Eigen::RowMajor> RRM;

  double nx[DIM] = {0};
  double in_F[EDIM*EDIM] = {0};

  // functions from sympy
  f_fun(in_x, dt, nx);
  F_fun(in_x, dt, in_F);


  EEM F(in_F);
  EEM P(in_P);
  EEM Q(in_Q);

  RRM F_main = F.topLeftCorner(MEDIM, MEDIM);
  P.topLeftCorner(MEDIM, MEDIM) = (F_main * P.topLeftCorner(MEDIM, MEDIM)) * F_main.transpose();
  P.topRightCorner(MEDIM, EDIM - MEDIM) = F_main * P.topRightCorner(MEDIM, EDIM - MEDIM);
  P.bottomLeftCorner(EDIM - MEDIM, MEDIM) = P.bottomLeftCorner(EDIM - MEDIM, MEDIM) * F_main.transpose();

  P = P + dt*Q;

  // copy out state
  memcpy(in_x, nx, DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
}

// note: extra_args dim only correct when null space projecting
// otherwise 1
template <int ZDIM, int EADIM, bool MAHA_TEST>
void update(double *in_x, double *in_P, Hfun h_fun, Hfun H_fun, Hfun Hea_fun, double *in_z, double *in_R, double *in_ea, double MAHA_THRESHOLD) {
  typedef Eigen::Matrix<double, ZDIM, ZDIM, Eigen::RowMajor> ZZM;
  typedef Eigen::Matrix<double, ZDIM, DIM, Eigen::RowMajor> ZDM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, EDIM, Eigen::RowMajor> XEM;
  //typedef Eigen::Matrix<double, EDIM, ZDIM, Eigen::RowMajor> EZM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, 1> X1M;
  typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> XXM;

  double in_hx[ZDIM] = {0};
  double in_H[ZDIM * DIM] = {0};
  double in_H_mod[EDIM * DIM] = {0};
  double delta_x[EDIM] = {0};
  double x_new[DIM] = {0};


  // state x, P
  Eigen::Matrix<double, ZDIM, 1> z(in_z);
  EEM P(in_P);
  ZZM pre_R(in_R);

  // functions from sympy
  h_fun(in_x, in_ea, in_hx);
  H_fun(in_x, in_ea, in_H);
  ZDM pre_H(in_H);

  // get y (y = z - hx)
  Eigen::Matrix<double, ZDIM, 1> pre_y(in_hx); pre_y = z - pre_y;
  X1M y; XXM H; XXM R;
  if (Hea_fun){
    typedef Eigen::Matrix<double, ZDIM, EADIM, Eigen::RowMajor> ZAM;
    double in_Hea[ZDIM * EADIM] = {0};
    Hea_fun(in_x, in_ea, in_Hea);
    ZAM Hea(in_Hea);
    XXM A = Hea.transpose().fullPivLu().kernel();


    y = A.transpose() * pre_y;
    H = A.transpose() * pre_H;
    R = A.transpose() * pre_R * A;
  } else {
    y = pre_y;
    H = pre_H;
    R = pre_R;
  }
  // get modified H
  H_mod_fun(in_x, in_H_mod);
  DEM H_mod(in_H_mod);
  XEM H_err = H * H_mod;

  // Do mahalobis distance test
  if (MAHA_TEST){
    XXM a = (H_err * P * H_err.transpose() + R).inverse();
    double maha_dist = y.transpose() * a * y;
    if (maha_dist > MAHA_THRESHOLD){
      R = 1.0e16 * R;
    }
  }

  // Outlier resilient weighting
  double weight = 1;//(1.5)/(1 + y.squaredNorm()/R.sum());

  // kalman gains and I_KH
  XXM S = ((H_err * P) * H_err.transpose()) + R/weight;
  XEM KT = S.fullPivLu().solve(H_err * P.transpose());
  //EZM K = KT.transpose(); TODO: WHY DOES THIS NOT COMPILE?
  //EZM K = S.fullPivLu().solve(H_err * P.transpose()).transpose();
  //std::cout << "Here is the matrix rot:\n" << K << std::endl;
  EEM I_KH = Eigen::Matrix<double, EDIM, EDIM>::Identity() - (KT.transpose() * H_err);

  // update state by injecting dx
  Eigen::Matrix<double, EDIM, 1> dx(delta_x);
  dx  = (KT.transpose() * y);
  memcpy(delta_x, dx.data(), EDIM * sizeof(double));
  err_fun(in_x, delta_x, x_new);
  Eigen::Matrix<double, DIM, 1> x(x_new);

  // update cov
  P = ((I_KH * P) * I_KH.transpose()) + ((KT.transpose() * R) * KT);

  // copy out state
  memcpy(in_x, x.data(), DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
  memcpy(in_z, y.data(), y.rows() * sizeof(double));
}




}
extern "C" {

void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_25, H_25, NULL, in_z, in_R, in_ea, MAHA_THRESH_25);
}
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<2, 3, 0>(in_x, in_P, h_24, H_24, NULL, in_z, in_R, in_ea, MAHA_THRESH_24);
}
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_30, H_30, NULL, in_z, in_R, in_ea, MAHA_THRESH_30);
}
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_26, H_26, NULL, in_z, in_R, in_ea, MAHA_THRESH_26);
}
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_27, H_27, NULL, in_z, in_R, in_ea, MAHA_THRESH_27);
}
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_29, H_29, NULL, in_z, in_R, in_ea, MAHA_THRESH_29);
}
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_28, H_28, NULL, in_z, in_R, in_ea, MAHA_THRESH_28);
}
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_31, H_31, NULL, in_z, in_R, in_ea, MAHA_THRESH_31);
}
void car_err_fun(double *nom_x, double *delta_x, double *out_1823493661961729959) {
  err_fun(nom_x, delta_x, out_1823493661961729959);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7001705699576052991) {
  inv_err_fun(nom_x, true_x, out_7001705699576052991);
}
void car_H_mod_fun(double *state, double *out_4716016119777539041) {
  H_mod_fun(state, out_4716016119777539041);
}
void car_f_fun(double *state, double dt, double *out_8418266052988918400) {
  f_fun(state,  dt, out_8418266052988918400);
}
void car_F_fun(double *state, double dt, double *out_6406240497487519515) {
  F_fun(state,  dt, out_6406240497487519515);
}
void car_h_25(double *state, double *unused, double *out_9109286272586353339) {
  h_25(state, unused, out_9109286272586353339);
}
void car_H_25(double *state, double *unused, double *out_449787556617676611) {
  H_25(state, unused, out_449787556617676611);
}
void car_h_24(double *state, double *unused, double *out_789680335081929477) {
  h_24(state, unused, out_789680335081929477);
}
void car_H_24(double *state, double *unused, double *out_2622437155623176177) {
  H_24(state, unused, out_2622437155623176177);
}
void car_h_30(double *state, double *unused, double *out_3170343761152063974) {
  h_30(state, unused, out_3170343761152063974);
}
void car_H_30(double *state, double *unused, double *out_4977483886745284809) {
  H_30(state, unused, out_4977483886745284809);
}
void car_h_26(double *state, double *unused, double *out_1831329506508781671) {
  h_26(state, unused, out_1831329506508781671);
}
void car_H_26(double *state, double *unused, double *out_4191290875491732835) {
  H_26(state, unused, out_4191290875491732835);
}
void car_h_27(double *state, double *unused, double *out_4107613004925507694) {
  h_27(state, unused, out_4107613004925507694);
}
void car_H_27(double *state, double *unused, double *out_7152247198545709720) {
  H_27(state, unused, out_7152247198545709720);
}
void car_h_29(double *state, double *unused, double *out_470163476671485344) {
  h_29(state, unused, out_470163476671485344);
}
void car_H_29(double *state, double *unused, double *out_4467252542430892625) {
  H_29(state, unused, out_4467252542430892625);
}
void car_h_28(double *state, double *unused, double *out_5051122857827170129) {
  h_28(state, unused, out_5051122857827170129);
}
void car_H_28(double *state, double *unused, double *out_2503622270865566374) {
  H_28(state, unused, out_2503622270865566374);
}
void car_h_31(double *state, double *unused, double *out_1346021015765680898) {
  h_31(state, unused, out_1346021015765680898);
}
void car_H_31(double *state, double *unused, double *out_4817498977725084311) {
  H_31(state, unused, out_4817498977725084311);
}
void car_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
void car_set_mass(double x) {
  set_mass(x);
}
void car_set_rotational_inertia(double x) {
  set_rotational_inertia(x);
}
void car_set_center_to_front(double x) {
  set_center_to_front(x);
}
void car_set_center_to_rear(double x) {
  set_center_to_rear(x);
}
void car_set_stiffness_front(double x) {
  set_stiffness_front(x);
}
void car_set_stiffness_rear(double x) {
  set_stiffness_rear(x);
}
}

const EKF car = {
  .name = "car",
  .kinds = { 25, 24, 30, 26, 27, 29, 28, 31 },
  .feature_kinds = {  },
  .f_fun = car_f_fun,
  .F_fun = car_F_fun,
  .err_fun = car_err_fun,
  .inv_err_fun = car_inv_err_fun,
  .H_mod_fun = car_H_mod_fun,
  .predict = car_predict,
  .hs = {
    { 25, car_h_25 },
    { 24, car_h_24 },
    { 30, car_h_30 },
    { 26, car_h_26 },
    { 27, car_h_27 },
    { 29, car_h_29 },
    { 28, car_h_28 },
    { 31, car_h_31 },
  },
  .Hs = {
    { 25, car_H_25 },
    { 24, car_H_24 },
    { 30, car_H_30 },
    { 26, car_H_26 },
    { 27, car_H_27 },
    { 29, car_H_29 },
    { 28, car_H_28 },
    { 31, car_H_31 },
  },
  .updates = {
    { 25, car_update_25 },
    { 24, car_update_24 },
    { 30, car_update_30 },
    { 26, car_update_26 },
    { 27, car_update_27 },
    { 29, car_update_29 },
    { 28, car_update_28 },
    { 31, car_update_31 },
  },
  .Hes = {
  },
  .sets = {
    { "mass", car_set_mass },
    { "rotational_inertia", car_set_rotational_inertia },
    { "center_to_front", car_set_center_to_front },
    { "center_to_rear", car_set_center_to_rear },
    { "stiffness_front", car_set_stiffness_front },
    { "stiffness_rear", car_set_stiffness_rear },
  },
  .extra_routines = {
  },
};

ekf_lib_init(car)
