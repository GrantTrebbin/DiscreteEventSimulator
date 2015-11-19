import DiscreteEventSimulator
import random
import math
import sqlite3
import numpy
import matplotlib.pyplot as plt
import retail_analyser as ra

def init_SOH_table(db):
    cur = db.cursor()
    cur.execute('''CREATE TABLE SOH_LOG (
        ADJUSTMENT_ID INTEGER PRIMARY KEY,
        ADJUSTMENT_TIME INTEGER,
        STOCK_ON_HAND INTEGER)''')
    db.commit()


def get_SOH_table(db):
    cur = db.cursor()
    cur.execute("SELECT * FROM SOH_LOG")

    arr = numpy.array(cur.fetchall())
    slicedArr = arr[:, 1:3]
    sortedArr = slicedArr[slicedArr[:, 0].argsort()]
    return sortedArr.T


def get_SOH_at_time(time, database):
    cur = database.cursor()
    cur.execute("SELECT STOCK_ON_HAND \
                 FROM SOH_LOG \
                 WHERE ADJUSTMENT_TIME <= ? \
                 ORDER BY ADJUSTMENT_TIME DESC\
                 LIMIT 1", (time,))
    return cur.fetchall()[0][0]


def log_SOH(time, stockOnHand, database):
    cur = database.cursor()
    cur.execute("INSERT INTO SOH_LOG\
                VALUES(null, ?, ?)",
                (time, stockOnHand))
    database.commit()


def order(simulator, database):
    global StockOnHand
    orderAmount = 50 - StockOnHand
    if (orderAmount < 0):
        orderAmount = 0
    cartonsToOrder = math.ceil(orderAmount / 24.0)
    StockOnHand = StockOnHand + 24 * cartonsToOrder
    log_SOH(simulator.time, StockOnHand, database)


def customer(simulator, database):
    global StockOnHand
    StockOnHand -= 1
    if (StockOnHand < 0):
        StockOnHand = 0
    currentTime = simulator.time
    timeToNextCustomer = int(random.expovariate(0.0004))
    simulator.schedule(currentTime + timeToNextCustomer, customer, simulator, database)
    log_SOH(currentTime, StockOnHand, database)


# Create database
database = sqlite3.connect(':memory:')
init_SOH_table(database)

# Set parameters
StockOnHand = 50
WeeksToSimulate = 100
secondsPerWeek = 7 * 24 * 60 * 60

simulationPeriod = WeeksToSimulate *   secondsPerWeek


# Perform Simulation
s = DiscreteEventSimulator.Simulator()
for orderNumber in range(0, WeeksToSimulate*7):
    s.schedule(3600 + orderNumber * 86400, order, s, database)

s.schedule(0, customer, s, database)

s.run(simulationPeriod)



# Analyse results
simulationResults = get_SOH_table(database)



# Regular times to resample the irregular simulation values
secondsBetweenSamples = 300  # Every 5 minutes
samplesPerWeek = secondsPerWeek/secondsBetweenSamples

periodicSamplePoints = numpy.arange(0, simulationPeriod, secondsBetweenSamples)

# Resample the simulation results at the specified times
regularlySampledSOHValue = ra.zero_order_resample(simulationResults, periodicSamplePoints)

# Create array of percentiles for aggregate statistics
percentiles = numpy.array([0, 10, 50, 90, 100])

# Calculate the SOH for specified percentiles over the period of a week
selecteddata = ra.folded_monte_carlo(percentiles, regularlySampledSOHValue, WeeksToSimulate)


print(selecteddata)

plt.plot(selecteddata.T)
plt.show()
#numpy.savetxt("test.csv", sortedArray, delimiter=",", fmt='%i')
