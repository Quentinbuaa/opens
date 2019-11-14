import tkinter as tk  # for python 3
import pygubu
from Opens import *


class Application:
    def __init__(self, master, controller):

        #1: Create a builder
        self.builder = builder = pygubu.Builder()


        #2: Load an ui file
        builder.add_from_file('opens-gui.ui')

        #3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('Mainframe', master)

        self.controller = controller
        self.builder.connect_callbacks(self)
        self.listbox = self.builder.get_object('Listbox')


    def add_new_recovery_method(self):
        name_index = self.builder.tkvariables['name_index'].get()
        coverage = self.builder.tkvariables['coverage'].get()
        mean_time_to_recovery = self.builder.tkvariables['mttr'].get()
        mttf_after_recover = self.builder.tkvariables['mttf_after'].get()
        self.listbox.insert(0,self._tabify(name_index)+self._tabify(coverage)
                                                  +self._tabify(mean_time_to_recovery)
                                                  +self._tabify(mttf_after_recover))

    def _tabify(self, s, tabsize = 8):
        ln = ((len(s)/tabsize)+1)*tabsize
        return s.ljust(10)

    def get_results_display(self):
        h_up0= self.builder.tkvariables['mttf_origin'].get()
        h_dd= self.builder.tkvariables['h_dd'].get()
        h_down= self.builder.tkvariables['h_down'].get()
        strategy = 0
        methods = self.listbox.get(0, tk.END)
        self.controller.StartToAnalysis(h_up0, h_dd, h_down,strategy,methods)

    def update(self, results):
        self.builder.tkvariables['availability'].set(results.availability)
        self.builder.tkvariables['op_sequence'].set(results.op_sequence)
        self.builder.tkvariables['sys_mttf'].set(results.sys_mttf)
        self.builder.tkvariables['sys_mttr'].set(results.sys_mttr)

    def change_recovery_method(self):
        if not self.listbox.curselection() == "":
            recovery_method_info = self.listbox.get(self.listbox.curselection())
            current_selection_index = self.listbox.curselection()[0]
            self.listbox.delete(current_selection_index)
            tuples = recovery_method_info.split()
            if len(tuples) == 4:
                self.builder.tkvariables['name_index'].set(tuples[0])
                self.builder.tkvariables['coverage'].set(tuples[1])
                self.builder.tkvariables['mttr'].set(tuples[2])
                self.builder.tkvariables['mttf_after'].set(tuples[3])


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root,Controller())
    root.mainloop()