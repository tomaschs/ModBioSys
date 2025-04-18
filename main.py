import random
import matplotlib.pyplot as plt
from sample import Sample, SampleSize
from doctor import Doctor
from headDoctor import HeadDoctor
from histopathology_lab import HistopathologyLab, EventType, Event
from simulation import Simulation
from datetime import datetime


# def display_results(lab, results):
#     print("\n=== ŠTATISTIKY HISTOPATOLOGICKÉHO PRACOVISKA ===")
#     print(f"Spracovaných vzoriek: {results['processed_samples']}")
#     print(f"Nespracovaných vzoriek: {results['remaining_samples']}")
#     print(f"Celkový počet spracovaných + nespracovaných vzoriek: {results['total_samples']}")
#
#     if hasattr(lab, 'waiting_times') and lab.waiting_times:
#         avg_wait = sum(lab.waiting_times) / len(lab.waiting_times)
#         print(f"Priemerná doba čakania: {avg_wait:.2f} minút")
#     else:
#         print("Žiadne vzorky nečakali v rade.")
#
#     # Calculate statistics by sample type
#     sample_types = {SampleSize.SMALL: 0, SampleSize.MEDIUM: 0, SampleSize.LARGE: 0}
#     for sample in lab.processed_samples:
#         sample_types[sample.size] += 1
#
#     print("\nRozdelenie vzoriek:")
#     for size, count in sample_types.items():
#         percentage = (count / len(lab.processed_samples)) * 100 if lab.processed_samples else 0
#         print(f"  {size.value}: {count} ({percentage:.1f}%)")
#
#     # Calculate how many samples needed head doctor review
#     head_doctor_samples = sum(1 for sample in lab.processed_samples if sample.needs_head_doctor_review)
#     if lab.processed_samples:
#         hd_percentage = (head_doctor_samples / len(lab.processed_samples)) * 100
#         print(f"\nVzorky vyžadujúce primára: {head_doctor_samples} ({hd_percentage:.1f}%)")
#
#     # Calculate average doctor utilization if available
#     if hasattr(lab, 'doctor_utilization') and lab.doctor_utilization:
#         avg_utilization = sum(lab.doctor_utilization) / len(lab.doctor_utilization) * 100
#         print(f"Priemerná vyťaženosť lekárov: {avg_utilization:.2f}%")


# def plot_results(lab, results):
#     if not (hasattr(lab, 'queue_lengths') and hasattr(lab, 'queue_times')):
#         print("Insufficient data for plotting")
#         return
#
#     # Plot 1: Queue length over time
#     plt.figure(figsize=(12, 10))
#
#     plt.subplot(2, 2, 1)
#     plt.plot(lab.queue_times, lab.queue_lengths, 'b-')
#     plt.title('Dĺžka radu v čase')
#     plt.xlabel('Čas (minúty od 8:00)')
#     plt.ylabel('Počet vzoriek v rade')
#     plt.grid(True)
#
#     # Plot 2: Doctor utilization over time
#     if hasattr(lab, 'doctor_utilization') and hasattr(lab, 'utilization_times'):
#         plt.subplot(2, 2, 2)
#         plt.plot(lab.utilization_times, [u * 100 for u in lab.doctor_utilization], 'r-')
#         plt.title('Vyťaženosť lekárov v čase')
#         plt.xlabel('Čas (minúty od 8:00)')
#         plt.ylabel('Vyťaženosť (%)')
#         plt.grid(True)
#
#     # Plot 3: Waiting time histogram
#     plt.subplot(2, 2, 3)
#     if hasattr(lab, 'waiting_times') and lab.waiting_times:
#         plt.hist(lab.waiting_times, bins=20, color='green', alpha=0.7)
#         plt.title('Histogram doby čakania')
#         plt.xlabel('Doba čakania (minúty)')
#         plt.ylabel('Počet vzoriek')
#         plt.grid(True)
#     else:
#         plt.text(0.5, 0.5, "Žiadne čakacie doby", ha='center', va='center')
#
#     # Plot 4: Sample type distribution
#     sample_types = {SampleSize.SMALL.value: 0, SampleSize.MEDIUM.value: 0, SampleSize.LARGE.value: 0}
#     for sample in lab.processed_samples:
#         sample_types[sample.size.value] += 1
#
#     plt.subplot(2, 2, 4)
#     plt.pie(sample_types.values(), labels=sample_types.keys(), autopct='%1.1f%%',
#             colors=['lightblue', 'lightgreen', 'coral'])
#     plt.title('Rozdelenie typov vzoriek')
#
#     plt.tight_layout()
#     plt.show()


if __name__ == "__main__":
    random.seed(datetime.now().timestamp())

    # od 8:00 do 14:00 (6 hodín) = 6*60 = 360 minút
    sim = Simulation(sample_arrival_mean=5, end_time=360)
    results = sim.run()

    # display_results(sim.lab, results)
    # plot_results(sim.lab, results)
