#pragma once

#include "ColoredShape.h"

namespace myapp {

class BlueRectangle : public ColoredShape {
private:
  double width;
  double height;

public:
  BlueRectangle(double width, double height);
  void draw() override;
};

}
