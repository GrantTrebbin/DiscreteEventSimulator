import numpy


class function(object):

    def __init__(self, data):
        self.x = data[:, 0]
        self.y = data[:, 1]

        x_difference = self.x[1:] - self.x[:-1]
        y_difference = self.y[1:] - self.y[:-1]

        # Make sure all the elements of x_difference are greater than zero
        if not (numpy.all(x_difference > 0)):
            raise ValueError("The x data supplied must be unique and in " +
                             "increasing order")

        # Make sure all the elements of y_difference are greater than or equal to zero
        if not (numpy.all(y_difference >= 0)):
            raise ValueError("The y data supplied must be in " +
                             "increasing order.  Uniqueness is note required")

    def interpolate(self, target, **kwargs):
        invert = kwargs.get('invert', False)

        #  if the invert setting is activated, search the dependent variable for target
        if (invert):
            #  because there can be duplicates in the dependant variable,
            #  make sure the first one found is returned.
            locations = (self.y == target)
            if numpy.any(locations):
                index = numpy.where(locations)
                returnVal = self.x[index][0]
            else:
                returnVal = numpy.interp(target, self.y, self.x)
        else:
            returnVal = numpy.interp(target, self.x, self.y)

        return returnVal


if __name__ == '__main__':

    data = numpy.array([[0, 0], [10, 20], [20, 50], [30, 50]])
    salesData = numpy.array([[(0 * 24 + 0) * 3600, 0],
                             [(0 * 24 + 8) * 3600, 0],
                             [(0 * 24 + 21) * 3600, 3000],
                             [(1 * 24 + 8) * 3600, 3000],
                             [(1 * 24 + 21) * 3600, 6000],
                             [(2 * 24 + 8) * 3600, 6000],
                             [(2 * 24 + 21) * 3600, 9000],
                             [(3 * 24 + 8) * 3600, 9000],
                             [(3 * 24 + 21) * 3600, 12000],
                             [(4 * 24 + 8) * 3600, 12000],
                             [(4 * 24 + 21) * 3600, 15000],
                             [(5 * 24 + 8) * 3600, 15000],
                             [(5 * 24 + 17) * 3600, 22500],
                             [(6 * 24 + 9) * 3600, 22500],
                             [(6 * 24 + 18) * 3600, 30000],
                             [(6 * 24 + 24) * 3600, 30000],
                             ])

    f = function(salesData)

    interpolateTest = f.interpolate(30000)
    print (interpolateTest)

    invertedTest = f.interpolate(22500, invert=True)
    print (invertedTest)
