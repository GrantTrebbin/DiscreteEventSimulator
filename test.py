import DiscreteEventSimulator
import random
import math


def order(simulator,):
    global StockOnHand
    orderAmount = 50 - StockOnHand
    if (orderAmount < 0):
        orderAmount = 0
    cartonsToOrder = math.ceil(orderAmount / 24.0)
    StockOnHand = StockOnHand + 24 * cartonsToOrder
    print (simulator.time, StockOnHand)


def customer(simulator):
    global StockOnHand
    StockOnHand -= 1
    if (StockOnHand < 0):
        StockOnHand = 0
    currentTime = simulator.time
    timeToNextCustomer = int(random.expovariate(0.0004))
    simulator.schedule(currentTime + timeToNextCustomer, customer, simulator)
    print (currentTime, StockOnHand)

StockOnHand = 50
s = DiscreteEventSimulator.Simulator()
e1 = s.schedule(3600 + 0 * 86400, order, s,)
e2 = s.schedule(3600 + 1 * 86400, order, s,)
e3 = s.schedule(3600 + 2 * 86400, order, s,)
e4 = s.schedule(3600 + 3 * 86400, order, s,)
e5 = s.schedule(3600 + 4 * 86400, order, s,)
e6 = s.schedule(3600 + 5 * 86400, order, s,)
e7 = s.schedule(3600 + 6 * 86400, order, s,)

e8 = s.schedule(0, customer, s,)
s.run(604800)
