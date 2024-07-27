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
void car_err_fun(double *nom_x, double *delta_x, double *out_1823493661961729959);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7001705699576052991);
void car_H_mod_fun(double *state, double *out_4716016119777539041);
void car_f_fun(double *state, double dt, double *out_8418266052988918400);
void car_F_fun(double *state, double dt, double *out_6406240497487519515);
void car_h_25(double *state, double *unused, double *out_9109286272586353339);
void car_H_25(double *state, double *unused, double *out_449787556617676611);
void car_h_24(double *state, double *unused, double *out_789680335081929477);
void car_H_24(double *state, double *unused, double *out_2622437155623176177);
void car_h_30(double *state, double *unused, double *out_3170343761152063974);
void car_H_30(double *state, double *unused, double *out_4977483886745284809);
void car_h_26(double *state, double *unused, double *out_1831329506508781671);
void car_H_26(double *state, double *unused, double *out_4191290875491732835);
void car_h_27(double *state, double *unused, double *out_4107613004925507694);
void car_H_27(double *state, double *unused, double *out_7152247198545709720);
void car_h_29(double *state, double *unused, double *out_470163476671485344);
void car_H_29(double *state, double *unused, double *out_4467252542430892625);
void car_h_28(double *state, double *unused, double *out_5051122857827170129);
void car_H_28(double *state, double *unused, double *out_2503622270865566374);
void car_h_31(double *state, double *unused, double *out_1346021015765680898);
void car_H_31(double *state, double *unused, double *out_4817498977725084311);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}