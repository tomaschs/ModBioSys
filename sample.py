import random
import enum


class SampleSize(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Sample:
    def __init__(self, arrival_time):
        self.arrival_time = arrival_time
        # 10% large, 20% medium, 70% small
        # normalvariate = normal distribution
        size_rand = random.random()
        if size_rand < 0.1:
            self.size = SampleSize.LARGE
            self.processing_time = random.normalvariate(20, 2)
        elif size_rand < 0.3:
            self.size = SampleSize.MEDIUM
            self.processing_time = random.normalvariate(15, 1.5)
        else:
            self.size = SampleSize.SMALL
            self.processing_time = random.normalvariate(7, 1)

        # Determine if this sample needs head doctor review (10% of small samples)
        self.needs_head_doctor_review = (
                self.size == SampleSize.SMALL and random.random() < 0.1
        )
        self.head_doctor_processing_time = None

    def generate_head_doctor_processing_time(self):
        if self.needs_head_doctor_review:
            self.head_doctor_processing_time = random.normalvariate(10, 1)
        else:
            self.head_doctor_processing_time = 0
        return self.head_doctor_processing_time

    def __str__(self):
        return f"Sample({self.size.value}, arrived at {self.arrival_time})"
