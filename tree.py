from treelib import Node, Tree
from model_classes import config, country, site, patient
from datetime import datetime, timedelta, date
#tree resources
    #https://treelib.readthedocs.io/en/latest/
    #https://medium.com/swlh/making-data-trees-in-python-3a3ceb050cfd

class model: 
    #future 
        #3+3, arms, seasonality
            #3+3
                #array of [#patients, stop period]
                    #when reach #patient apply stop
                #trigger stop timer in congfig/iteration?
            #config groups
                #could consider config group, to combine configs to give max_patients, i.e 1 group per arm
            #config
                # consider adding treatment period, screening period to config for cohorts
            #country
                #max_patients per country
            #patients
                #actual patients are projected to enrol and complete?
                #PFS,OS
            #output
                #table with interation, config, country, site, patient, screned, enrolled, complete
        #option to use beta-pert?
        #multithreading for interations
        # add option to __add__ models to combine trees?
    def __init__(self, config_objs, num_iterations = 1, screening_period = 0, treatment_period = 0):
        self.config_objs = config_objs
        self.num_iterations = num_iterations
        self.screening_period = screening_period
        self.treatment_period = treatment_period
        self.tree = Tree()
    def generate_model(self):
        #root node
        for a in ['model']:
            id_0 = a
            self.tree.create_node(
                a, 
                id_0
                )
            #iterations
            for n in [str(i) for i in range(self.num_iterations)]: 
                id_1 = n
                self.tree.create_node(
                    n, 
                    id_1, 
                    id_0, 
                    data= None
                    )
                
                #configs        
                for config_obj in config_objs:
                    for config_dict, config_key in [[config_obj.setup_dict[config_key], config_key] for config_key in config_obj.setup_dict]:
                        id_2 = '/'.join([id_1, config_key])
                        self.tree.create_node(
                            config_key, 
                            id_2, 
                            parent= id_1,
                            data= config(config_obj.setup_dict, config_obj.max_patients, config_obj.current_timestep)
                            )
                        
                        #countries
                        for country_info, country_dict, country_key in [[config_dict[country_key][0], config_dict[country_key][1], country_key] for country_key in config_dict]:
                            id_3 = '/'.join([id_2, country_key])
                            num_sites, screen_rate_low, screen_rate_med, screen_rate_high, setup_time_low, setup_time_med, setup_time_high, screen_fail_rate, drop_out_rate = country_info
                            self.tree.create_node(
                                country_key, 
                                id_3, 
                                parent= id_2, 
                                data=country(num_sites, screen_rate_low, screen_rate_med, screen_rate_high, setup_time_low, setup_time_med, setup_time_high, screen_fail_rate, drop_out_rate)
                                )
                            generated_sites = 0

                            #sites
                            for site_info, site_dict, site_key in [[country_dict[site_key][0], country_dict[site_key][1], site_key] for site_key in country_dict]:
                                id_4 = '/'.join([id_3, site_key])
                                screen_rate, setup_time  = site_info
                                if site_key.find('__') != 0: 
                                    self.tree.create_node(
                                        site_key, 
                                        id_4, 
                                        parent= id_3, 
                                        data=site(setup_time, screen_rate)
                                        )  
                                    generated_sites += 1
                                
                                #patients       #screening_period, treatment_period, screen_fail_rate, drop_out_rate, screen_dt, enrol_dt, complete_dt
                                for patient_dict, patient_key in [[site_dict[patient_key], patient_key] for patient_key in site_dict]:
                                    id_5 = '/'.join([id_4, patient_key])
                                    if patient_key.find('__') != 0: 
                                        screen_dt, enrol_dt, complete_dt = patient_dict
                                        self.tree.create_node(
                                            patient_key, 
                                            id_5, 
                                            parent= id_4, 
                                            data=patient(self.screening_period, self.treatment_period, screen_fail_rate, drop_out_rate, screen_dt, enrol_dt, complete_dt)
                                            )  
                                        if enrol_dt != None: config_obj.patients_enrolled += 1
                           
                            #other sites
                            for s in range(num_sites - generated_sites):
                                id_4 = '/'.join([id_3, str(s)])
                                country_node = self.tree.get_node(id_3)
                                sr = country_node.data.triangular_screen_rate()
                                st = country_node.data.triangular_setup_time()
                                st = st if st > config_obj.current_timestep else config_obj.current_timestep
                                self.tree.create_node(
                                    str(s), 
                                    id_4, 
                                    parent= id_3, 
                                    data=site(st, sr)
                                    )  
    def show_model(self, iteration=0):
        if iteration == -1: 
            self.tree.show()
        else:
            self.sub_tree = self.tree.subtree(str(iteration)) #need exception for if seletion if > num interations
            self.sub_tree.show()
    
    @staticmethod
    def simulate(model_obj, start_dt, max_timestep = 1000):
        start_dt = datetime.strptime(start_dt,'%d-%m-%Y')
        for timestep in range(max_timestep):
            for iteration_node in model_obj.tree.children('model'):
                for config_node in model_obj.tree.children(iteration_node.identifier):
                    if config_node.data.current_timestep > timestep: continue
                    if config_node.data.enrolment_complete: continue # if reached max patient
                    for country_node in model_obj.tree.children(config_node.identifier):
                        for site_node in model_obj.tree.children(country_node.identifier):
                            if site_node.data.setup_time > timestep: continue
                            site_node.data.screen_patient_buffer += site_node.data.screen_rate
                            if site_node.data.screen_patient_buffer >= 1:
                                for i in range(int(site_node.data.screen_patient_buffer)):
                                    patient_id = '/'.join([site_node.identifier, str(config_node.data.patients_enrolled)])
                                    model_obj.tree.create_node(
                                        str(config_node.data.patients_enrolled), 
                                        patient_id,
                                        parent= site_node.identifier, 
                                        data= patient.from_timestep(
                                            timestep,
                                            start_dt,
                                            model_obj.screening_period,
                                            model_obj.treatment_period,
                                            country_node.data.screen_fail_rate, 
                                            country_node.data.drop_out_rate
                                            ) 
                                    )
                                    patient_node = model_obj.tree.get_node(patient_id)
                                    if patient_node.data.enrolled_dt != None: 
                                        config_node.data.patients_enrolled += 1
                                    if config_node.data.patients_enrolled >= config_node.data.max_patients: 
                                        config_node.data.enrolment_complete = True
                                        config_node.data.max_patient_dt = date.strftime(start_dt + timedelta(days= timestep),'%d-%m-%Y')
                                        break
                            site_node.data.screen_patient_buffer = site_node.data.screen_patient_buffer%1    
        #return #list of config_objs to get max_patient dates


# #Test DataSepc
s_dict1 = {'projection_test': 
            {'UK': [[4, 0.1, 0.4, 0.6, 10, 40, 110, 0, 0], #num_sites, screen_rate_low, screen_rate_med, screen_rate_high, setup_time_low, setup_time_med, setup_time_high, screen_fail_rate, drop_out_rate]
                {'__': [[None, None], # screen_rate, setup_time
                    {'__': [None, None, None]}] # screen_dt, enrol_dt, complete_dt
                }], 
            'AUS': [[1, 0.1, 0.4, 0.6, 10, 40, 110, 0, 0],
                {'__': [[None, None],
                    {'__': [None, None, None]}]}]
            }}
s_dict2 = {'reprojection_test': 
            {'UK': [[4, 0.1, 0.4, 0.6, 10, 40, 110, 0, 0], 
                {'101': [[0.2, 32], 
                    {'John Smith': ['02-07-2020', '05-07-2020', '20-07-2020']
                    ,'Paul Smith': ['25-07-2020', None, None]
                    ,'Katy Madden': ['21-07-2020', '25-07-2020', None]}]
                ,'102': [[0.1, 42], 
                    {'__': [None, None, None]}]
                }], 
            'AUS': [[1, 0.1, 0.4, 0.6, 10, 40, 110, 0, 0],
                {'__': [[None, None],
                    {'__': [None, None, None]}]}]
            }}
s_dict3 = {'easy_test':
            {'UK': [[3, 3.6, 3.7, 1, 1, 1, 1, 0, 0],
                {'__': [[None, None], 
                    {'__': [None, None, None]}]
                }], 
            }}

#initialize
#config_objs = [config(s_dict1,max_patients= 50), config(s_dict2, max_patients= 50, current_timestep = 150)] # should config class have patients_enrolled?
#config_objs = [config(s_dict2, max_patients= 10, current_timestep = 100)]
config_objs = [config(s_dict3, max_patients= 40)]
model1 = model(config_objs, num_iterations = 50, screening_period = 2, treatment_period = 3)   
model1.generate_model()
model.simulate(model1, start_dt = '21-05-2020', max_timestep = 1500)   
#model1.show_model(0)    # -1 to show all, otherwise select specific iteration subtree

er_list = []
for iteration_node in model1.tree.children('model'):
    for config_node in model1.tree.children(iteration_node.identifier):
        print(config_node.data.max_patient_dt)
        er_list.append(config_node.data.max_patient_dt)

## Need to improve output and check enrolment output look rights
    ## NEED DATES PER CONFIG AND PLOT SEPERATELY
## apply graphing output 
## GRAPHS LOOK FRONT LOADED ARE TRIGULAR FUCNTION APPLYING CORRECTLY?

