from RecoveryModel import *
from OpensGui import *
import tkinter as tk


class Controller:
    def __init__(self):
        root = tk.Tk()
        root.title("OPENS")
        self.view = Application(root, self)
        root.mainloop()

    def getRecoverMethods(self,methods, strategy):
        name_list = []
        coverage_list =[]
        mttr_list =[]
        mttf_list =[]
        probability_list = []
        recovery_methods = []
        for method in methods:
            tokens = method.split()
            name_list.append(tokens[0])
            coverage_list.append(float(tokens[1]))
            mttr_list.append(float(tokens[2]))
            mttf_list.append(float(tokens[3]))
        if strategy == 0:
            probability_list =[1]+[0]*(len(coverage_list)-1)
        elif strategy == 1:
            probability_list = [item/sum(coverage_list) for item in coverage_list]

        for i in range(len(methods)):
            recovery_methods.append(RecoveryMethod(name_list[i],
                                                   coverage_list[i],
                                                   probability_list[i],
                                                   mttr_list[i],
                                                   mttf_list[i]))
        return (recovery_methods, 0)


    def StartToAnalysis(self, h_mttf, h_dd, h_down, strategy, methods):
        h_up_0= float(h_mttf)
        h_detected = float(h_dd)
        h_down = float(h_down)
        if strategy ==0:
            my_sys = EscalatedSystem()
        if strategy == 1:
            my_sys = System()
        (r_list, variance) =self.getRecoverMethods(methods, strategy)
        my_sys.parameter_initialization(h_up_0, h_detected , h_down,r_list)
        my_sys.option_initialization("Low","Balanced","Diagnosis","Equal","Unchanged")
        my_sys.set_variance(variance)
        observableSys = ModelDecorator(my_sys)
        observerView = ViewDecorator(self.view, observableSys)
        observerView.registModel()
        observableSys.calculate()

class ModelDecorator:
    def __init__(self, system):
        self.model = system
        self.observers = []

    def calculate(self):
        info = self.model.optimal_recovery_sequence()
        results = self.model.CollectResults()
        self.notifyObserver(results)

    def RegisterResults(self, observer):
        self.observers.append(observer)

    def notifyObserver(self,results):
        for observer in self.observers:
            observer.update(results)

class ViewDecorator:
    def __init__(self, view, model):
        self.observer = view
        self.model = model

    def registModel(self):
        self.model.RegisterResults(self.observer)

    def update(self,results):
        self.observer.update(results)


if __name__ == "__main__":
    controller = Controller()