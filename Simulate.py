import random
import copy
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

class Simulate():
	def __init__(self,graph_obj,agents,transmission_probability):
		self.graph_obj=graph_obj
		self.agents=agents
		self.transmission_probability=transmission_probability
		self.state_list={}
		self.state_history={}
		self.quarantine_list=[]
		self.quarantine_history=[]

		for state in transmission_probability.keys():
			self.state_list[state]=[]
			self.state_history[state]=[]


		for agent in self.agents:
			self.state_list[agent.state].append(agent.index)

		self.update()

	def simulate_day(self,q_degree,error_CT):
		#print(self.state_history['Exposed'])
		self.quarantine(q_degree,error_CT)
		self.spread()
		self.update()

	def simulate_days(self,days,q_degree,error_CT):
		for i in range(days):
			self.simulate_day(q_degree,error_CT)

	def quarantine(self,q_degree,error_CT):
		self.quarantine_list=[]
		for agent in self.agents:
			agent.quarantined=False
			agent.done_CT=False

		if q_degree<=0:
			return 

		self.quarantine_list = copy.deepcopy(self.state_list['Symptomatic'])

		for i in range(q_degree-1):
			temp_qlist=copy.deepcopy(self.quarantine_list)
			for indx in self.quarantine_list:
				if self.agents[indx].done_CT:
					continue 
				for contact_indx in self.graph_obj.adj_list[indx]:
					if random.random()>error_CT:
						temp_qlist.append(contact_indx)
				self.agents[indx].done_CT=True
			self.quarantine_list=list(set(temp_qlist))

		for indx in self.quarantine_list:
			self.agents[indx].quarantined=True


	def spread(self):
		#Asy,Sy : Sus ->2bExp
		to_beExposed=[]
		for agent_indx in self.state_list['Susceptible']:
			agent=self.agents[agent_indx]
			p_inf=self.transmission_probability['Susceptible']['Exposed'](agent,agent.neighbours)
			if random.random()<p_inf:
				to_beExposed.append(agent_indx)
		# Asy,Sy ->Rec
		for agent_indx in self.state_list['Symptomatic']:
			agent=self.agents[agent_indx]
			p=self.transmission_probability['Symptomatic']['Recovered'](agent,agent.neighbours)
			self.convert_state(agent,'Recovered',p)
		for agent_indx in self.state_list['Asymptomatic']:
			agent=self.agents[agent_indx]
			p=self.transmission_probability['Asymptomatic']['Recovered'](agent,agent.neighbours)
			self.convert_state(agent,'Recovered',p)  
		# Exp -> Asy, Sy
		for agent_indx in self.state_list['Exposed']:
			agent=self.agents[agent_indx]
			p1=self.transmission_probability['Exposed']['Symptomatic'](agent,agent.neighbours)
			p2=self.transmission_probability['Exposed']['Asymptomatic'](agent,agent.neighbours)
			r=random.random()
			if r<p1:
				self.convert_state(agent,'Symptomatic',p1)
			elif r<p1+p2:
				self.convert_state(agent,'Asymptomatic',p2)

		#2bExp->Exp
		for agent_indx in to_beExposed:
			agent=self.agents[agent_indx]
			self.convert_state(agent,'Exposed',1)


	def update(self):
		for state in self.state_history.keys():
			self.state_history[state].append(len(self.state_list[state]))
		self.quarantine_history.append(len(self.quarantine_list))

	def convert_state(self,agent,new_state,p):
		if random.random()<p:
			self.state_list[agent.state].remove(agent.index)
			agent.state=new_state
			self.state_list[agent.state].append(agent.index)

	def plot(self):
		for state in self.state_history.keys():
			plt.plot(self.state_history[state])
		plt.plot(self.quarantine_history)

		plt.title('SEYAR and quarantined plot')
		plt.legend(list(self.state_history.keys())+['Quarantined'],loc='upper right', shadow=True)
		plt.show()