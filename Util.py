class Util:
    @staticmethod
    def normalization(x, max, min):
        if max < min:
            raise ArithmeticError("Verify max and min of the normalize function")
        if max == min:
            raise ZeroDivisionError("Max and min are equal")
        if max <= 0:
            raise ArithmeticError("Not common for max to be zero or negative ")
        if min < 0:
            raise ArithmeticError("Min is negative")
        return (x - min) / (max - min)



