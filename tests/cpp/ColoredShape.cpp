#include "ColoredShape.h"
#include <iostream>

namespace myapp {

ColoredShape::ColoredShape(const std::string& color) : color(color) {}

void ColoredShape::printColor() {
    std::cout << "Color: " << color << std::endl;
}

} // namespace myapp
