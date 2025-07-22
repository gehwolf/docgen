#pragma once

#include "Shape.h"
#include <string>

namespace myapp {

class ColoredShape : public Shape {
protected:
  std::string color;

public:
  ColoredShape(const std::string &color);
  virtual void printColor();
};

} // namespace myapp
