import random
import copy
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import Agent
import Graph
import Simulate

def main(n,p,exp_per,days,qdegree,graph_obj):
	#print("Average degree : ",graph_obj.average_degree)
	agents=[]
	for i in range(n):
		state='Susceptible'
		if random.random()<exp_per:
			state='Exposed'
		agent=Agent.Agent(state,i)
		agents.append(agent)

	#create graph of agents from graph_obj
	for indx,agent in enumerate(agents):
		agent.index=indx
		for j in graph_obj.adj_list[indx]:
			agent.neighbours.append(agents[j])

	individual_types=['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']

	def p_infection(p1,p2):  # probability of infectiong neighbour
		def p_fn(my_agent,neighbour_agents):
			p_inf_symp=p1
			p_inf_asymp=p2
			p_not_inf=1
			for nbr_agent in neighbour_agents:
				if nbr_agent.state=='Symptomatic' and not nbr_agent.quarantined and not my_agent.quarantined:
					p_not_inf*=(1-p_inf_symp)
				if nbr_agent.state=='Asymptomatic' and not nbr_agent.quarantined and not my_agent.quarantined:
					p_not_inf*=(1-p_inf_asymp)
			return 1 - p_not_inf
		return p_fn


	def p_standard(p):
		def p_fn(my_agent,neighbour_agents):
			return p
		return p_fn

	transmission_prob={}
	for t in individual_types:
		transmission_prob[t]={}

	for t1 in individual_types:
		for t2 in individual_types:
			transmission_prob[t1][t2]=p_standard(0)
	transmission_prob['Susceptible']['Exposed']= p_infection(0.3,0.3)
	transmission_prob['Exposed']['Symptomatic']= p_standard(0.15)
	transmission_prob['Exposed']['Asymptomatic']= p_standard(0.2)
	transmission_prob['Symptomatic']['Recovered']= p_standard(0.1)
	transmission_prob['Asymptomatic']['Recovered']= p_standard(0.1)
	transmission_prob['Recovered']['Susceptible']= p_standard(0)

	sim_obj=Simulate.Simulate(graph_obj,agents,transmission_prob)
	sim_obj.simulate_days(days,qdegree)
	return sim_obj.state_history,sim_obj.quarantine_history
	#sim_obj.plot()



def average(tdict,number):
	for k in tdict.keys():
		l=tdict[k]
		for i in range(len(l)):
			tdict[k][i]/=number

	return tdict

def worlds(number,qdegree):
	n=10000
	p=0.0003
	num_exp=0.01
	days=100
	individual_types=['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']
	tdict={}
	for state in individual_types:
		tdict[state]=[0]*(days+1)
	tdict['Quarantined']=[0]*(days+1)

	for i in range(number):
		#graph_obj = Graph.RandomGraph(n,p,True)
		graph_obj = Graph.StratifiedGraph(n,[0.1,0.3,0.6,1],[0.02,0.008,0.003,0.002],True)
		sdict,qlist = main(n,p,num_exp,days,qdegree,graph_obj)
		for state in individual_types:
			for j in range(len(tdict[state])):
				tdict[state][j]+=sdict[state][j]
		for k in range(len(tdict['Quarantined'])):
			tdict['Quarantined'][k]+=qlist[k]

	tdict=average(tdict,number)

	for state in tdict.keys():
		plt.plot(tdict[state])

	plt.title('Averaged SEYAR with quarantine degree '+str(qdegree))
	plt.legend(list(tdict.keys()),loc='upper right', shadow=True)
	plt.show()

def histogram():
	n=1000
	p=0.005
	num_exp=0.01
	days=300
	qdegree_list=[0,1,2,3]
	individual_types=['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']
	hdict={}
	for s in individual_types:
		hdict[s]=[0]*len(qdegree_list)
	hdict['Quarantined']=[0]*len(qdegree_list)
	for qdegree in qdegree_list:
		for i in range(5):
			graph_obj = Graph.RandomGraph(n,p,True)
			sdict,qlist = main(n,p,num_exp,days,qdegree,graph_obj)
			for state in sdict.keys():
				for j in range(len(sdict[state])):
					hdict[state][qdegree]+=sdict[state][j]
			for k in range(len(qlist)):
				hdict[state][qdegree]+=qlist[k]

	labels=qdegree_list
	x = np.arange(len(labels))  # the label locations
	width = 0.2  # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(x-2*width, hdict['Symptomatic'], width, label='Symptomatic')
	rects2 = ax.bar(x-width, hdict['Asymptomatic'], width, label='Asymptomatic')
	#rects3 = ax.bar(x, hdict['Susceptible'], width, label='Susceptible')
	#rects4 = ax.bar(x+width, hdict['Quarantined'], width, label='Quarantined')
	#rects3 = ax.bar(x + width, distanced_hours_list, width, label='Distanced')

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Cumulative Hours')
	ax.set_xlabel('Quarantine degree')
	ax.set_title('Effects of different degrees of quarantine during contact tracing')
	ax.set_xticks(x)
	ax.set_xticklabels(labels)
	ax.legend()

	def autolabel(rects):
	    """Attach a text label above each bar in *rects*, displaying its height."""
	    '''for rect in rects:
	        height = rect.get_height()
	        ax.annotate('{}'.format(height),
	                    xy=(rect.get_x() + rect.get_width() / 2, height),
	                    xytext=(0, 3),  # 3 points vertical offset
	                    textcoords="offset points",
	                    ha='center', va='bottom')
      '''
	autolabel(rects1)
	autolabel(rects2)
	#autolabel(rects3)
	#autolabel(rects4)

	fig.tight_layout()

	plt.show()


worlds(1,1)
#Histogram of cumulative hours(yaxis) vs qdegree(x axis)
#histogram()