#import matplotlib.pylab as py
import itertools
import re
from math import factorial
#import numpy as np


class RecoveryMethod:
    def __init__(self, name, coverage_p, probability, mttr_h_1, mttf_h_up):
        self.name= name               # Index of the recovery method
        self.probability = probability # The enter proability
        self.coverage_p = coverage_p  # Coverage probability
        self.mttr_h_1 = mttr_h_1  # Mean time to recovery of "name" recovery
        self.mttf_h_up = mttf_h_up  # Mean time to failure after recovery

    def get_coverage(self):
        return self.coverage_p
    def get_probability(self):
        return self.probability

    def get_h_i(self):
        return self.mttr_h_1

    def get_h_up_i(self):
        return self.mttf_h_up

    def get_name(self):
        return self.name

    def get_latex_name(self):
        m = re.search('([a-zA-Z]+)\s*(\d+)', self.name)
        prefix = m.group(1)
        index = m.group(2)
        latex_name = prefix+"^{("+index+")}"
        return latex_name


    def display(self):
        #print(self.name)
        info = "{0}, {1}, {2}, {3}, {4}\n".format(self.name,self.coverage_p, self.probability,
                                                self.mttr_h_1, self.mttf_h_up)
        return info

class Results:
    def __init__(self):
        self.availability =""
        self.op_sequence = ""
        self.probability_vector = ""
        self.sys_mttf = ""
        self.sys_mttr = ""
        self.std_variance = ""

class System:
    def __init__(self):
        self.max_recovery = 0
        self.mini_recovery =0
        self.h_up_0 = 0
        self.mttf_diagnosis = 0
        self.h_down = 0
        self.recovery_list = []
        self.N=0
        self.system_complexity_op = ""
        self.coverage_op = ""
        self.enter_probability_op =""
        self.time_to_recover_op = ""
        self.time_to_failure_op = ""
        self.print_option = "Latex"
        self.results = Results()

    def parameter_initialization(self, original_time_to_failure, time_to_diagnosis,time_to_repair,
                                 candidate_recovery_list):
        self.h_up_0 = original_time_to_failure
        self.mttf_diagnosis = time_to_diagnosis
        self.h_down = time_to_repair
        self.recovery_list = candidate_recovery_list
        self.N = len(candidate_recovery_list)

    def option_initialization(self, system_complexity_op, coverage_op, enter_probability_op, time_to_recover_op, time_to_failure_op):
        self.system_complexity_op = system_complexity_op
        self.coverage_op =coverage_op
        self.enter_probability_op = enter_probability_op
        self.time_to_recover_op = time_to_recover_op
        self.time_to_failure_op = time_to_failure_op

    def set_variance(self, var):
        self.variance = var

    def information_matrix(self):
        info ="{5}\t{0}\t{1}\t{3}\t{4}\t{2}\t".format(self.coverage_op,
                                          self.system_complexity_op,
                                          self.enter_probability_op,
                                          self.time_to_recover_op,
                                          self.time_to_failure_op,
                                                 self.N)
        info += self.print_recovery_sequence(self.print_option)
        info += str(self.max_recovery)
        info += "\t"+str(self.variance)
        return info

    """There are two options
        "Latex": Output with equations, which is for latex expression.
        "Word": Which is better for human reading and research with. """
    def print_recovery_sequence(self, option):
        info = ""
        if option == "Word":
            for i in range(self.N):
                info +=self.recovery_list[i].get_name()
                if not i == (self.N-1):
                    info+="->"
                else:
                    info +="\t"
        # example $Rr^{(1)}\to Rr^{(2)}\to Rr^{(3)}$
        elif option == "Latex":
            info += r"$\langle "
            for i in range(self.N):
                info += self.recovery_list[i].get_latex_name()
                if not i == (self.N-1):
                    info += r",\,"
                else:
                    info +=r"\rangle$"+"\t"
        return info

    def recovery_setup(self,recovery_list):
        self.recovery_list = recovery_list

    def print_current_recovery_list(self):
        #for recovery in self.recovery_list:
        #    print(recovery.display())
        info = self.information_matrix()
        return info

    def optimal_recovery_sequence(self):
        possible_sequences = list(itertools.permutations(self.recovery_list))
        max = 0
        max_index = 0
        mini = 1.0
        sum = 0.0
        for index in range(len(possible_sequences)):
            self.recovery_setup(list(possible_sequences[index]))
            self.calculate_availability()
            sum += self.availability
            if self.availability > max:
                max = self.availability
                max_index = index
            if self.availability < mini:
                mini = self.availability
        self.recovery_setup(list(possible_sequences[max_index]))
        self.max_recovery = max
        self.mini_recovery = mini
        self.average = sum/float(factorial(self.N))
        #print("Max: {0}".format(max))
        op_sequence = self.print_current_recovery_list()
        return op_sequence

    def CollectResults(self):
        self.results.op_sequence = self.print_recovery_sequence("Word")
        self.results.availability = str(self.max_recovery)
        self.results.probability_vector = str(self.get_probability_vector())
        self.results.sys_mttf = str(self.all_mttf)
        self.results.sys_mttr = str(self.all_mttr)
        self.results.std_variance = str(self.variance)
        return self.results

    def get_probability_vector(self):
        result = []
        for i in range(self.N):
            result.append(self.recovery_list[i].get_probability())
        return result

    def get_syn_probability(self,i):
        syn_probability = 0.0
        for j in range(i):
            #temp_p_j = self.allocate_p_vector[j]
            temp_p_j = self.recovery_list[j].get_probability()
            if not temp_p_j == 0.0:
                weight = 1.0
                for k in range(j, i):
                    weight *= (1.0 - self.recovery_list[k].get_coverage())
                temp_p_j *= weight
                syn_probability += temp_p_j
        return syn_probability

    def get_weighted_h(self):
        sum = 0.0
        for i in range(self.N):
            sum += self.recovery_list[i].get_h_i() * self.recovery_list[i].get_probability()
        return sum

    def get_weighted_hup(self):
        sum = 0.0
        for i in range(self.N):
            sum += self.recovery_list[i].get_h_up_i() * self.recovery_list[i].get_probability() * self.recovery_list[i].get_coverage()
        return sum

    def calculate_mttr(self):
        sum = self.mttf_diagnosis                                 #h_detected
        sum += self.get_weighted_h()
        for i in range(1, self.N):
            sum += self.recovery_list[i].get_h_i() * self.get_syn_probability(i)
        sum += self.h_down*self.get_syn_probability(self.N)
        self.all_mttr = sum
        #print("The MTTR is: {0}".format(sum))

    def calculate_mttf(self):
        sum = 0.0
        sum += self.h_up_0 *self.get_syn_probability(self.N)
        sum += self.get_weighted_hup()
        for i in range(1, self.N):
            sum += self.recovery_list[i].get_h_up_i() * self.recovery_list[i].get_coverage() * self.get_syn_probability(i)
        self.all_mttf = sum
        #print("The MTTF is: {0}".format(sum))

    def calculate_availability(self):
        self.calculate_mttr()
        self.calculate_mttf()
        self.availability = 1.0/(1.0+ self.all_mttr/self.all_mttf)
        #self.print_current_recovery_list()
        #print("The availability is: {0}".format(self.availability))

class EscalatedSystem(System):
    def __init__(self):
        super(EscalatedSystem, self).__init__()

    def parameter_initialization(self, original_time_to_failure, time_to_diagnosis,time_to_repair,
                                 candidate_recovery_list):
        self.h_up_0 = original_time_to_failure
        self.mttf_diagnosis = time_to_diagnosis
        self.h_down = time_to_repair
        self.recovery_list = candidate_recovery_list
        self.N = len(candidate_recovery_list)
        self.set_probability_vector()

    def information_matrix(self):
        info ="{5}\t{0}\t{1}\t{3}\t{4}\t{2}\t".format(self.coverage_op,
                                                      self.system_complexity_op,
                                                      self.enter_probability_op,
                                                      self.time_to_recover_op,
                                                      self.time_to_failure_op,
                                                      self.N)
        info += self.print_recovery_sequence(self.print_option)
        info += str(self.max_recovery)
        info += "\t"+str(self.mini_recovery)
        info += "\t"+str(((self.max_recovery-self.mini_recovery)/self.mini_recovery)*100)
        info += "\t"+str(self.average)
        info += "\t"+str(((self.max_recovery-self.average)/self.average)*100)
        return info

    def set_probability_vector(self):
        self.allocate_p_vector = [0]*self.N    # The allocation probability for each type of recovery method.
        self.allocate_p_vector[0]=1

    def get_weighted_h(self):
        sum = 0.0
        for i in range(self.N):
            sum += self.recovery_list[i].get_h_i() * self.allocate_p_vector[i]
        return sum

    def get_weighted_hup(self):
        sum = 0.0
        for i in range(self.N):
            sum += self.recovery_list[i].get_h_up_i() * self.allocate_p_vector[i] * self.recovery_list[i].get_coverage()
        return sum

    def get_probability_vector(self):
        return self.allocate_p_vector

    def get_syn_probability(self,i):
        syn_probability = 0.0
        for j in range(i):
            temp_p_j = self.allocate_p_vector[j]
            if not temp_p_j == 0.0:
                weight = 1.0
                for k in range(j, i):
                    weight *= (1.0 - self.recovery_list[k].get_coverage())
                temp_p_j *= weight
                syn_probability += temp_p_j
        return syn_probability

if __name__ == "__main__":
    r1 = RecoveryMethod("Rr 1", 0.1, 0.2, 1.0, 1000.0)
    r2 = RecoveryMethod("Rr 2", 0.1, 0.2, 1.0, 2000.0)
    r3 = RecoveryMethod("Rr 3", 0.1, 0.2, 1.0, 1000.0)
    r4 = RecoveryMethod("Rr 4", 0.1, 0.2, 1.0, 1000.0)
    r5 = RecoveryMethod("Rr 5", 0.1, 0.2, 1.0, 1000.0)
    r_list = [r1, r2, r3, r4, r5]
    h_up_0= 43200.0
    h_detected = 5.0
    h_down = 1440.0
    my_sys = System()
    my_sys.parameter_initialization(h_up_0, h_detected , h_down,r_list)
    my_sys.option_initialization("Low","Balanced","Diagnosis","Equal","Unchanged")
    my_sys.set_variance(0)
    info = my_sys.optimal_recovery_sequence()
    print(info)

    es_sys = EscalatedSystem()
    es_sys.parameter_initialization(h_up_0, h_detected , h_down,r_list)
    es_sys.option_initialization("Low","Balanced","Escalated","Equal","Unchanged")
    es_sys.set_variance(0)
    info = es_sys.optimal_recovery_sequence()
    print(info)