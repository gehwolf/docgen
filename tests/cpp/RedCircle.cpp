#include "RedCircle.h"
#include <iostream>

namespace myapp {

RedCircle::RedCircle(double radius) : ColoredShape("Red"), radius(radius) {}

void RedCircle::draw() {
  printColor();
  std::cout << "Drawing a red circle with radius " << radius << std::endl;
}

} // namespace myapp
