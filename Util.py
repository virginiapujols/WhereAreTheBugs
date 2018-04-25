class Util:
    @staticmethod
    def normalization(x, max, min):
        return (x - min) / (max - min)