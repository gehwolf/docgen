#include "Circle.h"
#include <iostream>

namespace myapp {

Circle::Circle(double radius) : radius(radius) {}

void Circle::draw() {
  std::cout << "Drawing a circle with radius " << radius << std::endl;
}

} // namespace myapp
