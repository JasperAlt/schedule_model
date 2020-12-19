from model import *
from math import floor, ceil

DAYS = 7
HOURS = 6
WEEK = DAYS * HOURS
AGENTS = 120
CALENDAR = Calendar(DAYS,HOURS)

model = SchedModel(CALENDAR)

model.compartments({
            # Name          Susceptibilities   Evolution
            "S"     :(      [("I", "I", 0.03)], None                         ),  # First state taken as start
            "I"     :(      [],                ("R", floor(WEEK * 1.5))       ),
            "R"     :(      [],                ("S", floor(WEEK * 2))       ),
        })

model.activity_list({
            # Name              Capacity    Transmission
            "rest1"     :(      3,          0.9     ),
            "bus"       :(      20,         0.25    ),
            "work1"     :(      60,         0.02    ),
            "rest2"     :(      3,          0.9     ),
            "car"       :(      2,          0.5     ),
            "work2"     :(      40,         0.01    ),
            "leisure"   :(      5,          0.2     ),
            "weekend"   :(      25,         0.01    ),

    })

model.populate({
            # Name          Default activity    Number
            "class1"    :(  "rest1",            AGENTS // 2     ),
            "class2"    :(  "rest2",            AGENTS // 2     ),
    })

"""
model.constrain([
                # Class     Activity    Days                    Hours
            (   "class1",  "rest1",     range(DAYS-2),          0               ),  # Weekday constraints
            (   "class2",  "rest2",     range(DAYS-2),          0               ),
            (   "class1",  "bus",       range(DAYS-2),          1               ),
            (   "class2",  "car",       range(DAYS-2),          1               ),
            (   "class1",  "work1",     range(DAYS-2),          2               ),
            (   "class2",  "work2",     range(DAYS-2),          2               ),
            (   "class1",  "bus",       range(DAYS-2),          3               ),
            (   "class2",  "car",       range(DAYS-2),          3               ),
            (   "class1",  "leisure",   range(DAYS-2),          4               ),
            (   "class2",  "leisure",   range(DAYS-2),          4               ),
            (   "class1",  "rest1",     range(DAYS-2),          5               ),
            (   "class2",  "rest2",     range(DAYS-2),          5               ),
            (   "class1",  "rest1",     range(DAYS-2, DAYS),    range(0,3)      ),  # Weekends
            (   "class2",  "rest2",     range(DAYS-2, DAYS),    range(0,3)      ),
            (   "class1",  "weekend",   range(DAYS-2, DAYS),    range(3,HOURS)  ),
            (   "class2",  "weekend",   range(DAYS-2, DAYS),    range(3,HOURS)  ),
    ])
"""

model.constrain([
                # Class     Activity    Days                    Hours
            (   "class1",  "rest1",     range(DAYS-3),          0               ),  # Weekday constraints
            (   "class2",  "rest2",     range(DAYS-3),          0               ),
            (   "class1",  "bus",       range(DAYS-3),          1               ),
            (   "class2",  "car",       range(DAYS-3),          1               ),
            (   "class1",  "work1",     range(DAYS-3),          2               ),
            (   "class2",  "work2",     range(DAYS-3),          2               ),
            (   "class1",  "bus",       range(DAYS-3),          3               ),
            (   "class2",  "car",       range(DAYS-3),          3               ),
            (   "class1",  "leisure",   range(DAYS-3),          4               ),
            (   "class2",  "leisure",   range(DAYS-3),          4               ),
            (   "class1",  "rest1",     range(DAYS-3),          5               ),
            (   "class2",  "rest2",     range(DAYS-3),          5               ),
            (   "class1",  "rest1",     range(DAYS-3, DAYS),    range(0,3)      ),  # Weekends
            (   "class2",  "rest2",     range(DAYS-3, DAYS),    range(0,3)      ),
            (   "class1",  "weekend",   range(DAYS-3, DAYS),    range(3,HOURS)  ),
            (   "class2",  "weekend",   range(DAYS-3, DAYS),    range(3,HOURS)  ),
    ])

"""
model.constrain([
                # Class     Activity    Days                    Hours
            (   "class1",  "rest1",     range(DAYS),          0               ),  # Weekday constraints
            (   "class2",  "rest2",     range(DAYS),          0               ),
            (   "class1",  "bus",       range(DAYS),          1               ),
            (   "class2",  "car",       range(DAYS),          1               ),
            (   "class1",  "work1",     range(DAYS),          2               ),
            (   "class2",  "work2",     range(DAYS),          2               ),
            (   "class1",  "bus",       range(DAYS),          3               ),
            (   "class2",  "car",       range(DAYS),          3               ),
            (   "class1",  "leisure",   range(DAYS),          4               ),
            (   "class2",  "leisure",   range(DAYS),          4               ),
            (   "class1",  "rest1",     range(DAYS),          5               ),
            (   "class2",  "rest2",     range(DAYS),          5               ),
    ])
"""

model.sched()
model.infect(ceil(AGENTS * 0.02), "I")

for i in range(DAYS * HOURS * 100): model.step()

model.state_plot()
