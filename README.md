# Patient-Enrolment-Model
Python Project that models site initiation and patient enrolment into clinical trial using Tree Diagram.

The approach of this project is to use a tree diagram as a data structure to simulate a clinical trial. This method allows for reasonable level of complexity and flexibility. For example a additional node level could be added for treatment arms, allowing the same sites to enrol patients at differing enrolment rates if required. 

In this version of the model a node level was added for interation number for Monte Carlo simulations; triangular distribution was used to supply site start up times and enrolment rate. To get a monte carlo simulation we can just add a new parent node, 1 for each iteration.

There is a need to also have actual site and patient information flow into the model. I’ve setup the model to generate existing sites and patients, and then simulate remaining sites. To achieve this, I added another node level for configurations. Configurations give information regarding which countries, site and patients to be added, their enrolment rate, start-up times etc. In the next diagram I have two configurations one “projection_test” and one for “reprojection_test”. In the first I’ve not specified any sites or patients, and in the second I’ve added some sites and patients. 
model
├── 0
│   ├── projection_test         [0] #enrolment_offset
│   │   ├── AUS                 [2, 0.1, 0.2, 0.3, 30, 40, 60, 0, 0] #num_sites, screen_rate [low, med, high], setup_time [low, med, high], screen_fail_rate, drop_out_rate
│   │   │   ├── 1               [0.202, 53] #screen_rate, setup_time
│   │   │   └── 2               [0.123, 59]
│   │   └── UK                  [5, 0.1, 0.2, 0.3, 30, 40, 60, 0, 0]
│   │       ├── 1               [0.238, 44]
│   │       ├── 2               [0.213, 49]
│   │       └── 3               [0.14, 31]
│   └── reprojection_test       [50]
│       ├── AUS                 [2, 0.1, 0.2, 0.3, 30, 40, 60, 0, 0]
│       │   ├── 1               [0.206, 39]
│       │   └── 2               [0.193, 35]
│       └── UK                  [5, 0.1, 0.2, 0.3, 30, 40, 60, 0, 0]
│           ├── 101             [0.2, 32]
│           │   ├── John Smith  ['02-07-2020', '05-07-2020', '20-07-2020']
│           │   ├── Katy Madden ['21-07-2020', '25-07-2020', None]
│           │   └── Paul Smith  ['25-07-2020', None, None]
│           ├── 102             [0.1, 42]
│           └── 1               [0.19, 38]
└── 1
    ├── projection_test         [0]
    │   ├── AUS                 [2, 0.1, 0.2, 0.3, 30, 40, 60, 0, 0]
    │   │   ├── 1               [0.222, 35]
    │   │   └── 2               [0.124, 52]
    │   └── UK                  [5, 0.1, 0.2, 0.3, 30, 40, 60, 0, 0]
    │       ├── 1               [0.275, 44]
    │       ├── 2               [0.264, 36]
    │       └── 3               [0.201, 36]
    └── reprojection_test       [50]
        ├── AUS                 [2, 0.1, 0.2, 0.3, 30, 40, 60, 0, 0]
        │   ├── 1               [0.12, 45]
        │   └── 2               [0.145, 51]
        └── UK                  [5, 0.1, 0.2, 0.3, 30, 40, 60, 0, 0]
            ├── 101             [0.2, 32]
            │   ├── John Smith  ['02-07-2020', '05-07-2020', '20-07-2020']
            │   ├── Katy Madden ['21-07-2020', '25-07-2020', None]
            │   └── Paul Smith  ['25-07-2020', None, None]
            ├── 102             [0.1, 42]
            └── 1               [0.182, 40]
 
Once the model is generated, we apply a timestep to screen patients over time until we have reached the specified number of patients or reach a max timestep limit. We can take the dates and determine show a histogram, violin plot etc to show the spread and statistics of the outcomes. 
