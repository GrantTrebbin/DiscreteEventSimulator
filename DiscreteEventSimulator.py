#!/usr/bin/python
# This code is a slight variation of the code from user http://codereview.stackexchange.com/users/5583/garetjax
# http://codereview.stackexchange.com/questions/3670/discrete-event-simulation-with-variable-intervals

import heapq


class Simulator(object):

    def __init__(self):
        self.queue = []
        self.time = 0

    def schedule(self, time, callback, *args, **kwargs):
        """
        Schedules an event to be executed at a later point in time.
        ``callback`` is a callable which executed the event-specific behavior;
        the optional ``args`` and ``kwargs`` arguments will be passed to the
        event callback at invocation time.

        Returns an object which can be used to reschedule the event.
        """
        assert time >= self.time
        event = [time, True, callback, args, kwargs]
        heapq.heappush(self.queue, event)
        return event

    def reschedule(self, event, time):
        """
        Reschedules ``event`` to take place at a different point in time
        """
        assert time >= self.time
        rescheduled = list(event)
        event[1] = False
        rescheduled[0] = time
        heapq.heappush(self.queue, rescheduled)
        return rescheduled

    def run(self, timeLimit):
        """
        Simple simulation function to test the behavior
        """
        while (self.queue):
            time, valid, callback, args, kwargs = heapq.heappop(self.queue)
            if (time > timeLimit):
                break
            if not valid:
                continue
            self.time = time
            callback(*args, **kwargs)
