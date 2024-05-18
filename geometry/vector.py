import math


class Vector:
    def __init__(self, x=0.0, y=0.0) -> None:
        self.x, self.y = float(x), float(y)

    def __repr__(self):
        return "Vector({}, {})".format(self.x, self.y)

    def __str__(self):  # print
        return "({}, {})".format(self.x, self.y)

    def __add__(self, other: "Vector"):  # +
        return Vector(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: "Vector"):  # +=
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: "Vector"):  # -
        return Vector(self.x - other.x, self.y - other.y)

    def __isub__(self, other: "Vector"):  # -=
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, scalar: float) -> "Vector":  # *
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector":  # *
        return self * scalar

    def __imul__(self, scalar: float):  # *=
        self.x *= scalar
        self.y *= scalar
        return self

    def __truediv__(self, scalar: float) -> "Vector":  # /
        assert scalar != 0
        return Vector(self.x / scalar, self.y / scalar)

    def __rtruediv__(self, scalar: float) -> "Vector":  # /
        return self / scalar

    def __itruediv__(self, scalar):  # /=
        self.x /= scalar
        self.y /= scalar
        return self

    def __neg__(self) -> "Vector":  # -
        return Vector(-self.x, -self.y)

    def __abs__(self) -> float:
        return math.hypot(self.x, self.y)

    def sign(self) -> "Vector":
        sign = lambda a: 0 if (a == 0) else (1 if (a > 0) else -1)
        return Vector(sign(self.x), sign(self.y))

    def get_normalization(self) -> "Vector":
        if abs(self) > 0.0:
            return Vector(self.x, self.y) / abs(self)
        return Vector()

    def rotate(self, angle: float):
        a = self.x
        b = self.y
        self.x = a * math.cos(angle) - b * math.sin(angle)
        self.y = a * math.sin(angle) + b * math.cos(angle)
        return self

    def angle(self):
        """[0;2pi)"""
        if abs(self) == 0:
            return 0.0
        fi1 = math.acos(self.x / abs(self))
        fi2 = math.asin(self.y / abs(self))
        answer = 0
        if fi1 < math.pi / 2:
            answer = fi2
        elif fi2 > 0:
            answer = fi1
        else:
            answer = -fi1
        if answer < 0:
            answer += 2 * math.pi
        return answer

    def pair(self):
        return [self.x, self.y]
