import random
from enum import Enum
from collections import deque
from sample import Sample
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

    def add_event(self, event):
        # Insert event in the correct position to maintain time order
        self.events.append(event)
        self.events.sort()

    def process_next_event(self):
        if not self.events:
            return None

        event = self.events.pop(0)
        self.current_time = event.time

        if event.event_type == EventType.SAMPLE_ARRIVAL:
            self.handle_sample_arrival(event.sample)
        elif event.event_type == EventType.DOCTOR_COMPLETION:
            self.handle_doctor_completion(event.doctor)
        elif event.event_type == EventType.HEAD_DOCTOR_COMPLETION:
            self.handle_head_doctor_completion()

        return event

    def handle_sample_arrival(self, sample):
        # For samples that need head doctor review
        if sample.needs_head_doctor_review:
            sample.generate_head_doctor_processing_time()
            if self.head_doctor.is_available(self.current_time):
                # Assign directly if head doctor is available
                self.head_doctor.assign_sample(sample, self.current_time)
                # Schedule a completion event
                self.add_event(Event(
                    self.head_doctor.completion_time,
                    EventType.HEAD_DOCTOR_COMPLETION,
                    doctor=self.head_doctor,
                    sample=sample
                ))
            else:
                # Queue for head doctor review
                self.head_doctor_queue.append(sample)
        else:
            # Handle regular sample processing
            assigned = False
            for doctor in self.doctors:
                if doctor.is_available(self.current_time):
                    doctor.assign_sample(sample, self.current_time)
                    # Schedule a completion event
                    self.add_event(Event(
                        doctor.completion_time,
                        EventType.DOCTOR_COMPLETION,
                        doctor=doctor,
                        sample=sample
                    ))
                    assigned = True
                    break

            if not assigned:
                self.regular_queue.append(sample)

    def handle_doctor_completion(self, doctor):
        completed_sample = doctor.complete_sample()
        self.processed_samples.append(completed_sample)

        # Try to assign next sample from queue if available
        if self.regular_queue:
            next_sample = self.regular_queue.popleft()
            doctor.assign_sample(next_sample, self.current_time)
            self.add_event(Event(
                doctor.completion_time,
                EventType.DOCTOR_COMPLETION,
                doctor=doctor,
                sample=next_sample
            ))

    def handle_head_doctor_completion(self):
        completed_sample = self.head_doctor.complete_sample()
        self.processed_samples.append(completed_sample)

        # Try to assign next sample from head doctor queue if available
        if self.head_doctor_queue and self.head_doctor.is_available(self.current_time):
            next_sample = self.head_doctor_queue.popleft()
            self.head_doctor.assign_sample(next_sample, self.current_time)
            self.add_event(Event(
                self.head_doctor.completion_time,
                EventType.HEAD_DOCTOR_COMPLETION,
                doctor=self.head_doctor,
                sample=next_sample
            ))