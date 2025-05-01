import random
from histopathology_lab import HistopathologyLab, Event, EventType
from sample import Sample


class Simulation:
    def __init__(self, sample_arrival_mean=5, end_time=360, num_doctors=4):
        """
        Initialize simulation parameters

        Args:
            sample_arrival_mean: Mean time between sample arrivals in minutes
            end_time: End time of simulation in minutes (default: 360 = 6 hours)
        """
        self.sample_arrival_mean = sample_arrival_mean
        self.end_time = end_time
        self.lab = HistopathologyLab(num_doctors)

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
                # print(time)

        # Add head doctor shift start events
        if self.end_time >= 120:  # First shift at 10:00
            self.lab.add_event(Event(120, EventType.HEAD_DOCTOR_SHIFT_START))

        if self.end_time >= 240:  # Second shift at 12:00
            self.lab.add_event(Event(240, EventType.HEAD_DOCTOR_SHIFT_START))

        # Add simulation end event
        self.lab.add_event(Event(self.end_time, EventType.SIMULATION_END))

    def run(self):
        self.setup()
        simulation_ended = False

        while self.lab.events:
            event = self.lab.process_next_event()

            if event.event_type == EventType.SIMULATION_END:
                simulation_ended = True

            # Only exit when simulation has ended AND all processing is complete
            if simulation_ended:
                if (not any(doc.busy for doc in self.lab.doctors) and
                        not self.lab.head_doctor.busy and
                        len(self.lab.regular_queue) == 0 and
                        len(self.lab.head_doctor_queue) == 0):
                    break

        return {
            "processed_samples": len(self.lab.processed_samples),
            "samples": self.lab.processed_samples
        }
