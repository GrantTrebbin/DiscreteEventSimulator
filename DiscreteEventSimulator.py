#!/usr/bin/env python

# This code is a variation of the code from user
# http://codereview.stackexchange.com/users/5583/garetjax
# http://codereview.stackexchange.com/questions/3670/discrete-event-simulation-with-variable-intervals

"""Framework to manage and call events for a discrete event simulator.

Events that are to be run in the future are created and placed in a heap to be
run a certain time and with a certain priority. Once started, the next event on
the heap is continually called until there are none left or a time limit is
exceeded.
"""
import heapq


class Event(object):
    """The `Event` class is used to hold information about schedulable events.

    Attributes:
        time: The time that the `Event` will be called
        priority: Used to indicate the importance of the `Event`
        valid: Determines if the callback function in called when the
               `Event` object is called.  Set to true when instantiated.
        callback: Function to run when the `Event` object is called
        args: Positional arguments to pass to the `callback` attribute
        kwargs: Keyword arguments to pass to the `callback` attribute
    """

    def __init__(self, time, priority, callback, args, kwargs):
        """Initialize the Event object."""
        self.time = time
        self.priority = priority
        self.valid = True
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def invalidate(self):
        """Invalidate the Event.

        Set the `valid` attribute to False.  This prevents the `Event` object
        from being called
        """
        self.valid = False

    def reschedule(self, time):
        """Return a rescheduled event.

        Stop the `Event` object from running by setting the `valid` attribute
        to False.  Return a new `Event` object with all the same attributes
        except with the time attribute changed to the new time argument.

        Args:
            time (object): New time to reschedule the event.

        Returns:
            Event: new rescheduled event
        """
        self.invalidate()
        return Event(time, self.priority, self.callback, self.args, self.kwargs)

    def __call__(self, env):
        """Define callable behaviour of the `Event` Object.

        If the `valid` attribute is True, call the `callback` attribute of the
        `Event` object and pass the `Simulator` object to it along with the
        `args` and `kwargs` attributes.

        Args:
            env (Simulator):
        """
        if self.valid:
            self.callback(env, *self.args, **self.kwargs)

    def __lt__(self, other):
        """Less than comparison for `Event` objects.

        Less than comparison of `Event` objects by first comparing the time, if
        `time` attributes are equal then `priority` attributes are compared.

        Args:
            other (Event): Other `Event` object to compare to

        Returns:
            bool: The return value.  True if `self` is less than `other`
        """
        return [self.time, self.priority] < [other.time, other.priority]


class Simulator(object):
    """The `Simulator` class manages a heap of `Event` objects for simulations.

    After creating a `Simulation` object users can schedule actions that will be
    run in the future. Actor functions need to accept a variable that represents
    the simulation environment.

    Example

    def actor_function(env):
        perform some future action
        print(env.time)

    simulation = Simulator(0, 1000)
    simulation.schedule(1, 1, actor_function)
    simulation.schedule(10, 2, actor_function)
    simulation.schedule(10, 1, actor_function)
    simulation.run()

    Attributes:
        start_time: The time that the simulation will begin
        end_time: The time that the simulation will end
        kwargs: Keyword arguments that will be added as dynamic attributes of
            the `Simulator` object. For example, they can be used to hold a data
            structure or connection to a database that holds information about
            the state of the system being simulated.

            Example:

            database = sqlite3.connect(':memory:')
            simulation = Simulator(0, 1000, data=database)

            simulation.data will now provide access to the database


        @DynamicAttrs
    """

    def __init__(self, start_time, end_time, **kwargs):
        """Initialize the Simulator object."""
        assert end_time > start_time
        self.queue = []
        self.time = start_time
        self.end_time = end_time
        self.current_event = None
        for key, values in kwargs.items():
            setattr(self, key, values)

    def schedule(self, time, priority, callback, *args, **kwargs):
        """Schedule an event to be executed at a later point in time.

        Creates an `Event` object and places it in a heapq data structure.  The
        next `Event` to call will always be at the top of the ordered heap.
        ``callback`` is a callable which executes the event-specific behavior;
        the optional ``args`` and ``kwargs`` arguments will be passed to the
        event callback at invocation time.

        Args:
            time: The time to execute the `callback` argument.  Needs to be
                sortable
            priority: Used to differentiate `Event` objects scheduled to run at
                the same time. Needs to be sortable.
            callback: Function to call when the simulator time reaches `time`
            *args: positional arguments to pass to `callback`
            **kwargs: keyword arguments to pass to `callback`

        Returns: an `Event` object which can be used to reschedule the event.
        """
        assert time >= self.time
        event = Event(time, priority, callback, args, kwargs)
        try:
            heapq.heappush(self.queue, event)
        except TypeError:
            print(event)
            raise
        return event

    def schedule_relative(self,
                          offset_time,
                          priority,
                          callback,
                          *args,
                          **kwargs):
        """Schedule a future event by adding an offset to the current time.

        Args:
            offset_time: Added to the current `time` attribute to determine a
            time to schedule an `Event` object.  The time to execute the
            `callback` argument.  Needs to be sortable.
            priority: Used to differentiate `Event` objects scheduled to run at
                the same time. Needs to be sortable.
            callback: Function to call when the simulator time reaches `time`
            *args: positional arguments to pass to `callback`
            **kwargs: keyword arguments to pass to `callback`

        Returns: an `Event` object which can be used to reschedule the event.
        """
        return_event = self.schedule(self.time + offset_time,
                                     priority,
                                     callback,
                                     *args,
                                     **kwargs)
        return return_event

    def reschedule(self, old_event, time):
        """
        Reschedule an `Event` to take place at a different point in time.

        Args:
            old_event (Event): The event to be rescheduled
            time: Reschedule the old event at the new new `time` attribute

        Returns:
            Event: A new rescheduled event
        """
        assert time >= self.time
        new_event = old_event.reschedule(time)
        heapq.heappush(self.queue, new_event)
        return new_event

    def extend_end_time(self, new_end_time):
        """Extend the tim that the simulation is allowed to run.

        Args:
            new_end_time: The simulation will now be allowed to run until this
            time limit is reached.
        """
        assert new_end_time > self.end_time
        self.end_time = new_end_time

    def stop(self):
        """Stop the simulation.

        The simulation is halted by setting the simulation end time to the
        current time.  This prevent further execution of `Event` objects on the
        heap
        """
        self.end_time = self.time

    def run(self):
        """Start running the simulation.

        Run continually takes the next `Event` object from the heap and executes
        it.  This continues as long as there are events on the heap and the
        current simulation time is less than the `end_time` attribute.  The
        `Simulation` object is passed to the next `Event` when called.  This
        allows scheduled user defined functions to be aware of the simulation
        environment.
        """
        while self.queue:
            event = heapq.heappop(self.queue)
            self.current_event = event
            if self.end_time < event.time:
                break
            self.time = event.time
            event(self)
