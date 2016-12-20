from DiscreteEventSimulator import Simulator
from datetime import datetime
from croniter import croniter
import pytz


class CronSimulator(Simulator):

    def __init__(self, start_time, end_time, default_location, **kwargs):
        self.default_location = default_location
        start_timestamp = self.localized_timestamp(*start_time)
        end_timestamp = self.localized_timestamp(*end_time)

        Simulator.__init__(self,
                           start_timestamp,
                           end_timestamp,
                           **kwargs)

    def localized_timestamp(self, year, month, day, hour, minute,
                            second, tz=None):
        tz = tz or self.default_location

        zone = pytz.timezone(tz)
        time = datetime(year, month, day, hour, minute, second)

        timestamp = zone.localize(time).timestamp()

        return timestamp

    def timestamp_to_datetime(self, timestamp, tz=None):
        tz = tz or self.default_location

        # Convert timestamp to an aware datetime with a UTC time zone
        utc_zone = pytz.timezone("UTC")
        utc_time = utc_zone.localize(datetime.utcfromtimestamp(timestamp))

        # Convert UTC datetime to a specific timezone
        zone = pytz.timezone(tz)
        time = zone.normalize(utc_time.astimezone(zone))

        return time

    def localize_cron_string(self, cron_instruction):
        if isinstance(cron_instruction, str):
            return_value = (cron_instruction, self.default_location)
        else:
            return_value = cron_instruction
        return return_value

    def schedule(self, time, priority, callback, *args, **kwargs):
        timestamp = self.localized_timestamp(*time)

        Simulator.schedule(self,
                           timestamp,
                           priority,
                           callback,
                           *args,
                           **kwargs)

    def cron_schedule(self, cron_instruction, start, end, priority, callback, *args, **kwargs):
        if not start:
            cron_start = self.time
        else:
            cron_start = self.localized_timestamp(*start)

        if not end:
            cron_end = self.end_time
        else:
            cron_end = self.localized_timestamp(*end)

        local_cron_instruction = self.localize_cron_string(cron_instruction)
        start_datetime = self.timestamp_to_datetime(cron_start, local_cron_instruction[1])
        cron_iterator = croniter(local_cron_instruction[0], start_datetime)
        zone = pytz.timezone(local_cron_instruction[1])

        while True:
            next_event = cron_iterator.get_next(datetime)
            next_event = zone.normalize(next_event)
            event_timestamp = self.localized_timestamp(next_event.year,
                                                       next_event.month,
                                                       next_event.day,
                                                       next_event.hour,
                                                       next_event.minute,
                                                       next_event.second,
                                                       local_cron_instruction[1])
            Simulator.schedule(self,
                               event_timestamp,
                               priority,
                               callback,
                               *args,
                               **kwargs)

            if event_timestamp > cron_end:
                break