import random
from HistopathologyLab import HistopathologyLab


class Simulation:
    def __init__(self, sample_arrival_mean=5, end_time=360):
        """
        Initialize simulation parameters

        Args:
            sample_arrival_mean: Mean time between sample arrivals in minutes
            end_time: End time of simulation in minutes (default: 360 = 6 hours)
        """
        self.sample_arrival_mean = sample_arrival_mean  # average 5 minutes between arrivals
        self.end_time = end_time  # 8:00 - 14:00 = 6 hours = 360 minutes
        self.lab = HistopathologyLab()

    def setup(self):
        # Generate all sample arrival events
        time = 0
        while time < self.end_time:
            # Generate next arrival time using exponential distribution
            time += random.expovariate(1.0 / self.sample_arrival_mean)
            if time < self.end_time:  # Only add if within working hours
                sample = Sample(time)
                self.lab.add_event(Event(time, EventType.SAMPLE_ARRIVAL, sample=sample))

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

# To run the simulation:
sim = Simulation()
results = sim.run()
print(f"Processed {results['processed_samples']} samples")
print(f"Remaining {results['remaining_samples']} samples in queues at end of day")