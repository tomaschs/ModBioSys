class Doctor:
    def __init__(self, doctor_id):
        self.doctor_id = doctor_id
        self.busy = False
        self.current_sample = None
        self.completion_time = 0

    def is_available(self, current_time):
        return not self.busy or current_time >= self.completion_time

    def assign_sample(self, sample, current_time):
        """Assign a sample to the doctor and calculate completion time"""
        if not self.is_available(current_time):
            return False

        self.busy = True
        self.current_sample = sample
        self.completion_time = current_time + sample.processing_time
        return True

    def complete_sample(self):
        """Mark the current sample as completed"""
        completed_sample = self.current_sample
        self.busy = False
        self.current_sample = None
        return completed_sample

    def __str__(self):
        status = "busy" if self.busy else "available"
        return f"Doctor #{self.doctor_id} ({status})"