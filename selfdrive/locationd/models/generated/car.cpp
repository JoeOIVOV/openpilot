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
void err_fun(double *nom_x, double *delta_x, double *out_4405245383551283102) {
   out_4405245383551283102[0] = delta_x[0] + nom_x[0];
   out_4405245383551283102[1] = delta_x[1] + nom_x[1];
   out_4405245383551283102[2] = delta_x[2] + nom_x[2];
   out_4405245383551283102[3] = delta_x[3] + nom_x[3];
   out_4405245383551283102[4] = delta_x[4] + nom_x[4];
   out_4405245383551283102[5] = delta_x[5] + nom_x[5];
   out_4405245383551283102[6] = delta_x[6] + nom_x[6];
   out_4405245383551283102[7] = delta_x[7] + nom_x[7];
   out_4405245383551283102[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6814225357492049644) {
   out_6814225357492049644[0] = -nom_x[0] + true_x[0];
   out_6814225357492049644[1] = -nom_x[1] + true_x[1];
   out_6814225357492049644[2] = -nom_x[2] + true_x[2];
   out_6814225357492049644[3] = -nom_x[3] + true_x[3];
   out_6814225357492049644[4] = -nom_x[4] + true_x[4];
   out_6814225357492049644[5] = -nom_x[5] + true_x[5];
   out_6814225357492049644[6] = -nom_x[6] + true_x[6];
   out_6814225357492049644[7] = -nom_x[7] + true_x[7];
   out_6814225357492049644[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_8873206987470723373) {
   out_8873206987470723373[0] = 1.0;
   out_8873206987470723373[1] = 0;
   out_8873206987470723373[2] = 0;
   out_8873206987470723373[3] = 0;
   out_8873206987470723373[4] = 0;
   out_8873206987470723373[5] = 0;
   out_8873206987470723373[6] = 0;
   out_8873206987470723373[7] = 0;
   out_8873206987470723373[8] = 0;
   out_8873206987470723373[9] = 0;
   out_8873206987470723373[10] = 1.0;
   out_8873206987470723373[11] = 0;
   out_8873206987470723373[12] = 0;
   out_8873206987470723373[13] = 0;
   out_8873206987470723373[14] = 0;
   out_8873206987470723373[15] = 0;
   out_8873206987470723373[16] = 0;
   out_8873206987470723373[17] = 0;
   out_8873206987470723373[18] = 0;
   out_8873206987470723373[19] = 0;
   out_8873206987470723373[20] = 1.0;
   out_8873206987470723373[21] = 0;
   out_8873206987470723373[22] = 0;
   out_8873206987470723373[23] = 0;
   out_8873206987470723373[24] = 0;
   out_8873206987470723373[25] = 0;
   out_8873206987470723373[26] = 0;
   out_8873206987470723373[27] = 0;
   out_8873206987470723373[28] = 0;
   out_8873206987470723373[29] = 0;
   out_8873206987470723373[30] = 1.0;
   out_8873206987470723373[31] = 0;
   out_8873206987470723373[32] = 0;
   out_8873206987470723373[33] = 0;
   out_8873206987470723373[34] = 0;
   out_8873206987470723373[35] = 0;
   out_8873206987470723373[36] = 0;
   out_8873206987470723373[37] = 0;
   out_8873206987470723373[38] = 0;
   out_8873206987470723373[39] = 0;
   out_8873206987470723373[40] = 1.0;
   out_8873206987470723373[41] = 0;
   out_8873206987470723373[42] = 0;
   out_8873206987470723373[43] = 0;
   out_8873206987470723373[44] = 0;
   out_8873206987470723373[45] = 0;
   out_8873206987470723373[46] = 0;
   out_8873206987470723373[47] = 0;
   out_8873206987470723373[48] = 0;
   out_8873206987470723373[49] = 0;
   out_8873206987470723373[50] = 1.0;
   out_8873206987470723373[51] = 0;
   out_8873206987470723373[52] = 0;
   out_8873206987470723373[53] = 0;
   out_8873206987470723373[54] = 0;
   out_8873206987470723373[55] = 0;
   out_8873206987470723373[56] = 0;
   out_8873206987470723373[57] = 0;
   out_8873206987470723373[58] = 0;
   out_8873206987470723373[59] = 0;
   out_8873206987470723373[60] = 1.0;
   out_8873206987470723373[61] = 0;
   out_8873206987470723373[62] = 0;
   out_8873206987470723373[63] = 0;
   out_8873206987470723373[64] = 0;
   out_8873206987470723373[65] = 0;
   out_8873206987470723373[66] = 0;
   out_8873206987470723373[67] = 0;
   out_8873206987470723373[68] = 0;
   out_8873206987470723373[69] = 0;
   out_8873206987470723373[70] = 1.0;
   out_8873206987470723373[71] = 0;
   out_8873206987470723373[72] = 0;
   out_8873206987470723373[73] = 0;
   out_8873206987470723373[74] = 0;
   out_8873206987470723373[75] = 0;
   out_8873206987470723373[76] = 0;
   out_8873206987470723373[77] = 0;
   out_8873206987470723373[78] = 0;
   out_8873206987470723373[79] = 0;
   out_8873206987470723373[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3688990143768374912) {
   out_3688990143768374912[0] = state[0];
   out_3688990143768374912[1] = state[1];
   out_3688990143768374912[2] = state[2];
   out_3688990143768374912[3] = state[3];
   out_3688990143768374912[4] = state[4];
   out_3688990143768374912[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8000000000000007*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3688990143768374912[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3688990143768374912[7] = state[7];
   out_3688990143768374912[8] = state[8];
}
void F_fun(double *state, double dt, double *out_6095431430690537089) {
   out_6095431430690537089[0] = 1;
   out_6095431430690537089[1] = 0;
   out_6095431430690537089[2] = 0;
   out_6095431430690537089[3] = 0;
   out_6095431430690537089[4] = 0;
   out_6095431430690537089[5] = 0;
   out_6095431430690537089[6] = 0;
   out_6095431430690537089[7] = 0;
   out_6095431430690537089[8] = 0;
   out_6095431430690537089[9] = 0;
   out_6095431430690537089[10] = 1;
   out_6095431430690537089[11] = 0;
   out_6095431430690537089[12] = 0;
   out_6095431430690537089[13] = 0;
   out_6095431430690537089[14] = 0;
   out_6095431430690537089[15] = 0;
   out_6095431430690537089[16] = 0;
   out_6095431430690537089[17] = 0;
   out_6095431430690537089[18] = 0;
   out_6095431430690537089[19] = 0;
   out_6095431430690537089[20] = 1;
   out_6095431430690537089[21] = 0;
   out_6095431430690537089[22] = 0;
   out_6095431430690537089[23] = 0;
   out_6095431430690537089[24] = 0;
   out_6095431430690537089[25] = 0;
   out_6095431430690537089[26] = 0;
   out_6095431430690537089[27] = 0;
   out_6095431430690537089[28] = 0;
   out_6095431430690537089[29] = 0;
   out_6095431430690537089[30] = 1;
   out_6095431430690537089[31] = 0;
   out_6095431430690537089[32] = 0;
   out_6095431430690537089[33] = 0;
   out_6095431430690537089[34] = 0;
   out_6095431430690537089[35] = 0;
   out_6095431430690537089[36] = 0;
   out_6095431430690537089[37] = 0;
   out_6095431430690537089[38] = 0;
   out_6095431430690537089[39] = 0;
   out_6095431430690537089[40] = 1;
   out_6095431430690537089[41] = 0;
   out_6095431430690537089[42] = 0;
   out_6095431430690537089[43] = 0;
   out_6095431430690537089[44] = 0;
   out_6095431430690537089[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_6095431430690537089[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_6095431430690537089[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6095431430690537089[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_6095431430690537089[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_6095431430690537089[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_6095431430690537089[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_6095431430690537089[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_6095431430690537089[53] = -9.8000000000000007*dt;
   out_6095431430690537089[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_6095431430690537089[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_6095431430690537089[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6095431430690537089[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6095431430690537089[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_6095431430690537089[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_6095431430690537089[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_6095431430690537089[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_6095431430690537089[62] = 0;
   out_6095431430690537089[63] = 0;
   out_6095431430690537089[64] = 0;
   out_6095431430690537089[65] = 0;
   out_6095431430690537089[66] = 0;
   out_6095431430690537089[67] = 0;
   out_6095431430690537089[68] = 0;
   out_6095431430690537089[69] = 0;
   out_6095431430690537089[70] = 1;
   out_6095431430690537089[71] = 0;
   out_6095431430690537089[72] = 0;
   out_6095431430690537089[73] = 0;
   out_6095431430690537089[74] = 0;
   out_6095431430690537089[75] = 0;
   out_6095431430690537089[76] = 0;
   out_6095431430690537089[77] = 0;
   out_6095431430690537089[78] = 0;
   out_6095431430690537089[79] = 0;
   out_6095431430690537089[80] = 1;
}
void h_25(double *state, double *unused, double *out_2085281169667296275) {
   out_2085281169667296275[0] = state[6];
}
void H_25(double *state, double *unused, double *out_1623550404401847017) {
   out_1623550404401847017[0] = 0;
   out_1623550404401847017[1] = 0;
   out_1623550404401847017[2] = 0;
   out_1623550404401847017[3] = 0;
   out_1623550404401847017[4] = 0;
   out_1623550404401847017[5] = 0;
   out_1623550404401847017[6] = 1;
   out_1623550404401847017[7] = 0;
   out_1623550404401847017[8] = 0;
}
void h_24(double *state, double *unused, double *out_953773106991605179) {
   out_953773106991605179[0] = state[4];
   out_953773106991605179[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4462623414451625302) {
   out_4462623414451625302[0] = 0;
   out_4462623414451625302[1] = 0;
   out_4462623414451625302[2] = 0;
   out_4462623414451625302[3] = 0;
   out_4462623414451625302[4] = 1;
   out_4462623414451625302[5] = 0;
   out_4462623414451625302[6] = 0;
   out_4462623414451625302[7] = 0;
   out_4462623414451625302[8] = 0;
   out_4462623414451625302[9] = 0;
   out_4462623414451625302[10] = 0;
   out_4462623414451625302[11] = 0;
   out_4462623414451625302[12] = 0;
   out_4462623414451625302[13] = 0;
   out_4462623414451625302[14] = 1;
   out_4462623414451625302[15] = 0;
   out_4462623414451625302[16] = 0;
   out_4462623414451625302[17] = 0;
}
void h_30(double *state, double *unused, double *out_4081832870303838028) {
   out_4081832870303838028[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5293139937089769738) {
   out_5293139937089769738[0] = 0;
   out_5293139937089769738[1] = 0;
   out_5293139937089769738[2] = 0;
   out_5293139937089769738[3] = 0;
   out_5293139937089769738[4] = 1;
   out_5293139937089769738[5] = 0;
   out_5293139937089769738[6] = 0;
   out_5293139937089769738[7] = 0;
   out_5293139937089769738[8] = 0;
}
void h_26(double *state, double *unused, double *out_4050923066687483124) {
   out_4050923066687483124[0] = state[7];
}
void H_26(double *state, double *unused, double *out_966696340291535113) {
   out_966696340291535113[0] = 0;
   out_966696340291535113[1] = 0;
   out_966696340291535113[2] = 0;
   out_966696340291535113[3] = 0;
   out_966696340291535113[4] = 0;
   out_966696340291535113[5] = 0;
   out_966696340291535113[6] = 0;
   out_966696340291535113[7] = 1;
   out_966696340291535113[8] = 0;
}
void h_27(double *state, double *unused, double *out_7086954437328141920) {
   out_7086954437328141920[0] = state[3];
}
void H_27(double *state, double *unused, double *out_3927652663345511998) {
   out_3927652663345511998[0] = 0;
   out_3927652663345511998[1] = 0;
   out_3927652663345511998[2] = 0;
   out_3927652663345511998[3] = 1;
   out_3927652663345511998[4] = 0;
   out_3927652663345511998[5] = 0;
   out_3927652663345511998[6] = 0;
   out_3927652663345511998[7] = 0;
   out_3927652663345511998[8] = 0;
}
void h_29(double *state, double *unused, double *out_6929767768977012775) {
   out_6929767768977012775[0] = state[1];
}
void H_29(double *state, double *unused, double *out_1242658007230694903) {
   out_1242658007230694903[0] = 0;
   out_1242658007230694903[1] = 1;
   out_1242658007230694903[2] = 0;
   out_1242658007230694903[3] = 0;
   out_1242658007230694903[4] = 0;
   out_1242658007230694903[5] = 0;
   out_1242658007230694903[6] = 0;
   out_1242658007230694903[7] = 0;
   out_1242658007230694903[8] = 0;
}
void h_28(double *state, double *unused, double *out_6358116368720564051) {
   out_6358116368720564051[0] = state[0];
}
void H_28(double *state, double *unused, double *out_720972264334631348) {
   out_720972264334631348[0] = 1;
   out_720972264334631348[1] = 0;
   out_720972264334631348[2] = 0;
   out_720972264334631348[3] = 0;
   out_720972264334631348[4] = 0;
   out_720972264334631348[5] = 0;
   out_720972264334631348[6] = 0;
   out_720972264334631348[7] = 0;
   out_720972264334631348[8] = 0;
}
void h_31(double *state, double *unused, double *out_1552168358586726075) {
   out_1552168358586726075[0] = state[8];
}
void H_31(double *state, double *unused, double *out_1592904442524886589) {
   out_1592904442524886589[0] = 0;
   out_1592904442524886589[1] = 0;
   out_1592904442524886589[2] = 0;
   out_1592904442524886589[3] = 0;
   out_1592904442524886589[4] = 0;
   out_1592904442524886589[5] = 0;
   out_1592904442524886589[6] = 0;
   out_1592904442524886589[7] = 0;
   out_1592904442524886589[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4405245383551283102) {
  err_fun(nom_x, delta_x, out_4405245383551283102);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6814225357492049644) {
  inv_err_fun(nom_x, true_x, out_6814225357492049644);
}
void car_H_mod_fun(double *state, double *out_8873206987470723373) {
  H_mod_fun(state, out_8873206987470723373);
}
void car_f_fun(double *state, double dt, double *out_3688990143768374912) {
  f_fun(state,  dt, out_3688990143768374912);
}
void car_F_fun(double *state, double dt, double *out_6095431430690537089) {
  F_fun(state,  dt, out_6095431430690537089);
}
void car_h_25(double *state, double *unused, double *out_2085281169667296275) {
  h_25(state, unused, out_2085281169667296275);
}
void car_H_25(double *state, double *unused, double *out_1623550404401847017) {
  H_25(state, unused, out_1623550404401847017);
}
void car_h_24(double *state, double *unused, double *out_953773106991605179) {
  h_24(state, unused, out_953773106991605179);
}
void car_H_24(double *state, double *unused, double *out_4462623414451625302) {
  H_24(state, unused, out_4462623414451625302);
}
void car_h_30(double *state, double *unused, double *out_4081832870303838028) {
  h_30(state, unused, out_4081832870303838028);
}
void car_H_30(double *state, double *unused, double *out_5293139937089769738) {
  H_30(state, unused, out_5293139937089769738);
}
void car_h_26(double *state, double *unused, double *out_4050923066687483124) {
  h_26(state, unused, out_4050923066687483124);
}
void car_H_26(double *state, double *unused, double *out_966696340291535113) {
  H_26(state, unused, out_966696340291535113);
}
void car_h_27(double *state, double *unused, double *out_7086954437328141920) {
  h_27(state, unused, out_7086954437328141920);
}
void car_H_27(double *state, double *unused, double *out_3927652663345511998) {
  H_27(state, unused, out_3927652663345511998);
}
void car_h_29(double *state, double *unused, double *out_6929767768977012775) {
  h_29(state, unused, out_6929767768977012775);
}
void car_H_29(double *state, double *unused, double *out_1242658007230694903) {
  H_29(state, unused, out_1242658007230694903);
}
void car_h_28(double *state, double *unused, double *out_6358116368720564051) {
  h_28(state, unused, out_6358116368720564051);
}
void car_H_28(double *state, double *unused, double *out_720972264334631348) {
  H_28(state, unused, out_720972264334631348);
}
void car_h_31(double *state, double *unused, double *out_1552168358586726075) {
  h_31(state, unused, out_1552168358586726075);
}
void car_H_31(double *state, double *unused, double *out_1592904442524886589) {
  H_31(state, unused, out_1592904442524886589);
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
