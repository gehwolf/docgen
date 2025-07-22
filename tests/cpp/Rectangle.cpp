#include "Rectangle.h"
#include <iostream>

namespace myapp {

Rectangle::Rectangle(double width, double height)
    : width(width), height(height) {}

void Rectangle::draw() {
  std::cout << "Drawing a rectangle with width " << width << " and height "
            << height << std::endl;
}

} // namespace myapp
