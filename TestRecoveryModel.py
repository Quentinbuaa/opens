from RecoveryModel import *
import math

class TestFactory:
    def __init__(self, N_list):
        self.original_time_to_failure = 43200.0
        self.h_up = self.original_time_to_failure
        self.time_to_diagnosis = 5.0
        self.time_to_repair = 1440.0
        self.max_esrecovery_list = []
        self.N_list = N_list
        self.system_list=[]

    def GenerateSystems(self):
        self.coverage_options=["Balanced","Hierarchical"]
        self.system_complexity=["Low","Medium","High"]
        self.enter_probability_setup=["Escalated"]
        self.time_to_recovery_options=["Similar","Hierarchical"]
        self.time_to_failure_after_recovery_options=["Unchanged","Reconfigured"]


        for system_complexity in self.system_complexity:
            base_coverage = self.get_base_coverage(system_complexity)
            for coverage_op in self.coverage_options:
                coverage_list = self.get_coverage_list(coverage_op,base_coverage)
                for time_to_recover_op in self.time_to_recovery_options:
                    time_to_recover_list = self.get_time_to_recovery_list(time_to_recover_op )
                    for time_to_failure_after_recovery_op in self.time_to_failure_after_recovery_options:
                        time_to_failure_after_recovery_list = self.get_time_to_failure_after_recovery_list(time_to_failure_after_recovery_op)
                        for enter_probability_op in self.enter_probability_setup:
                            probability_list= self.get_probability_list(enter_probability_op,
                                                                        coverage_list)
                            test_recovery_list = self.get_test_recovery_list(coverage_list,probability_list,time_to_recover_list,time_to_failure_after_recovery_list)
                            system_to_test = self.get_system_to_test(enter_probability_op)
                            system_to_test.parameter_initialization(self.original_time_to_failure,
                                                                    self.time_to_diagnosis,
                                                                    self.time_to_repair,test_recovery_list)
                            system_to_test.option_initialization(system_complexity,coverage_op,enter_probability_op,time_to_recover_op,
                                                                 time_to_failure_after_recovery_op)
                            #system_to_test.set_variance(np.std(coverage_list))
                            self.system_list.append(system_to_test)


    """There are three types of system complexity. 
    and here is the mapping:
    {Low:0.05,Medium:0.2,High:0.5}"""
    def get_base_coverage(self,system_complexity):
        coverage_dict = {"Low":0.05,"Medium":0.2,"High":0.5}
        return coverage_dict[system_complexity]

    """There are three types of coverage relation or option. 
    Make sure the largest coverage is not larger than 1"""
    def get_coverage_list(self, coverage_op, base_coverage):
        coverage_list = [base_coverage]
        if coverage_op =="Balanced":
            coverage_list+=[base_coverage]*(self.N-1)
        elif coverage_op == "Hierarchical":
            for i in range(self.N-1):
                coverage_list.append(base_coverage + (i+1)*((0.6*base_coverage)/(self.N-1))) #New version
        elif coverage_op == "Exclusive":
            coverage_list += [0.01*base_coverage]*(self.N-1)
        else:
            pass
        return coverage_list

    """There are two type of options,
    for escalated, return [1,0,...],
    for diagnosis, return weighted probability"""
    def get_probability_list(self,enter_probability_op , coverage_list):
        if enter_probability_op =="Escalated":
            return [1]+[0]*(self.N-1)
        elif enter_probability_op=="Diagnosis":
            sum_sum = sum(coverage_list)
            return list(map(lambda x: x/sum_sum, coverage_list))
        else:
            return []

    """There are two types of time to recovery relation,
    for Equal, return [base_h_i,....],
    for Hierarchical, return weighted"""
    def get_time_to_recovery_list(self, time_to_recover_op):
        base_h_i = 1.0
        high_h_i = 600.0
        if time_to_recover_op == "Similar":
            return [30.0]*self.N
        elif time_to_recover_op == "Hierarchical":
            h_i_list = [base_h_i]
            for i in range(self.N-1):
                h_i_list.append((high_h_i/(self.N-1))*(i+1))
            return h_i_list
        else:
            return []

    """There are two types of relation,
    if reconfigured, the time to failure after satisfy a linear increase with coefficient of 2"""
    def get_time_to_failure_after_recovery_list(self, time_to_recover_op):
        base_h_up = self.h_up
        if time_to_recover_op == "Unchanged":
            return [base_h_up]*self.N
        elif time_to_recover_op == "Reconfigured":
            h_up_list = [base_h_up]
            for i in range(self.N-1):
                h_up_list.append(1.5*(i+1)*base_h_up)
            #print(h_up_list)
            return h_up_list
        else:
            return []

    """Then, we can generate the recovery list"""
    def get_test_recovery_list(self,coverage_list,probability_list,time_to_recover_list,time_to_failure_after_recovery_list):
        recovery_name_list = ["rr" + str(i+1) for i in range(self.N)]
        recovery_list = []
        for i in range(self.N):
            recovery_list.append(RecoveryMethod(recovery_name_list[i], coverage_list[i],
                                                probability_list[i], time_to_recover_list[i], time_to_failure_after_recovery_list[i]))
        return recovery_list

    """Generate the system to test"""
    def get_system_to_test(self, enter_probability_op):
        if enter_probability_op=="Escalated":
            return EscalatedSystem()
        if enter_probability_op =="Diagnosis":
            return System()

    def RunExperiments(self):
        for N in self.N_list:
            self.N = N
            self.GenerateSystems()
            for i in range(len(self.system_list)):
                info = str(i+1)
                info +="\t"
                info += self.system_list[i].optimal_recovery_sequence()
                print(info)
            self.system_list = []

if __name__=="__main__":
    N_list =[3, 5, 7]
    exp = TestFactory(N_list)
    exp.RunExperiments()
