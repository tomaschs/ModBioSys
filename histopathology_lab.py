import random
from enum import Enum
from collections import deque
from sample import Sample
from doctor import Doctor
from headDoctor import HeadDoctor


def set_sample_end_time(sample, time):
    sample.end_time = time


class EventType(Enum):
    SAMPLE_ARRIVAL = "sample_arrival"
    DOCTOR_COMPLETION = "doctor_completion"
    HEAD_DOCTOR_COMPLETION = "head_doctor_completion"
    SIMULATION_END = "simulation_end"
    HEAD_DOCTOR_SHIFT_START = "head_doctor_shift_start"


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
        self.waiting_samples = deque()
        self.processed_samples = []
        self.current_time = 0
        self.events = []

        # For statistics tracking
        self.waiting_times = []
        self.regular_queue_lengths = []
        self.head_doctor_queue_lengths = []
        # self.queue_lengths = []
        self.queue_times = []
        self.doctor_utilization = []
        self.utilization_times = []

    def add_event(self, event):
        # Insert event in the correct position to maintain time order
        self.events.append(event)
        self.events.sort()

    def schedule_event(self, time, event_type, doctor=None, sample=None):
        self.add_event(Event(time, event_type, doctor, sample))

    def process_next_event(self):
        if not self.events:
            return None

        event = self.events.pop(0)
        self.current_time = event.time

        # Record queue length at this time
        # self.queue_lengths.append(len(self.regular_queue) + len(self.head_doctor_queue))
        self.regular_queue_lengths.append(len(self.regular_queue))
        self.head_doctor_queue_lengths.append(len(self.head_doctor_queue))
        self.queue_times.append(self.current_time)

        # Record doctor and head_doctor utilization
        utilization_row = [1 if doctor.busy else 0 for doctor in self.doctors]
        utilization_row.append(1 if self.head_doctor.busy else 0)  # primár ako posledný
        self.doctor_utilization.append(utilization_row)
        self.utilization_times.append(self.current_time)

        if event.event_type == EventType.SAMPLE_ARRIVAL:
            self.handle_sample_arrival(event.sample)
        elif event.event_type == EventType.DOCTOR_COMPLETION:
            self.handle_doctor_completion(event.doctor)
        elif event.event_type == EventType.HEAD_DOCTOR_COMPLETION:
            self.handle_head_doctor_completion()
        elif event.event_type == EventType.HEAD_DOCTOR_SHIFT_START:
            self.handle_head_doctor_shift_start()

        return event

    def handle_sample_arrival(self, sample):
        # All samples first go through normal doctors
        assigned = False
        for doctor in self.doctors:
            if doctor.is_available(self.current_time):
                doctor.assign_sample(sample, self.current_time)
                # Schedule a completion event
                self.schedule_event(doctor.completion_time, EventType.DOCTOR_COMPLETION, doctor, sample)
                assigned = True
                break

        if not assigned:
            # Add queue entry time for waiting time statistics
            sample.queue_entry_time = self.current_time
            self.waiting_samples.append(sample)
            self.regular_queue.append(sample)

    def handle_doctor_completion(self, doctor):
        completed_sample = doctor.complete_sample()

        # Check if this sample needs head doctor review
        if completed_sample.needs_head_doctor_review:
            completed_sample.generate_head_doctor_processing_time()
            if self.head_doctor.is_available(self.current_time):
                # Assign to head doctor
                self.head_doctor.assign_sample(completed_sample, self.current_time)
                # Schedule a completion event
                self.schedule_event(self.head_doctor.completion_time, EventType.HEAD_DOCTOR_COMPLETION,
                                    self.head_doctor, completed_sample)
            else:
                # Queue for head doctor review
                if not hasattr(completed_sample, 'queue_entry_time'):
                    completed_sample.queue_entry_time = self.current_time

                self.waiting_samples.append(completed_sample)
                self.head_doctor_queue.append(completed_sample)
        else:
            # Regular sample is fully processed
            set_sample_end_time(completed_sample, self.current_time)
            self.processed_samples.append(completed_sample)

        # Try to assign next sample from queue if available
        if self.regular_queue:
            next_sample = self.regular_queue.popleft()
            # Calculate waiting time for statistics
            if hasattr(next_sample, 'queue_entry_time'):
                wait_time = self.current_time - next_sample.queue_entry_time
                if not hasattr(self, 'waiting_times'):
                    self.waiting_times = []
                self.waiting_times.append(wait_time)

            doctor.assign_sample(next_sample, self.current_time)
            self.schedule_event(doctor.completion_time, EventType.DOCTOR_COMPLETION, doctor, next_sample)

    def handle_head_doctor_completion(self):
        completed_sample = self.head_doctor.complete_sample()
        set_sample_end_time(completed_sample, self.current_time)
        self.processed_samples.append(completed_sample)

        # Try to assign next sample from head doctor queue if available
        if self.head_doctor_queue and self.head_doctor.is_available(self.current_time):
            next_sample = self.head_doctor_queue.popleft()

            # Calculate waiting time for statistics
            if hasattr(next_sample, 'queue_entry_time'):
                wait_time = self.current_time - next_sample.queue_entry_time
                self.waiting_times.append(wait_time)

            self.head_doctor.assign_sample(next_sample, self.current_time)
            self.schedule_event(self.head_doctor.completion_time, EventType.HEAD_DOCTOR_COMPLETION, self.head_doctor, next_sample)

    def handle_head_doctor_shift_start(self):
        # Check if there are samples waiting and the head doctor is available
        if self.head_doctor_queue and self.head_doctor.is_available(self.current_time):
            next_sample = self.head_doctor_queue.popleft()
            wait_time = self.current_time - next_sample.queue_entry_time
            self.waiting_times.append(wait_time)

            self.head_doctor.assign_sample(next_sample, self.current_time)
            self.schedule_event(self.head_doctor.completion_time, EventType.HEAD_DOCTOR_COMPLETION, self.head_doctor, next_sample)
