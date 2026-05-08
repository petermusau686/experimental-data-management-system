"""
FUNDAMENTALS OF OBJECT ORIENTED PROGRAMMING
EXPERIMENTAL DATA MANAGEMENT SYSTEM

Milestones 1 & 2
"""

from datetime import datetime

class Measurement:
    def __init__(self, variable, value, unit):
        self.variable = variable
        self.value = value
        self.unit = unit

    def is_valid(self):
        return True

    def display(self):
        print(f"{self.variable}: {self.value} {self.unit}")


class TemperatureMeasurement(Measurement):
    def is_valid(self):
        return 20 <= self.value <= 30


class PHMeasurement(Measurement):
    def is_valid(self):
        return 6.0 <= self.value <= 7.5


class WeightMeasurement(Measurement):
    def is_valid(self):
        return 98 <= self.value <= 102


class Trial:
    def __init__(self, trial_id, operator):
        self.trial_id = trial_id
        self.operator = operator
        self.timestamp = datetime.now()
        self.measurements = []

    def add_measurement(self, measurement):
        self.measurements.append(measurement)

    def remove_measurement(self, variable):
        self.measurements = [m for m in self.measurements if m.variable != variable]

    def get_measurement(self, variable):
        for m in self.measurements:
            if m.variable == variable:
                return m
        return None

    def evaluate(self):
        for m in self.measurements:
            if not m.is_valid():
                return "FAIL"
        return "PASS"

    def summary(self):
        return {
            "trial_id": self.trial_id,
            "operator": self.operator,
            "result": self.evaluate()
        }

    def display(self):
        print(f"\nTrial {self.trial_id} (Operator: {self.operator})")
        for m in self.measurements:
            m.display()
        print("Result:", self.evaluate())

class Experiment:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.date_created = datetime.now()
        self.trials = []

    def add_trial(self, trial):
        self.trials.append(trial)

    def remove_trial(self, trial_id):
        self.trials = [t for t in self.trials if t.trial_id != trial_id]

    def get_trial(self, trial_id):
        for t in self.trials:
            if t.trial_id == trial_id:
                return t
        return None

    def evaluate_experiment(self):
        results = [t.evaluate() for t in self.trials]
        return "FAILED" if "FAIL" in results else "PASSED"

    def get_statistics(self):
        total = len(self.trials)
        passed = sum(1 for t in self.trials if t.evaluate() == "PASS")
        failed = total - passed
        return {
            "total_trials": total,
            "passed": passed,
            "failed": failed
        }

    def display(self):
        print(f"\nExperiment: {self.name}")
        print(f"Description: {self.description}")
        print(f"Date: {self.date_created}")

        for t in self.trials:
            t.display()

        print("\nOverall Result:", self.evaluate_experiment())
        print("Statistics:", self.get_statistics())


class ExperimentManager:
    def __init__(self):
        self.experiments = []

    def add_experiment(self, experiment):
        self.experiments.append(experiment)

    def find_experiment(self, name):
        for exp in self.experiments:
            if exp.name == name:
                return exp
        return None

    def list_experiments(self):
        for exp in self.experiments:
            print(exp.name)

    def display_all(self):
        for exp in self.experiments:
            exp.display()


class Report:
    def __init__(self, experiment):
        self.experiment = experiment

    def generate(self):
        stats = self.experiment.get_statistics()
        print("\nEXPERIMENT REPORT")
        print("Name:", self.experiment.name)
        print("Total Trials:", stats["total_trials"])
        print("Passed:", stats["passed"])
        print("Failed:", stats["failed"])
        print("Final Status:", self.experiment.evaluate_experiment())




if __name__ == "__main__":

    manager = ExperimentManager()

    exp = Experiment("Milk Quality Test", "Testing milk under controlled conditions")

    t1 = Trial(1, "Alice")
    t1.add_measurement(TemperatureMeasurement("Temperature", 25, "C"))
    t1.add_measurement(PHMeasurement("pH", 6.8, ""))
    t1.add_measurement(WeightMeasurement("Weight", 100, "g"))

    t2 = Trial(2, "Bob")
    t2.add_measurement(TemperatureMeasurement("Temperature", 35, "C")) 
    t2.add_measurement(PHMeasurement("pH", 6.5, ""))
    t2.add_measurement(WeightMeasurement("Weight", 101, "g"))

    exp.add_trial(t1)
    exp.add_trial(t2)

    manager.add_experiment(exp)

    manager.display_all()

    report = Report(exp)
    report.generate()

