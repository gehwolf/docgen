#pragma once

#include "ColoredShape.h"

namespace myapp {

class RedCircle : public ColoredShape {
private:
  double radius;

public:
  RedCircle(double radius);
  void draw() override;
};

} // namespace myapp
