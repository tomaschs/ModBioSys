import random
from histopathology_lab import HistopathologyLab, Event, EventType
from sample import Sample


class Simulation:
    def __init__(self, sample_arrival_mean=5, end_time=360):
        """
        Initialize simulation parameters

        Args:
            sample_arrival_mean: Mean time between sample arrivals in minutes
            end_time: End time of simulation in minutes (default: 360 = 6 hours)
        """
        self.sample_arrival_mean = sample_arrival_mean
        self.end_time = end_time
        self.lab = HistopathologyLab()

    def setup(self):
        # Generate all sample arrival events
        time = 0
        while time < self.end_time:
            # Generate next arrival time using exponential distribution
            # lambda = 1 / sample_arrival_mean
            time += random.expovariate(1.0 / self.sample_arrival_mean)
            if time < self.end_time:  # Only add if within working hours
                sample = Sample(time)
                self.lab.add_event(Event(time, EventType.SAMPLE_ARRIVAL, sample=sample))
                print(time)

        # Add head doctor shift start events
        if self.end_time >= 120:  # First shift at 10:00
            self.lab.add_event(Event(120, EventType.HEAD_DOCTOR_SHIFT_START))

        if self.end_time >= 240:  # Second shift at 12:00
            self.lab.add_event(Event(240, EventType.HEAD_DOCTOR_SHIFT_START))

        # Add simulation end event
        self.lab.add_event(Event(self.end_time, EventType.SIMULATION_END))

    def run(self):
        self.setup()

        while self.lab.events:
            event = self.lab.process_next_event()
            if event.event_type == EventType.SIMULATION_END:
                break

        # Process any remaining samples in queues for statistics
        remaining_samples = len(self.lab.regular_queue) + len(self.lab.head_doctor_queue)

        return {
            "processed_samples": len(self.lab.processed_samples),
            "remaining_samples": remaining_samples,
            "total_samples": len(self.lab.processed_samples) + remaining_samples,
            "samples": self.lab.processed_samples
        }