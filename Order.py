#! /usr/bin/python

import csv
import sqlite3
import datetime

import simpy
from simpy.util import start_delayed


def init_order_table(db):
    cur = db.cursor()
    cur.execute('''CREATE TABLE ORDER_SCHEDULE (
        ORDER_ID INTEGER PRIMARY KEY,
        ORDER_TIME INTEGER,
        DISPLAY_TIME INTEGER,
        PRODUCT_EXPIRY INTEGER)''')
    db.commit()


# Verify that the product expiry time is after the delivery time and
# verify that the delivery time is after the order time.  Once complete,
# add the order to the database.
# ts indicates time stamp in seconds

def insert_order(order_ts, display_ts, expiry_ts, db):
    if not (0 <= order_ts <= display_ts <= expiry_ts):
        raise Exception("Order dates are not in the correct sequence")

    cur = db.cursor()
    cur.execute("INSERT INTO ORDER_SCHEDULE\
                VALUES(null, ?, ?, ?)",
                (order_ts, display_ts, expiry_ts))
    db.commit()


# Calculate how many seconds are in an
# interval specified in days, hours and minutes

def interval_seconds(interval_days, interval_hours, interval_minutes):
    seconds = datetime.timedelta(days=interval_days, hours=interval_hours,
                                 minutes=interval_minutes)
    return seconds.total_seconds()


def print_order_table(db):
    cur = db.cursor()
    cur.execute("SELECT * FROM ORDER_SCHEDULE")
    for record in cur.fetchall():
        print (record)


def timeToSeconds(weeks, days, hours, minutes):
    values = [weeks, days, hours, minutes]

    # check inputs are numbers
    for value in values:
        try:
            float(value)
        except ValueError:
            print("Non number passed to timeToSeconds")
            raise

    # check inputs are integers (whole numbers)
    for value in values:
        if not float(value).is_integer():
            raise ValueError("Number is not an integer")

    # check inputs are in valid ranges
    if not (0 <= weeks):
        raise ValueError("Invalid week value")
    if not (0 <= days <= 6):
        raise ValueError("Invalid day value")
    if not (0 <= hours <= 23):
        raise ValueError("Invalid hour value")
    if not (0 <= minutes <= 59):
        raise ValueError("Invalid minute value")

    return datetime.timedelta(weeks=weeks,
                              days=days,
                              hours=hours,
                              minutes=minutes).total_seconds()


def generate_recurring_weekly_order(order,
                                    display,
                                    expiry,
                                    recurrencePeriod,
                                    numberOfOrders,
                                    db):
    try:
        for orderNumber in range(0, numberOfOrders):
            offset = recurrencePeriod * orderNumber
            insert_order(order + offset,
                         display + offset,
                         expiry + offset,
                         db)
    except TypeError:
        print("Invalid parameters to generate order")
        raise


def placeOrder(env, db, stock):
    print("tesdt")
    print(env.now)
    yield env.timeout(1)


database = sqlite3.connect(':memory:')
init_order_table(database)
StockOnhand  = 0 


generate_recurring_weekly_order(timeToSeconds(0,  0, 20,  0),
                                timeToSeconds(0,  3, 10,  0),
                                timeToSeconds(1,  3,  0,  0),
                                timeToSeconds(1,  0,  0,  0),
                                20,
                                database)

generate_recurring_weekly_order(timeToSeconds(0,  1, 20,  0),
                                timeToSeconds(0,  4, 10,  0),
                                timeToSeconds(1,  4,  0,  0),
                                timeToSeconds(1,  0,  0,  0),
                                20,
                                database)

print_order_table(database)


env = simpy.Environment()

start_delayed(env, placeOrder(env, database, 10), 10)
start_delayed(env, placeOrder(env, database, 10), 100)


env.run(until=200)
