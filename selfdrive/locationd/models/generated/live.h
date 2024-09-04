#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_8605358087906380768);
void live_err_fun(double *nom_x, double *delta_x, double *out_7536170868467214378);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_2595613781234485125);
void live_H_mod_fun(double *state, double *out_8460251824602801486);
void live_f_fun(double *state, double dt, double *out_6356829281411656445);
void live_F_fun(double *state, double dt, double *out_8639720302372924628);
void live_h_4(double *state, double *unused, double *out_5024870629752735468);
void live_H_4(double *state, double *unused, double *out_1752310950812596014);
void live_h_9(double *state, double *unused, double *out_2675503251996688187);
void live_H_9(double *state, double *unused, double *out_1511121304183005369);
void live_h_10(double *state, double *unused, double *out_7370746392053236487);
void live_H_10(double *state, double *unused, double *out_7385579306469280005);
void live_h_12(double *state, double *unused, double *out_3987271481309322321);
void live_H_12(double *state, double *unused, double *out_1131211925765002347);
void live_h_35(double *state, double *unused, double *out_387267383515705374);
void live_H_35(double *state, double *unused, double *out_1614351106560011362);
void live_h_32(double *state, double *unused, double *out_8661748451588242164);
void live_H_32(double *state, double *unused, double *out_7415655478767623920);
void live_h_13(double *state, double *unused, double *out_4888723774468744577);
void live_H_13(double *state, double *unused, double *out_1203933476290211087);
void live_h_14(double *state, double *unused, double *out_2675503251996688187);
void live_H_14(double *state, double *unused, double *out_1511121304183005369);
void live_h_33(double *state, double *unused, double *out_8061952833475180318);
void live_H_33(double *state, double *unused, double *out_4764908111198868966);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}