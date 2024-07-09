#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_4405245383551283102);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6814225357492049644);
void car_H_mod_fun(double *state, double *out_8873206987470723373);
void car_f_fun(double *state, double dt, double *out_3688990143768374912);
void car_F_fun(double *state, double dt, double *out_6095431430690537089);
void car_h_25(double *state, double *unused, double *out_2085281169667296275);
void car_H_25(double *state, double *unused, double *out_1623550404401847017);
void car_h_24(double *state, double *unused, double *out_953773106991605179);
void car_H_24(double *state, double *unused, double *out_4462623414451625302);
void car_h_30(double *state, double *unused, double *out_4081832870303838028);
void car_H_30(double *state, double *unused, double *out_5293139937089769738);
void car_h_26(double *state, double *unused, double *out_4050923066687483124);
void car_H_26(double *state, double *unused, double *out_966696340291535113);
void car_h_27(double *state, double *unused, double *out_7086954437328141920);
void car_H_27(double *state, double *unused, double *out_3927652663345511998);
void car_h_29(double *state, double *unused, double *out_6929767768977012775);
void car_H_29(double *state, double *unused, double *out_1242658007230694903);
void car_h_28(double *state, double *unused, double *out_6358116368720564051);
void car_H_28(double *state, double *unused, double *out_720972264334631348);
void car_h_31(double *state, double *unused, double *out_1552168358586726075);
void car_H_31(double *state, double *unused, double *out_1592904442524886589);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}