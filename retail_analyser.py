#!/usr/bin/env python
# -*- coding: ascii -*-

"""
retail_analyser.py

This module contains functions to assist in the analysis of retail sales
simulations
"""


__author__ = 'Grant Trebbin'


import numpy


def zero_order_resample(data_set, sample_points):
    """
    zero_order_resample takes an ordered data set representing a sampled
    function and resamples the dependent variable for new values of the
    independent variable

    The original data is supplied as a 2xn array containing ordered values of
    the independent variable with corresponding values of the function.
    samplePoints is an array containing new values of the independent variable.
    The function is resampled at these points.

    The resample procedure is as follows.  If the new indpendendent variable
    has a corresponding value in the data set, use that.  If not, use the
    value of the next lowest value.  If there is no lower value, use the
    lowest value available

    For example, the function represented by the sample points

        (1, 1), (5, 2), (10, 3), (11, 4), (12, 5), (20 , 6)

    can be resampled at the points -10, 1, 2, 10, 30 to give

        (-10, 1), (1, 1), (2, 1), (10, 3), (30, 6)

    """

    independent_variable = data_set[0, :]
    dependent_variable = data_set[1, :]

    # Find indexed location of samplePoints in independent_variable
    insertion_points = numpy.searchsorted(independent_variable,
                                          sample_points,
                                          side='right') - 1

    # For values less than the lowest data point, resample the data at
    # the lowest data point
    insertion_points[insertion_points < 0] = 0

    # Use insertion_points to retrieve values for resampled data
    resampled_data = dependent_variable[insertion_points]

    return (resampled_data)


def folded_monte_carlo(percentiles, data, number_of_folds):
    """
    folded_monte_carlo take a long array of data and and folds it to simulate
    multiple trials.  This data is then sorted.  Rows are then extracted based
    upon the percentile values supplied.  For small number of folds the
    percentiles suffer quantisation error

    For example
        A temperature measurement is taken 4 times a day for 5 days.  The time
        the measurement is taken isn't important, just that they're taken the
        same time each day.  The 0, 75, and 100 percentiles are also required

        percentiles = [0, 80, 100]
        data = [12, 50, 19, 4, 14, 48, 32, 22, 39, 31, 25, 44, 41, 5, 44, 40,
                0, 44, 4, 11]
        number_of_folds = 5

    After folding, the data is arranged as follow
        [[12, 50, 19,  4],
         [14, 48, 32, 22],
         [39, 31, 25, 44],
         [41,  5, 44, 40],
         [ 0, 44,  4, 11]]

    After sorting, the array will look like this
        [[ 0,  5,  4,  4],
         [12, 31, 19, 11],
         [14, 44, 25, 22],
         [39, 48, 32, 40],
         [41, 50, 44, 44]]

    The percentiles are then converted to row numbers
        round([0, 80, 100] * 4 / 100) = round([0, 3.2, 4])
                                      = [0, 3, 4]

    Rows 0, 3, and 4 are then selected to give
        [[ 0,  5,  4,  4],
         [39, 48, 32, 40],
         [41, 50, 44, 44]]

    This means the measurements are less than
        [ 0,  5,  4,  4]   0 percent of the time
        [39, 48, 32, 40]  80 percent of the time
        [41, 50, 44, 44] 100 percent of the time

    """

    # Convert the data from one long array into a rectangular array
    # The reshpaed_data array and the data array must have the same number
    # of elements
    reshaped_data = data.reshape(number_of_folds, -1)

    # Sort the data at each sample instance
    sorted_data = numpy.sort(reshaped_data, axis=0)

    # Conceptually, number of rows makes more sense from this point forward
    number_of_rows = number_of_folds

    # Use the values of the percentiles array to determine what rows of the
    # sorted_data array to select
    records_to_select = (numpy.rint(percentiles * (number_of_rows - 1)
                         / 100)).astype(int)

    # extract percentile data from the sorted_data array
    selected_data = sorted_data[records_to_select, :]

    return (selected_data)


def test():
    """ Run a suite of test functions """

    # Test the zero_order_resample function
    test_data_set = numpy.array([[1, 5, 10, 11, 12, 20], [1, 2, 3, 4, 5, 6]])
    test_sample_points = numpy.array([-10, 1, 2, 10, 30])

    print(zero_order_resample(test_data_set, test_sample_points))

    # Test the folded_monte_carlo function
    percentiles = numpy.array([0, 80, 100])
    data = numpy.array([12, 50, 19, 4, 14, 48, 32, 22, 39, 31, 25, 44, 41, 5, 44, 40,
                        0, 44, 4, 11])
    number_of_folds = 5

    print(folded_monte_carlo(percentiles, data, number_of_folds))


if __name__ == '__main__':
    test()
