from doctor import Doctor


class HeadDoctor(Doctor):
    def __init__(self, doctor_id):
        super().__init__(doctor_id)
        self.completion_time = None
        self.busy = None
        self.current_sample = None

    def is_available(self, current_time):
        """
        Check if head doctor is available based on time constraints:
        - 10:00 to 11:00 (120 to 180 minutes from 8:00)
        - 12:00 to 14:00 (240 to 360 minutes from 8:00)
        """
        # First check if the doctor is not busy
        if self.busy and current_time < self.completion_time:
            return False

        # Available from 10:00-11:00 and 12:00-14:00
        working_hours = [(120, 180), (240, 360)]
        if any(start <= current_time <= end for start, end in working_hours):
            return True

        return False

    def assign_sample(self, sample, current_time):
        """Assign a sample to the head doctor with head doctor processing time"""
        if not self.is_available(current_time):
            return False

        self.busy = True
        self.current_sample = sample
        self.completion_time = current_time + sample.head_doctor_processing_time
        return True
