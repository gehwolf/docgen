#pragma once

namespace myapp {

class Shape {
public:
  virtual void draw() = 0;
  virtual ~Shape() = default;
};

} // namespace myapp
