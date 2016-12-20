from CronDiscreteEventSimulator import CronSimulator
from random import randint
import csv


def log_data(env):
    env.log.append((env.time, env.rubbish_level))


def empty_rubbish(env):
    env.rubbish_level = 0


def take_out_trash(env):
    env.rubbish_level += randint(0, 10)

s = CronSimulator((2016, 12, 1, 0, 0, 0, 'Australia/Sydney'),
                  (2017, 5, 31, 23, 59, 59, 'America/New_York'),
                  'Australia/Brisbane',
                  rubbish_level=0,
                  log=[])

s.cron_schedule(("*/30 * * * *", "Australia/Brisbane"),
                None,
                None,
                2,
                log_data)

s.cron_schedule("0 8 * * 1",
                None,
                None,
                1,
                empty_rubbish)

s.cron_schedule("0 20 * * *",
                (2017, 1, 1, 0, 0, 0),
                (2017, 4, 30, 23, 59, 59),
                1,
                take_out_trash)

s.run()

with open('rubbish_log.csv', 'w', newline='') as csvfile:
    log_writer = csv.writer(csvfile, delimiter=',')
    for entry in s.log:
        log_writer.writerow(entry)
