# import pandas
# import numpy
import random
from datetime import datetime, timedelta, date

class config:
    def __init__(self, setup_dict, max_patients, current_timestep = 0):
        self.setup_dict = setup_dict
        self.current_timestep = current_timestep
        self.max_patients = max_patients
        self.patients_enrolled = 0
        self.enrolment_complete = False
        self.max_patient_dt = None

class country:
    def __init__(self, num_sites, screen_rate_low, screen_rate_med, screen_rate_high, setup_time_low, setup_time_med, setup_time_high, screen_fail_rate = 0, drop_out_rate = 0):
        self.num_sites = num_sites
        self.screen_rate_low = screen_rate_low
        self.screen_rate_med = screen_rate_med
        self.screen_rate_high = screen_rate_high
        self.setup_time_low = setup_time_low
        self.setup_time_med = setup_time_med
        self.setup_time_high = setup_time_high
        self.screen_fail_rate = screen_fail_rate
        self.drop_out_rate = drop_out_rate
    def triangular_setup_time(self):
        return int(random.triangular(self.setup_time_low, self.setup_time_high, self.setup_time_med))
    def triangular_screen_rate(self):
        return round(random.triangular(self.screen_rate_low, self.screen_rate_high, self.screen_rate_med),3)

class site:
    def __init__(self, setup_time, screen_rate):
        self.setup_time = setup_time
        self.screen_rate = screen_rate / 30.416 # monthly to daily
        self.screen_patient_buffer = 0
    
class patient:
    def __init__(self, screening_period = 0, treatment_period = 0, screen_fail_rate = 0, drop_out_rate = 0, screened_dt = None, enrolled_dt = None, completed_dt = None):
        self.screening_period = screening_period 
        self.treatment_period = treatment_period 
        self.screen_fail_rate = screen_fail_rate
        self.drop_out_rate = drop_out_rate
        self.screened_dt = datetime.strptime(screened_dt,'%d-%m-%Y')
        self.enrolled_dt = None
        self.completed_dt = None
        if random.random() > self.screen_fail_rate:
            self.enrolled_dt = datetime.strptime(enrolled_dt,'%d-%m-%Y') if enrolled_dt != None else self.screened_dt + timedelta(self.screening_period)
            if random.random() > self.drop_out_rate:
                self.completed_dt = datetime.strptime(completed_dt,'%d-%m-%Y') if completed_dt != None else timedelta(self.treatment_period)
    @classmethod
    def from_timestep(cls, timestep, start_dt, screening_period= 0, treatment_period = 0, screen_fail_rate = 0, drop_out_rate = 0):
        return cls(screening_period, treatment_period, screen_fail_rate, drop_out_rate, datetime.strftime(start_dt + timedelta(days= timestep),'%d-%m-%Y'))
