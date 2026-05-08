"""
EXPERIMENTAL DATA MANAGEMENT SYSTEM 

MILESTONES 1,2,3 AND 4
"""

from datetime import datetime
import pandas as pd
import json
from collections import deque


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


# EXCEPTIONS
class DataLoadError(Exception):
    pass

class ValidationError(Exception):
    pass


# LOGGING
def log(message):
    with open("log.txt", "a") as f:
        f.write(f"{datetime.now()} - {message}\n")


# STRATEGY PATTERN (Validation)
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
        print(f"Timestamp: {self.timestamp}")
        for m in self.measurements:
            m.display()
        print("Result:", self.evaluate())


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
        return {"total": total, "passed": passed, "failed": total - passed}

    # Milestone 3 Features 
    def measurement_generator(self):
        for t in self.trials:
            for m in t.measurements:
                yield m

    def get_valid_measurements(self):
        return list(filter(lambda m: m.is_valid(), self.measurement_generator()))

    def get_variables(self):
        return set(m.variable for m in self.measurement_generator())

    def analyze(self):
        data = [
            {"variable": m.variable, "value": m.value}
            for m in self.measurement_generator()
        ]

        df = pd.DataFrame(data)

        print("\n=== ANALYSIS ===")
        print("Mean:\n", df.groupby("variable")["value"].mean())
        print("\nVariance:\n", df.groupby("variable")["value"].var())

    def save_csv(self, filename):
        data = [
            {"trial": t.trial_id, "variable": m.variable, "value": m.value}
            for t in self.trials for m in t.measurements
        ]
        pd.DataFrame(data).to_csv(filename, index=False)
        self.notify("Data saved to CSV")

    def save_json(self, filename):
        data = [
            {"trial": t.trial_id, "variable": m.variable, "value": m.value}
            for t in self.trials for m in t.measurements
        ]
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        self.notify("Data saved to JSON")

    def display(self, limit = 10):
        print(f"\nExperiment: {self.name}")
        for t in self.trials[:limit]:
            t.display()
        print(f"\nShowing first {limit} trials only...")   
        print("\nOverall:", self.evaluate_experiment())
        print("Stats:", self.get_statistics())



class ProcessingQueue:
    def __init__(self):
        self.queue = deque()

    def add_task(self, task):
        self.queue.append(task)

    def process(self):
        while self.queue:
            task = self.queue.popleft()
            task()
            print("Processing:", task)
            log(f"Processed task: {task}")
        

# DATA LOADER
def load_from_csv(file_path):
    try:
        df = pd.read_csv(file_path, sep=';')
    except FileNotFoundError:
        raise DataLoadError("File not found")
    except Exception as e:
        raise DataLoadError(f"Error loading file: {e}")

    exp = Experiment("Wine Quality Experiment", "Real dataset")
    exp.add_observer(LoggerObserver())

    for i, row in df.iterrows():
        trial = Trial(i + 1)

        for column in df.columns:
            unit = UNITS.get(column, "")
            value = row[column]

            if pd.isna(value):
                raise ValidationError(f"Missing value in column {column}")

            trial.add_measurement(Measurement(column, value, unit))

        exp.add_trial(trial)

    log("Dataset loaded successfully")
    return exp


# MENU
def menu():
    print("\n===== EDMS MENU =====")
    print("1. Load Dataset")
    print("2. Display Experiment")
    print("3. Analyze Data")
    print("4. Save CSV")
    print("5. Save JSON")
    print("6. Show Variables")
    print("7. Process Tasks")
    print("8. Exit")


if __name__ == "__main__":

    exp = None
    queue = ProcessingQueue()

    while True:
        menu()
        choice = input("Enter choice: ")

        try:
            if choice == "1":
                path = input("Enter CSV path: ")
                exp = load_from_csv(path)
                print("Dataset loaded successfully!")

            elif choice == "2":
                exp.display()

            elif choice == "3":
                exp.analyze()

            elif choice == "4":
                exp.save_csv("output.csv")
                print("Saved to CSV!")

            elif choice == "5":
                exp.save_json("output.json")
                print("Saved to JSON!")

            elif choice == "6":
                print("Variables:", exp.get_variables())

            elif choice == "7":
                queue.add_task("Analyze Data")
                queue.add_task("Save Results")
                queue.process()

            elif choice == "8":
                print("Exiting...")
                break

            else:
                print("Invalid choice.")

        except DataLoadError as e:
            print("Data Error:", e)

        except ValidationError as e:
            print("Validation Error:", e)

        except Exception as e:
            print("Unexpected Error:", e)