#pragma once

#include "Shape.h"

namespace myapp {

class Rectangle : public Shape {
private:
  double width;
  double height;

public:
  Rectangle(double width, double height);
  void draw() override;
};

} // namespace myapp
