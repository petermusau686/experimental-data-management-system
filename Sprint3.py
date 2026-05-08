"""
EXPERIMENTAL DATA MANAGEMENT SYSTEM 

MILESTONES 1,2,3,4,5 and 6
FULL SYSTEM
"""

from datetime import datetime
import pandas as pd
import json
from collections import deque, defaultdict
import threading
import multiprocessing
import asyncio
import time
import math
from concurrent.futures import ThreadPoolExecutor


# CONFIGURATION
VALID_RANGES = {
    "pH": (2.5, 4.5),
    "alcohol": (8, 15),
    "density": (0.98, 1.04)
}

UNITS = {
    "fixed acidity": "g/dm³",
    "volatile acidity": "g/dm³",
    "citric acid": "g/dm³",
    "residual sugar": "g/dm³",
    "chlorides": "g/dm³",
    "free sulfur dioxide": "mg/dm³",
    "total sulfur dioxide": "mg/dm³",
    "density": "g/cm³",
    "pH": "",
    "alcohol": "%"
}


# CUSTOM EXCEPTIONS
class DataLoadError(Exception):
    pass


class ValidationError(Exception):
    pass


# LOGGING
def log(message):
    with open("log.txt", "a") as f:
        f.write(f"{datetime.now()} - {message}\n")


# SAFETY CHECK
def require_dataset(exp):
    if exp is None:
        print("\nPlease load the dataset first (Option 1).")
        return False
    return True


# STRATEGY PATTERN
class ValidationStrategy:
    def validate(self, variable, value):
        return True


class RangeValidation(ValidationStrategy):
    def validate(self, variable, value):
        if variable in VALID_RANGES:
            low, high = VALID_RANGES[variable]
            return low <= value <= high
        return True


# OBSERVER PATTERN
class Observer:
    def update(self, message):
        pass


class LoggerObserver(Observer):
    def update(self, message):
        log(message)


# MEASUREMENT CLASS
class Measurement:
    def __init__(self, variable, value, unit="", strategy=None):
        self.variable = variable
        self.value = value
        self.unit = unit
        self.strategy = strategy or RangeValidation()

    def is_valid(self):
        return self.strategy.validate(self.variable, self.value)

    def display(self):
        print(f"{self.variable}: {self.value} {self.unit}")


# TRIAL CLASS
class Trial:
    def __init__(self, trial_id, operator="Technician"):
        self.trial_id = trial_id
        self.operator = operator
        self.timestamp = datetime.now()
        self.measurements = []

    def add_measurement(self, measurement):
        self.measurements.append(measurement)

    def evaluate(self):
        return "PASS" if all(m.is_valid() for m in self.measurements) else "FAIL"

    def display(self):
        print(f"\nTrial {self.trial_id} ({self.operator})")
        for m in self.measurements:
            m.display()
        print("Result:", self.evaluate())


# EXPERIMENT CLASS
class Experiment:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.date_created = datetime.now()
        self.trials = []
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify(self, message):
        for obs in self.observers:
            obs.update(message)

    def add_trial(self, trial):
        self.trials.append(trial)
        self.notify(f"Trial {trial.trial_id} added")

    def evaluate_experiment(self):
        return "PASSED" if all(t.evaluate() == "PASS" for t in self.trials) else "FAILED"

    def get_statistics(self):
        total = len(self.trials)
        passed = sum(1 for t in self.trials if t.evaluate() == "PASS")

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed
        }

    def measurement_generator(self):
        for t in self.trials:
            for m in t.measurements:
                yield m

    def get_variables(self):
        return set(m.variable for m in self.measurement_generator())

   
    # ANALYTICS
    def analyze_sequential(self):
        start = time.time()

        data = [{"variable": m.variable, "value": m.value}
                for m in self.measurement_generator()]

        df = pd.DataFrame(data)

        print("\n===== SEQUENTIAL ANALYSIS =====")
        print(df.groupby("variable")["value"].mean())
        print(df.groupby("variable")["value"].var())

        duration = time.time() - start
        print(f"\nSequential Time: {duration:.4f}s")

        return duration

    def analyze_parallel(self):
        start = time.time()

        data = [{"variable": m.variable, "value": m.value}
                for m in self.measurement_generator()]

        df = pd.DataFrame(data)

        grouped = [(n, g["value"].tolist())
                   for n, g in df.groupby("variable")]

        with multiprocessing.Pool() as pool:
            means = pool.map(compute_mean, grouped)
            variances = pool.map(compute_variance, grouped)

        print("\nMeans:", means)
        print("Variances:", variances)

        duration = time.time() - start
        print(f"\nParallel Time: {duration:.4f}s")

        return duration


    # ASYNC EXPORT
    async def async_save_json(self, filename):
        await asyncio.sleep(1)

        data = [{"trial": t.trial_id,
                 "variable": m.variable,
                 "value": m.value}
                for t in self.trials
                for m in t.measurements]

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

        self.notify("JSON saved")

    async def async_save_csv(self, filename):
        await asyncio.sleep(1)

        data = [{"trial": t.trial_id,
                 "variable": m.variable,
                 "value": m.value}
                for t in self.trials
                for m in t.measurements]

        pd.DataFrame(data).to_csv(filename, index=False)

        self.notify("CSV saved")

    def threaded_export(self):
        with ThreadPoolExecutor(max_workers=2) as ex:
            ex.submit(asyncio.run, self.async_save_json("data.json"))
            ex.submit(asyncio.run, self.async_save_csv("data.csv"))

        print("Export complete")

    def display(self):
        print(f"\nExperiment: {self.name}")
        for t in self.trials:
            t.display()

        print("\nOverall:", self.evaluate_experiment())
        print("Statistics:", self.get_statistics())


# MULTIPROCESSING HELPERS
def compute_mean(group):
    variable, values = group
    return (variable, round(sum(values) / len(values), 4))


def compute_variance(group):
    variable, values = group
    mean = sum(values) / len(values)
    return (variable, round(sum((x - mean) ** 2 for x in values) / len(values), 4))


# MILESTONE 6: ANOMALY DETECTION MODULE
class AnomalyDetector:

    def __init__(self, experiment):
        self.experiment = experiment
        self.stats = {}

    def compute_stats(self):

        grouped = defaultdict(list)

        for m in self.experiment.measurement_generator():
            grouped[m.variable].append(m.value)

        for var, values in grouped.items():
            mean = sum(values) / len(values)
            std = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))

            self.stats[var] = {
                "mean": mean,
                "std": std
            }

        return self.stats

    def detect_anomalies(self, threshold=2.0):

        if not self.stats:
            self.compute_stats()

        results = []

        for m in self.experiment.measurement_generator():

            s = self.stats[m.variable]

            if s["std"] == 0:
                z = 0
            else:
                z = (m.value - s["mean"]) / s["std"]

            if abs(z) >= threshold:
                status = "🚨 OUTLIER"
            elif abs(z) >= 1:
                status = "⚠️ BORDERLINE"
            else:
                status = "✅ NORMAL"

            results.append({
                "variable": m.variable,
                "value": m.value,
                "z_score": round(z, 3),
                "status": status
            })

        return results

    def report(self):

        print("\n===== ANOMALY DETECTION REPORT =====")

        for r in self.detect_anomalies():
            print(f"{r['variable']}: {r['value']} | Z={r['z_score']} | {r['status']}")

class ProcessingQueue:
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()

    def add_task(self, task):
        with self.lock:
            self.queue.append(task)

    def worker(self):
        while True:
            with self.lock:
                if not self.queue:
                    break
                task = self.queue.popleft()

            print(f"{threading.current_thread().name} processing: {task}")
            log(f"{threading.current_thread().name} processed task: {task}")
            time.sleep(1)

    def process(self):
        threads = []

        for i in range(3):
            t = threading.Thread(target=self.worker, name=f"Worker-{i+1}")
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        print("All threaded tasks completed.")


# DATA LOADER
def load_from_csv(file_path):

    try:
        df = pd.read_csv(file_path, sep=';')
    except Exception as e:
        raise DataLoadError(str(e))

    exp = Experiment("Wine Quality System", "EDMS Milestone 6")
    exp.add_observer(LoggerObserver())

    for i, row in df.iterrows():
        trial = Trial(i + 1)

        for col in df.columns:
            value = row[col]
            unit = UNITS.get(col, "")

            if pd.isna(value):
                raise ValidationError("Missing value")

            trial.add_measurement(Measurement(col, value, unit))

        exp.add_trial(trial)

    return exp


# MENU
def menu():
    print("\n===== EDMS MENU =====")
    print("1. Load Dataset")
    print("2. Display")
    print("3. Sequential Analysis")
    print("4. Parallel Analysis")
    print("5. Export Async")
    print("6. Variables")
    print("7. Thread Queue")
    print("8. Benchmark")
    print("9. Exit")
    print("10. Anomaly Detection")



# MAIN
if __name__ == "__main__":

    multiprocessing.freeze_support()

    exp = None
    queue = ProcessingQueue()

    while True:

        menu()
        choice = input("Enter choice: ")

        try:

            if choice == "1":
                path = input("CSV path: ")
                exp = load_from_csv(path)
                print("Loaded!")

            elif choice == "2":
                if not require_dataset(exp): continue
                exp.display()

            elif choice == "3":
                if not require_dataset(exp): continue
                exp.analyze_sequential()

            elif choice == "4":
                if not require_dataset(exp): continue
                exp.analyze_parallel()

            elif choice == "5":
                if not require_dataset(exp): continue
                exp.threaded_export()

            elif choice == "6":
                if not require_dataset(exp): continue
                print(exp.get_variables())

            elif choice == "7":
                queue.process()

            elif choice == "8":
                if not require_dataset(exp): continue
                s = exp.analyze_sequential()
                p = exp.analyze_parallel()
                print("Improvement:", s - p)

            elif choice == "10":
                if not require_dataset(exp): continue
                AnomalyDetector(exp).report()

            elif choice == "9":
                break

        except Exception as e:
            print("Error:", e)