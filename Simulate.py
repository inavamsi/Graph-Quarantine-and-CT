import random
import copy
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

class Simulate():
	def __init__(self,graph_obj,agents):
		self.graph_obj=graph_obj
		self.agents=agents
		self.state_list={}
		self.state_history={}
		self.quarantine_list=[]
		self.quarantine_history=[]

		for state in ['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']:
			self.state_list[state]=[]
			self.state_history[state]=[]

		for agent in self.agents:
			self.state_list[agent.state].append(agent.index)

		self.update()

	def simulate_day(self,q_degree,error_CT,quarantine_time, trace_delay):
		self.quarantine_list=[]
		for state in self.state_list.keys():
			self.state_list[state]=list(set(self.state_list[state]))
		self.quarantine(q_degree,error_CT,quarantine_time, trace_delay)
		self.spread(q_degree)
		self.update()

		#print(self.state_history['Symptomatic'])
		#print(self.quarantine_history)
		#print('')

	def simulate_days(self,days,q_degree,error_CT,quarantine_time, trace_delay):
		for i in range(days):
			#print(q_degree,"   ",i)
			self.simulate_day(q_degree,error_CT,quarantine_time, trace_delay)

	def quarantine(self,q_degree,error_CT,quarantine_time, trace_delay):

		if q_degree<=0:
			return

		for agent in self.agents:
			if agent.quarantine_state!=None:
				agent.quarantine_state+=1

			if agent.state=='Symptomatic':
				if agent.quarantine_state==None:
					agent.quarantine_state=0
					agent.qdegree=1
				agent.quarantined=True
				self.quarantine_list.append(agent.index)

			else:
				if agent.quarantine_state==None:
					agent.quarantined=False
				else:
					if agent.quarantine_state>=quarantine_time:
						agent.quarantine_state=None
						agent.qdegree=None
						agent.quarantined=False
					else :
						agent.quarantined=True
						self.quarantine_list.append(agent.index)


		for agent in self.agents:
			if agent.qdegree!=None:
				if agent.qdegree<q_degree and agent.quarantine_state==trace_delay:
					for contact_indx in self.graph_obj.adj_list[agent.index]:
						c_agent=self.agents[contact_indx]
						if random.random()>error_CT:
							if c_agent.quarantine_state==None:
								c_agent.quarantine_state=0
								c_agent.qdegree=agent.qdegree+1


	def spread(self,q_degree):

		def p_fn(my_agent,neighbour_agents,p_inf_symp,p_inf_asymp):
			p_not_inf=1
			for nbr_agent in neighbour_agents:
				if nbr_agent.state=='Symptomatic' and not nbr_agent.quarantined and not my_agent.quarantined:
					p_not_inf*=(1-p_inf_symp)
				if nbr_agent.state=='Asymptomatic' and not nbr_agent.quarantined and not my_agent.quarantined:
					p_not_inf*=(1-p_inf_asymp)
			return 1 - p_not_inf


		def exposed_fn():
			return np.random.gamma(1.63,2) # https://bmjopen.bmj.com/content/10/8/e039652

		def asymp_fn():
			return random.randint(6,10) # https://bmjopen.bmj.com/content/10/8/e039856

		def symp_fn():
			return max(8,int(np.random.normal(13,3))) #https://bmjopen.bmj.com/content/10/8/e039856

		def none_fn():
			return None

		state_change={}
		p_symp=0.1
		p_asymp=0.08
		state_change['Susceptible']={'next states':['Exposed'],'schedule': none_fn}
		#
		state_change['Exposed']={'next states':['Symptomatic','Symptomatic','Symptomatic','Symptomatic','Symptomatic','Symptomatic','Symptomatic','Asymptomatic','Asymptomatic','Asymptomatic'],'schedule': exposed_fn} # 30% Asymptomatic https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249090
		state_change['Symptomatic']={'next states':['Recovered'],'schedule': symp_fn}
		state_change['Asymptomatic']={'next states':['Recovered'],'schedule': asymp_fn}
		state_change['Recovered']={'next states':['Recovered'],'schedule': none_fn}

		for agent in self.agents:
			agent.new_day()
			if agent.state in ['Exposed','Asymptomatic','Symptomatic']:
				if agent.schedule_time_left<=0:
					new_state=random.choice(state_change[agent.state]['next states'])
					schedule=state_change[new_state]['schedule']()
					self.convert_state(agent,new_state,schedule)

					#if new_state=='Symptomatic' and agent.state=='Symptomatic' and q_degree>0:
					#	self.quarantine_list.append(agent.index)


		#Asy,Sy : Sus ->2bExp
		for agent_indx in self.state_list['Susceptible']:
			agent=self.agents[agent_indx]
			p_inf=p_fn(agent,agent.neighbours,p_symp,p_asymp)
			if random.random()<p_inf:
				schedule=state_change['Exposed']['schedule']()
				self.convert_state(agent,'Exposed',schedule)

	def update(self):
		for state in self.state_history.keys():
			self.state_history[state].append(len(set(self.state_list[state])))
		self.quarantine_history.append(len(set(self.quarantine_list)))


	def convert_state(self,agent,new_state,schedule):
		self.state_list[agent.state].remove(agent.index)
		agent.state=new_state
		agent.schedule_time_left=schedule
		self.state_list[agent.state].append(agent.index)

	def plot(self):
		for state in self.state_history.keys():
			plt.plot(self.state_history[state])
		plt.plot(self.quarantine_history)

		plt.title('SEYAR and quarantined plot')
		plt.legend(list(self.state_history.keys())+['Quarantined'],loc='upper right', shadow=True)
		plt.show()
