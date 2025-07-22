#pragma once

#include "Shape.h"

namespace myapp {

class Circle : public Shape {
private:
  double radius;

public:
  Circle(double radius);
  void draw() override;
};

} // namespace myapp
