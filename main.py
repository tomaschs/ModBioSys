import random
from enum import Enum
from collections import deque
import matplotlib.pyplot as plt

from sample import Sample, SampleSize
from doctor import Doctor
from headDoctor import HeadDoctor


class EventType(Enum):
    SAMPLE_ARRIVAL = "sample_arrival"
    DOCTOR_COMPLETION = "doctor_completion"
    HEAD_DOCTOR_COMPLETION = "head_doctor_completion"
    SIMULATION_END = "simulation_end"


class Event:
    def __init__(self, time, event_type, doctor=None, sample=None):
        self.time = time
        self.event_type = event_type
        self.doctor = doctor
        self.sample = sample

    def __lt__(self, other):
        return self.time < other.time


class HistopathologyLab:
    def __init__(self, num_doctors=4):
        self.doctors = [Doctor(i) for i in range(num_doctors)]
        self.head_doctor = HeadDoctor(num_doctors)
        self.regular_queue = deque()
        self.head_doctor_queue = deque()
        self.processed_samples = []
        self.current_time = 0
        self.events = []

        # For statistics
        self.waiting_times = []
        self.queue_lengths = []
        self.queue_times = []
        self.doctor_utilization = []
        self.utilization_times = []

    def add_event(self, event):
        # Insert event in the correct position to maintain time order
        self.events.append(event)
        self.events.sort()

    def process_next_event(self):
        if not self.events:
            return None

        event = self.events.pop(0)
        self.current_time = event.time

        # Record queue length at this time
        self.queue_lengths.append(len(self.regular_queue) + len(self.head_doctor_queue))
        self.queue_times.append(self.current_time)

        # Record doctor utilization
        busy_doctors = sum(1 for doctor in self.doctors if doctor.busy)
        self.doctor_utilization.append(busy_doctors / len(self.doctors))
        self.utilization_times.append(self.current_time)

        if event.event_type == EventType.SAMPLE_ARRIVAL:
            self.handle_sample_arrival(event.sample)
        elif event.event_type == EventType.DOCTOR_COMPLETION:
            self.handle_doctor_completion(event.doctor)
        elif event.event_type == EventType.HEAD_DOCTOR_COMPLETION:
            self.handle_head_doctor_completion()

        return event

    def handle_sample_arrival(self, sample):
        if sample.needs_head_doctor_review:
            sample.generate_head_doctor_processing_time()
            if self.head_doctor.is_available(self.current_time):
                self.head_doctor.assign_sample(sample, self.current_time)
                self.add_event(Event(
                    self.head_doctor.completion_time,
                    EventType.HEAD_DOCTOR_COMPLETION,
                    doctor=self.head_doctor,
                    sample=sample
                ))
            else:
                sample.queue_entry_time = self.current_time
                self.head_doctor_queue.append(sample)
        else:
            assigned = False
            for doctor in self.doctors:
                if doctor.is_available(self.current_time):
                    doctor.assign_sample(sample, self.current_time)
                    self.add_event(Event(
                        doctor.completion_time,
                        EventType.DOCTOR_COMPLETION,
                        doctor=doctor,
                        sample=sample
                    ))
                    assigned = True
                    break

            if not assigned:
                sample.queue_entry_time = self.current_time
                self.regular_queue.append(sample)

    def handle_doctor_completion(self, doctor):
        completed_sample = doctor.complete_sample()
        completed_sample.completion_time = self.current_time
        self.processed_samples.append(completed_sample)

        if self.regular_queue:
            next_sample = self.regular_queue.popleft()
            wait_time = self.current_time - next_sample.queue_entry_time
            self.waiting_times.append(wait_time)

            doctor.assign_sample(next_sample, self.current_time)
            self.add_event(Event(
                doctor.completion_time,
                EventType.DOCTOR_COMPLETION,
                doctor=doctor,
                sample=next_sample
            ))

    def handle_head_doctor_completion(self):
        completed_sample = self.head_doctor.complete_sample()
        completed_sample.completion_time = self.current_time
        self.processed_samples.append(completed_sample)

        if self.head_doctor_queue and self.head_doctor.is_available(self.current_time):
            next_sample = self.head_doctor_queue.popleft()
            wait_time = self.current_time - next_sample.queue_entry_time
            self.waiting_times.append(wait_time)

            self.head_doctor.assign_sample(next_sample, self.current_time)
            self.add_event(Event(
                self.head_doctor.completion_time,
                EventType.HEAD_DOCTOR_COMPLETION,
                doctor=self.head_doctor,
                sample=next_sample
            ))


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

        return {
            "processed_samples": len(self.lab.processed_samples),
            "remaining_regular_queue": len(self.lab.regular_queue),
            "remaining_head_doctor_queue": len(self.lab.head_doctor_queue),
            "total_samples": (len(self.lab.processed_samples) +
                              len(self.lab.regular_queue) +
                              len(self.lab.head_doctor_queue)),
            "waiting_times": self.lab.waiting_times,
            "queue_lengths": self.lab.queue_lengths,
            "queue_times": self.lab.queue_times,
            "doctor_utilization": self.lab.doctor_utilization,
            "utilization_times": self.lab.utilization_times
        }

    def display_results(self, results):
        print("\n=== ŠTATISTIKY HISTOPATOLOGICKÉHO PRACOVISKA ===")
        print(f"Celkový počet vzoriek: {results['total_samples']}")
        print(f"Spracovaných vzoriek: {results['processed_samples']}")
        print(f"Nespracovaných vzoriek v bežnej rade: {results['remaining_regular_queue']}")
        print(f"Nespracovaných vzoriek pre primára: {results['remaining_head_doctor_queue']}")

        if results['waiting_times']:
            avg_wait = sum(results['waiting_times']) / len(results['waiting_times'])
            print(f"Priemerná doba čakania: {avg_wait:.2f} minút")
        else:
            print("Žiadne vzorky nečakali v rade.")

        # Calculate statistics by sample type
        sample_types = {SampleSize.SMALL: 0, SampleSize.MEDIUM: 0, SampleSize.LARGE: 0}
        for sample in self.lab.processed_samples:
            sample_types[sample.size] += 1

        print("\nRozdelenie vzoriek:")
        for size, count in sample_types.items():
            percentage = (count / len(self.lab.processed_samples)) * 100 if self.lab.processed_samples else 0
            print(f"  {size.value}: {count} ({percentage:.1f}%)")

        # Calculate how many samples needed head doctor review
        head_doctor_samples = sum(1 for sample in self.lab.processed_samples if sample.needs_head_doctor_review)
        print(
            f"\nVzorky vyžadujúce primára: {head_doctor_samples} ({(head_doctor_samples / len(self.lab.processed_samples)) * 100:.1f}%)")

        # Calculate average doctor utilization
        if results['doctor_utilization']:
            avg_utilization = sum(results['doctor_utilization']) / len(results['doctor_utilization']) * 100
            print(f"Priemerná vyťaženosť lekárov: {avg_utilization:.2f}%")

    def plot_results(self, results):
        # Plot 1: Queue length over time
        plt.figure(figsize=(12, 10))

        plt.subplot(2, 2, 1)
        plt.plot(results['queue_times'], results['queue_lengths'], 'b-')
        plt.title('Dĺžka radu v čase')
        plt.xlabel('Čas (minúty od 8:00)')
        plt.ylabel('Počet vzoriek v rade')
        plt.grid(True)

        # Plot 2: Doctor utilization over time
        plt.subplot(2, 2, 2)
        plt.plot(results['utilization_times'], [u * 100 for u in results['doctor_utilization']], 'r-')
        plt.title('Vyťaženosť lekárov v čase')
        plt.xlabel('Čas (minúty od 8:00)')
        plt.ylabel('Vyťaženosť (%)')
        plt.grid(True)

        # Plot 3: Waiting time histogram
        plt.subplot(2, 2, 3)
        if results['waiting_times']:
            plt.hist(results['waiting_times'], bins=20, color='green', alpha=0.7)
            plt.title('Histogram doby čakania')
            plt.xlabel('Doba čakania (minúty)')
            plt.ylabel('Počet vzoriek')
            plt.grid(True)
        else:
            plt.text(0.5, 0.5, "Žiadne čakacie doby", ha='center', va='center')

        # Plot 4: Sample type distribution
        sample_types = {SampleSize.SMALL.value: 0, SampleSize.MEDIUM.value: 0, SampleSize.LARGE.value: 0}
        for sample in self.lab.processed_samples:
            sample_types[sample.size.value] += 1

        plt.subplot(2, 2, 4)
        plt.pie(sample_types.values(), labels=sample_types.keys(), autopct='%1.1f%%',
                colors=['lightblue', 'lightgreen', 'coral'])
        plt.title('Rozdelenie typov vzoriek')

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)

    # Run the simulation
    sim = Simulation(sample_arrival_mean=5, end_time=360)
    results = sim.run()

    # Display and visualize results
    sim.display_results(results)
    sim.plot_results(results)