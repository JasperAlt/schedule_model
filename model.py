from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from math import ceil
import time
import random
import matplotlib.pyplot as plt


class State():
    # State objects are part of the compartment model

    def __init__(self, s_id, transitions=[], evolution=None):
        # transitions is a list of tuples (a,b)
        # where exposure to an agent in state a transitions this agent to state b
        # evolution is one tuple (c, t)
        # where duration t elapsing causes the agent to transition to state c

        self.id = s_id
        self.transitions = transitions
        self.evolution = evolution


class Contagion():
    # Compartment model:
    # a collection of states, which have transitions

    def __init__(self,states):
        self.states = states


class Calendar():
    # Slice time into two nested cycles

    def __init__(self, DAYS=7, HOURS=3):
        self.days = DAYS
        self.hours = HOURS


class Log():
    # Object for agents to log activity

    def __init__(self, model):
        self.entries = []
        self.model = model

    def add(self, text):
        self.entries += [(self.model.steps, text)]

    def dump(self):
        for entry in entries:
            print(entry)


class SchedAgent(Agent):
    # Main agent class

    def __init__(self, unique_id, model, kind, calendar, default):
        # default is the agent's default activity
        super().__init__(unique_id, model)
        self.site = -1
        self.kind = kind
        self.hours = calendar.hours
        self.days = calendar.days
        self.default = default
        self.calendar = [[default for hour in range(calendar.hours)] for day in range(calendar.days)]
        self.activities = set([])
        self.model = model
        self.neighbors = []
        self.log = Log(model)

        self.state = model.contagion.states[0]
        self.next_state = self.state
        self.last_change = 0

    def constrain(self, constraint):
        # This method places a constraint (obj; see below) on the agent's schedule

        if not self.calendar[constraint.day][constraint.hour] == self.default:
            raise ValueError("Conflicting constraints on agent " + str(self.unique_id) + " (" + self.kind + ")")
        act = self.model.activities[constraint.activity]
        self.calendar[constraint.day][constraint.hour] = act
        self.activities |= set([act])

    def show_activity(self):
        # display... 

        print("\nAgent " + str(self.unique_id) + " of kind " + self.kind)
        print("Activities (days across, hours down)")
        print("\t".join(["\t" + str(i) for i in range(self.days)]))
        for hour in range(self.hours):
            print(str(hour) + ": " + "\t".join([str(self.calendar[day][hour].label) for day in range(self.days)]))

    def show_site(self):
        # display... 

        print("\nAgent " + str(self.unique_id) + " of kind " + self.kind)
        print("Sites (days across, hours down)")
        print("\t".join(["\t" + str(i) for i in range(self.days)]))
        for hour in range(self.hours):
            print(str(hour) + ": " + "\t".join([str(self.calendar[day][hour]) for day in range(self.days)]))

    def step(self):
        # go to current scheduled location

        self.state = self.next_state
        self.next_state = self.state
        self.log.add("state: " + self.state.id)
        self.site = self.calendar[self.model.day][self.model.hour]
        self.site.current += [self]

    def advance(self):
        # progresses the contagion model (rename this function)

        neighbor_states = [agent.state.id for agent in self.site.current if agent is not self]
        if (self.state.evolution is not None):
            self.last_change += 1
            if self.last_change == self.state.evolution[1]:
                self.next_state = [state for state in self.model.contagion.states if state.id == self.state.evolution[0]][0]
        elif len(self.state.transitions) > 0:
            infected = False
            triggers = [u for (u,v,w) in self.state.transitions]
            for neighbor in self.site.current:
                if neighbor.state.id in triggers and random.random() < self.site.transmission:
                    T = [(t[0],t[1],t[2]) for t in self.state.transitions if t[0] == neighbor.state.id]
                    T = random.choice(T) # currently only supporting uniform random nondeterminism
                    if random.random() < T[2]:
                        self.next_state = [state for state in self.model.contagion.states if state.id == T[1]][0]
                        self.log.add("infection " + self.state.id + " --> " + self.next_state.id + " at " + self.site.activity.label + " site " + str(self.site.site_id))
                        self.last_change = 0



class Activity():
    # A thing every site has and every agent wants
    
    def __init__(self, label, capacity=2, transmission=0.5):
        self.label = label
        self.capacity = capacity
        self.occupancy = 0
        self.transmission= transmission
        self.current = []


class Site():
    # Has activities and agents
    
    def __init__(self, activity, site_id, capacity, occupied):
        self.activity = activity
        self.transmission = activity.transmission
        self.site_id = site_id
        self.capacity = capacity
        self.occupied = occupied
        self.current = []


class Constraint():
    # A simple constraint represents a hard requirement on agent schedules
    # For example, workers go to work during the day and home at night.
    # Unconstrained time are assigned to an agent's default activity

    def __init__(self, kind, activity, day, hour):
        self.agent = kind
        self.activity = activity
        self.day = day
        self.hour = hour


class Schedule():
    # not to be confused with the scheduler in Mesa
    # this is actually a schedule table

    def __init__(self, AGENTS, CLASSES, ACTIVITIES, CONSTRAINTS, CALENDAR):
        self.activities = ACTIVITIES
        self.agents = AGENTS
        self.constraints = CONSTRAINTS
        self.days = CALENDAR.days
        self.hours = CALENDAR.hours
        self.classes = CLASSES
        self.sites = []


    def show(self):
        # display...

        for day in range(self.days):
            for hour in range(self.hours):
                print("Site assignments at hour " + str(hour) + " of day " + str(day))
                for site in self.sites:
                    print("\tSite " + str(site.site_id) + " for activity " + site.activity.label)
                    for agent in self.agents:
                        if agent.calendar[day][hour] is site:
                            print("\t\tAgent " + str(agent.unique_id) + " of kind " + agent.kind)

    def show_occupancy(self, kind="all"):
        # display...

        if kind == "all":
            select = [agent for (key,agent) in self.agents.items()]
        else:
            select = [agent for (key, agent) in self.agents.items() if agent.kind == kind]
        for day in range(self.days):
            print("\n\n" + "".join(["----" for hour in range(self.hours)]) + "\tDAY\t" + str(day) + "\t" + "".join(["----" for hour in range(self.hours+1)]))
            print("\tSite occupancy by " + kind + " agents")
            print("\n\t\t\t" + "\t".join(["" for hour in range(self.hours // 2)]) + "Hour")
            print("\nAct.\tSite\t|\t" + "\t".join([str(hour) for hour in range(self.hours)]))
            print("".join(["--------" for hour in range(self.hours + 3)]))
            for key, act in self.activities.items():
                for site in self.sites:
                    if site.activity is act:
                        print(key + "\t" + str(site.site_id) + "\t|\t" + "\t".join([str(sum([1 for agent in select if agent.calendar[day][hour] is site])) for hour in range(self.hours)]))
                print("".join(["--------" for hour in range(self.hours + 3)]))


    def sched(self, world):
        # schedule everything 

        self.sites = []

        #print("\n\nACTIVITY ASSIGNMENT\n\n")

        for constraint in self.constraints:
            for agent in self.classes[constraint.agent]:
                # build class dict to speed this up
                agent.constrain(constraint)

        #print("\n\nSITE ASSIGNMENT\n\n")

        for key, act in self.activities.items():
            # Make room for the busiest times
            times = [(hour, day) for hour in range(self.hours) for day in range(self.days)]
            most = max([sum([(1 if agent.calendar[day][hour] is act else 0) for (key, agent) in self.agents.items()]) for (hour, day) in times])
            for i in range(ceil(most/act.capacity)): self.sites += [Site(act, i, act.capacity, 0)]

        for key, act in self.activities.items():
            # For each activity, each agent is assigned one preferred site
            candidates = set([site for site in self.sites if site.activity is act])
            for (key, agent) in self.agents.items():
                fave = None
                if(act in agent.activities and len(candidates) > 0):                    # If I do this activity
                    site = random.choice(list(candidates))                              # Pick a site
                    while fave is None and site.occupied >= site.capacity:              # While no space
                        if(site.occupied == site.capacity): candidates -= set([site])   # Remove candidate
                        site = random.choice(list(candidates))                          # Keep looking
                    fave = site                     # It's my space now
                    site.occupied += 1              # Less space for you

                    for day in range(self.days):                                        # Favored site chosen
                        for hour in range(self.hours):                                  # for *all* instances
                            if agent.calendar[day][hour] is act:                        # of this activity
                                agent.calendar[day][hour] = fave

        world.sites = self.sites # pass the sites off to this dumb object I should rethink


class World():
    # Contains all the sites
    # Synchronizes their cleanup
    # Maybe ought to do some logging later
    # Maybe ought to be removed

    def __init__(self):
        self.sites = []
        self.journal = []

    def clear_sites(self):
        for site in self.sites:
            site.current = []


class SchedModel(Model):
    # Overall model object
    # Loads data into objects as user requires
    # Top level controls for model

    def __init__(self, CALENDAR):
        self.activities = {}
        self.agents = []
        self.constraints = []
        self.calendar = CALENDAR
        self.days = CALENDAR.days
        self.hours = CALENDAR.hours
        self.classes = {}
        self.contagion = {}
    
        self.scheduler = SimultaneousActivation(self)
        self.world = World()

        self.day = 0
        self.hour = 0
        self.steps = 0

        self.log = []

    def compartments(self, states):
        # build a contagion object
        states = [State(name, infections, evolution) for name, (infections, evolution) in states.items()]
        #states = {(name, State(name, infections, evolution)) for name, (infections,evolution) in states.items()}
        # uncomment and debug
        self.contagion = Contagion(states)
        
    def activity(self, name, capacity, transmission):
        # add one activity
        self.activities[name] = Activity(name, capacity, transmission)

    def activity_list(self, acts):
        # add a list of activities
        for name, (capacity, transmission) in acts.items():
            self.activities[name] = Activity(name,capacity,transmission)

    def constrain(self, constraints):
        # take constraint list
        for (aclass, activity, days, hours) in constraints:
            print("Yo")
            if isinstance(days, range) and isinstance(hours,range):
                for day in days:
                    for hour in hours:  
                        self.constraints += [Constraint(aclass, activity, day, hour)]
            elif isinstance(days, range):
                for day in days:
                    self.constraints += [Constraint(aclass, activity, day, hours)]
            elif isinstance(hours, range):
                for hour in hours:
                    self.constraints += [Constraint(aclass, activity, days, hour)]
            else:
                self.constraints += [Constraint(aclass, activity, days, hours)]

        for constraint in self.constraints:
            print(constraint)

    def populate(self, classes):
        # Create agents
        self.agents = {}
        i = 0
        for name, (default, number) in classes.items():
            self.classes[name] = []
            # kind = (class_id, default activity, quantity)
            for j in range(i, i+number):
                a = SchedAgent(j, self, name, self.calendar, self.activities[default])
                self.agents[j] = a
                self.classes[name] += [a]
                self.scheduler.add(a)
            i = j


    def sched(self):
        self.schedule = Schedule(self.agents, self.classes, self.activities, self.constraints, self.calendar)
        self.schedule.sched(self.world)
        self.schedule.show_occupancy()
        #for kind in self.classes: self.schedule.show_occupancy(kind)

    def contagion_summary(self):
        # reporting function
        # log count of agents in each compartment

        states = []
        for agent in self.agents.values():
            states += [agent.state.id]
        counts = []
        for S in self.contagion.states:
            counts += [(S.id, sum([1 for state in states if state == S.id]))]
        self.log+=[counts]

    def report(self):
        # print state log
        for entry in self.log:
            print("".join([state + ":\t"+ str(quant) + "\t" for (state, quant) in entry]))

    def state_plot(self):
        # plot state counts over history
        series = {}
        for state in self.contagion.states:
            series[state.id] = []

        for entry in self.log:
            for (s, q) in entry:
                series[s] += [q]

        for state in self.contagion.states:
            plt.plot(series[state.id])

        plt.show()

    def infect(self, N, state_id):
        # choose an agent and set it to chosen state
        for i in range(N):
            a = random.choice(list(self.agents.values()))
            a.next_state = [state for state in self.contagion.states if state.id == state_id][0]

    def step(self):
        # step model forward
        #print("\nHOUR " + str(self.hour) + " OF DAY " + str(self.day) + " (STEP " + str(self.steps) + "):\n")
        self.contagion_summary()
        self.world.clear_sites()
        self.scheduler.step()
        self.hour += 1
        self.steps += 1
        if self.hour == self.hours:
            self.hour = 0
            self.day += 1
        if self.day == self.days:
            self.day = 0

