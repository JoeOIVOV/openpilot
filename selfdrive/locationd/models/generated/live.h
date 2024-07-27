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
void live_H(double *in_vec, double *out_3969893128517011236);
void live_err_fun(double *nom_x, double *delta_x, double *out_1006419718300617568);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8817840190981899676);
void live_H_mod_fun(double *state, double *out_6477212205675135460);
void live_f_fun(double *state, double dt, double *out_6834650672371603337);
void live_F_fun(double *state, double dt, double *out_5478108233600911700);
void live_h_4(double *state, double *unused, double *out_7729241800317890539);
void live_H_4(double *state, double *unused, double *out_5199473691953303502);
void live_h_9(double *state, double *unused, double *out_5651445951659387245);
void live_H_9(double *state, double *unused, double *out_4958284045323712857);
void live_h_10(double *state, double *unused, double *out_6193925307380695013);
void live_H_10(double *state, double *unused, double *out_9161549963754530533);
void live_h_12(double *state, double *unused, double *out_8203641853388437577);
void live_H_12(double *state, double *unused, double *out_180017283921341707);
void live_h_35(double *state, double *unused, double *out_4000488817324217692);
void live_H_35(double *state, double *unused, double *out_2565545748403672002);
void live_h_32(double *state, double *unused, double *out_8660119988636660788);
void live_H_32(double *state, double *unused, double *out_3477651144291595728);
void live_h_13(double *state, double *unused, double *out_3567048378260979633);
void live_H_13(double *state, double *unused, double *out_8054277663346687055);
void live_h_14(double *state, double *unused, double *out_5651445951659387245);
void live_H_14(double *state, double *unused, double *out_4958284045323712857);
void live_h_33(double *state, double *unused, double *out_2337059077647592131);
void live_H_33(double *state, double *unused, double *out_1317745370058161478);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}