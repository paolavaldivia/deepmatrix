
class Scale:

    def __init__(self, rang=[0, 1], domain=[0, 1]):
        self._range = rang
        self._domain = domain

    def __call__(self, number):
        return (self._range[1] - self._range[0]) * (number - self._domain[0]) / (self._domain[1] - self._domain[0]) \
               + self._range[0]

    def invert(self, number):
        return (self._range[0] - self._range[1]) * (number - self._domain[0]) / (self._domain[1] - self._domain[0]) \
               + self._range[1]

    def domain(self, domain):
        return self.__class__(self._range, domain)

    def get_domain(self):
        return self._domain

    def get_domain_ext(self):
        return self._domain[1] - self._domain[0]

    def get_range_ext(self):
        return self._range[1] - self._range[0]

    def rang(self, rang):
        return self.__class__(rang, self._domain)

    def get_range(self):
        return self._range
