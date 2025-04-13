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
    def __init__(self, num_doctors=4, verbose=True):
        self.doctors = [Doctor(i) for i in range(num_doctors)]
        self.head_doctor = HeadDoctor(num_doctors)
        self.regular_queue = deque()
        self.head_doctor_queue = deque()
        self.processed_samples = []
        self.current_time = 0
        self.events = []
        self.verbose = verbose  # Whether to print detailed logs

        # For statistics tracking
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

        # After processing each event, show status summary
        if self.verbose:
            busy_count = sum(1 for doctor in self.doctors if doctor.busy)
            head_busy = "Áno" if self.head_doctor.busy else "Nie"
            print(f"STATUS: Zaneprázdnení doktori: {busy_count}/{len(self.doctors)}, "
                  f"Primár zaneprázdnený: {head_busy}, "
                  f"Vzorky v rade: {len(self.regular_queue)}, "
                  f"Vzorky v rade primára: {len(self.head_doctor_queue)}, "
                  f"Dokončené vzorky: {len(self.processed_samples)}")
            print("------------------------------------------------------------")

        return event

    def handle_sample_arrival(self, sample):
        if self.verbose:
            print(
                f"[{self.current_time:.2f} min] Príchod vzorky {sample.size.value}, potrebuje primára: {sample.needs_head_doctor_review}")

        # All samples first go through normal doctors
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
                if self.verbose:
                    print(
                        f"          Vzorka pridelená doktorovi #{doctor.doctor_id}, dokončenie v čase {doctor.completion_time:.2f}")
                assigned = True
                break

        if not assigned:
            # Add queue entry time for waiting time statistics
            sample.queue_entry_time = self.current_time
            self.regular_queue.append(sample)
            if self.verbose:
                print(
                    f"          Všetci doktori sú zaneprázdnení. Vzorka ide do radu. Dĺžka radu: {len(self.regular_queue)}")

    def handle_doctor_completion(self, doctor):
        completed_sample = doctor.complete_sample()
        if self.verbose:
            print(
                f"[{self.current_time:.2f} min] Doktor #{doctor.doctor_id} dokončil vzorku {completed_sample.size.value}")

        # Check if this sample needs head doctor review
        if completed_sample.needs_head_doctor_review:
            completed_sample.generate_head_doctor_processing_time()
            if self.verbose:
                print(f"          Vzorka potrebuje posúdenie primárom")

            if self.head_doctor.is_available(self.current_time):
                # Assign directly to head doctor
                self.head_doctor.assign_sample(completed_sample, self.current_time)
                # Schedule a completion event
                self.add_event(Event(
                    self.head_doctor.completion_time,
                    EventType.HEAD_DOCTOR_COMPLETION,
                    doctor=self.head_doctor,
                    sample=completed_sample
                ))
                if self.verbose:
                    print(
                        f"          Vzorka pridelená primárovi, dokončenie v čase {self.head_doctor.completion_time:.2f}")
            else:
                # Queue for head doctor review
                if not hasattr(completed_sample, 'queue_entry_time'):
                    completed_sample.queue_entry_time = self.current_time
                self.head_doctor_queue.append(completed_sample)
                if self.verbose:
                    print(
                        f"          Primár nie je dostupný. Vzorka ide do radu primára. Dĺžka radu: {len(self.head_doctor_queue)}")
        else:
            # Regular sample is fully processed
            self.processed_samples.append(completed_sample)
            if self.verbose:
                print(f"          Vzorka spracovaná, potreba primára: {completed_sample.needs_head_doctor_review}")

        # Try to assign next sample from queue if available
        if self.regular_queue:
            next_sample = self.regular_queue.popleft()
            # Calculate waiting time for statistics
            if hasattr(next_sample, 'queue_entry_time'):
                wait_time = self.current_time - next_sample.queue_entry_time
                if not hasattr(self, 'waiting_times'):
                    self.waiting_times = []
                self.waiting_times.append(wait_time)
                if self.verbose:
                    print(
                        f"          Ďalšia vzorka z radu pridelená doktorovi #{doctor.doctor_id} (čakala {wait_time:.2f} min)")

            doctor.assign_sample(next_sample, self.current_time)
            self.add_event(Event(
                doctor.completion_time,
                EventType.DOCTOR_COMPLETION,
                doctor=doctor,
                sample=next_sample
            ))
            if self.verbose:
                print(f"          Dokončenie odhadované na {doctor.completion_time:.2f}")
        else:
            if self.verbose:
                print(f"          Doktor #{doctor.doctor_id} je teraz voľný")

    def handle_head_doctor_completion(self):
        completed_sample = self.head_doctor.complete_sample()
        self.processed_samples.append(completed_sample)
        if self.verbose:
            print(f"[{self.current_time:.2f} min] Primár dokončil posúdenie vzorky")

        # Try to assign next sample from head doctor queue if available
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
            if self.verbose:
                print(f"          Ďalšia vzorka z radu pridelená primárovi (čakala {wait_time:.2f} min)")
                print(f"          Dokončenie odhadované na {self.head_doctor.completion_time:.2f}")
        else:
            if self.verbose:
                if self.head_doctor_queue:
                    print(
                        f"          Primár nie je dostupný v tomto čase. Vzorky v rade: {len(self.head_doctor_queue)}")
                else:
                    print(f"          Primár je teraz voľný")