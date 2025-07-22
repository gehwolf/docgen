#include "BlueRectangle.h"
#include <iostream>

namespace myapp {

BlueRectangle::BlueRectangle(double width, double height)
    : ColoredShape("Blue"), width(width), height(height) {}

void BlueRectangle::draw() {
  printColor();
  std::cout << "Drawing a blue rectangle with width " << width << " and height "
            << height << std::endl;
}

} // namespace myapp
