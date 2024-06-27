#pragma once

#include "selfdrive/ui/qt/onroad/alerts.h"
#include "selfdrive/ui/qt/onroad/annotated_camera.h"

#ifdef DP
#include "dp_priv/selfdrive/ui/qt/onroad/onroad_home.h"
#endif

class OnroadWindow : public QWidget {
  Q_OBJECT

public:
  OnroadWindow(QWidget* parent = 0);

private:
  void paintEvent(QPaintEvent *event);
  OnroadAlerts *alerts;
  AnnotatedCameraWidget *nvg;
  QColor bg = bg_colors[STATUS_DISENGAGED];
  QHBoxLayout* split;

  // dp
  bool dp_ui_map_full = false;
  bool dp_nav_free_map = false;
  #ifdef DP
  BorderIndicator *border_indicator;
  #endif

private slots:
  void offroadTransition(bool offroad);
  void updateState(const UIState &s);
};
