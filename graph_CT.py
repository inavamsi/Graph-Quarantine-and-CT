import random
import copy
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import Agent
import Graph
import Simulate

def main(n,p,exp_per,days,qdegree,graph_obj,error_CT):
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
	transmission_prob['Exposed']['Symptomatic']= p_standard(0.3)
	transmission_prob['Exposed']['Asymptomatic']= p_standard(0.3)
	transmission_prob['Symptomatic']['Recovered']= p_standard(0.1)
	transmission_prob['Asymptomatic']['Recovered']= p_standard(0.1)
	transmission_prob['Recovered']['Susceptible']= p_standard(0)

	sim_obj=Simulate.Simulate(graph_obj,agents,transmission_prob)
	sim_obj.simulate_days(days,qdegree,error_CT)
	return sim_obj.state_history,sim_obj.quarantine_history
	#sim_obj.plot()



def average(tdict,number):
	for k in tdict.keys():
		l=tdict[k]
		for i in range(len(l)):
			tdict[k][i]/=number

	return tdict

def worlds(number,qdegree):
	n=1000
	p=0.003
	num_exp=0.01
	days=300
	error_CT=0
	individual_types=['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']
	tdict={}
	for state in individual_types:
		tdict[state]=[0]*(days+1)
	tdict['Quarantined']=[0]*(days+1)

	for i in range(number):
		#graph_obj = Graph.RandomGraph(n,p,True)
		graph_obj = Graph.StratifiedGraph(n,[0.1,0.3,0.6,1],[0.02,0.008,0.003,0.002],True)
		sdict,qlist = main(n,p,num_exp,days,qdegree,graph_obj,error_CT)
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

#worlds(30,3)

def histogram(n,p):
	num_exp=0.01
	days=100
	error_CT=0.1
	qdegree_list=[0,1,2,3]
	worlds=3
	individual_types=['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']
	hdict={}
	for s in individual_types:
		hdict[s]=[0]*len(qdegree_list)
	hdict['Quarantined']=[0]*len(qdegree_list)
	for qdegree in qdegree_list:
		for i in range(worlds):
			graph_obj = Graph.RandomGraph(n,p,True)
			sdict,qlist = main(n,p,num_exp,days,qdegree,graph_obj,error_CT)
			for state in sdict.keys():
				for j in range(len(sdict[state])):
					hdict[state][qdegree]+=sdict[state][j]
			for k in range(len(qlist)):
				hdict['Quarantined'][qdegree]+=qlist[k]

	labels=qdegree_list
	x = np.arange(len(labels))  # the label locations
	width = 0.2  # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(x-2*width, hdict['Symptomatic'], width, label='Symptomatic')
	rects2 = ax.bar(x-width, hdict['Asymptomatic'], width, label='Asymptomatic')
	#rects3 = ax.bar(x, hdict['Susceptible'], width, label='Susceptible')
	rects4 = ax.bar(x, hdict['Quarantined'], width, label='Quarantined')
	#rects3 = ax.bar(x + width, distanced_hours_list, width, label='Distanced')

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Cumulative Hours')
	ax.set_xlabel('Quarantine degree')
	ax.set_title('Effects of different degrees of quarantine on G('+str(n)+','+str(p)+')')
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
	autolabel(rects4)

	fig.tight_layout()

	plt.show()

#Histogram of cumulative hours(yaxis) vs qdegree(x axis)
histogram(1000,0.003)

def country_histogram(p,country,family_sizes):
	n=1000
	num_exp=0.01
	days=300
	error_CT=0
	qdegree_list=[0,1,2,3]
	individual_types=['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']
	hdict={}
	for s in individual_types:
		hdict[s]=[0]*len(qdegree_list)
	hdict['Quarantined']=[0]*len(qdegree_list)
	for qdegree in qdegree_list:
		for i in range(20):
			graph_obj = Graph.FamilyGraph(n,p,family_sizes,True)
			sdict,qlist = main(n,p,num_exp,days,qdegree,graph_obj,error_CT)
			for state in sdict.keys():
				for j in range(len(sdict[state])):
					hdict[state][qdegree]+=sdict[state][j]
			for k in range(len(qlist)):
				hdict['Quarantined'][qdegree]+=qlist[k]

	labels=qdegree_list
	x = np.arange(len(labels))  # the label locations
	width = 0.2  # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(x-2*width, hdict['Symptomatic'], width, label='Symptomatic')
	rects2 = ax.bar(x-width, hdict['Asymptomatic'], width, label='Asymptomatic')
	#rects3 = ax.bar(x, hdict['Susceptible'], width, label='Susceptible')
	rects4 = ax.bar(x, hdict['Quarantined'], width, label='Quarantined')
	#rects3 = ax.bar(x + width, distanced_hours_list, width, label='Distanced')

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Cumulative Hours')
	ax.set_xlabel('Quarantine degree')
	ax.set_title('Country:'+country+', G(1000,'+str(p)+')')
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
	autolabel(rects4)

	fig.tight_layout()

	plt.show()

#country_histogram(0.005,'Nederland',[0.35,0.58,0.81,0.9,0.99,1])
#country_histogram(0.005,'Afghanistan',[0,0.03,0.06,0.14,0.23,0.6,1])


def optimal(p,cost_of_symptomatic,cost_of_quarantine):
	n=1000
	num_exp=0.01
	days=300
	error_CT=0
	qdegree_list=[0,1,2,3]
	individual_types=['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']
	hdict={}
	for s in individual_types:
		hdict[s]=[0]*len(qdegree_list)
	hdict['Quarantined']=[0]*len(qdegree_list)
	for qdegree in qdegree_list:
		for i in range(20):
			graph_obj = Graph.RandomGraph(n,p,True)
			sdict,qlist = main(n,p,num_exp,days,qdegree,graph_obj,error_CT)
			for state in sdict.keys():
				for j in range(len(sdict[state])):
					hdict[state][qdegree]+=sdict[state][j]
			for k in range(len(qlist)):
				hdict['Quarantined'][qdegree]+=qlist[k]

	opt_qdeg=0
	opt_value=cost_of_symptomatic*hdict['Symptomatic'][0]+cost_of_quarantine*hdict['Quarantined'][0]
	for i in qdegree_list:
		temp=cost_of_symptomatic*hdict['Symptomatic'][i]+cost_of_quarantine*hdict['Quarantined'][i]
		if temp<opt_value:
			opt_value=temp
			opt_qdeg=i 

	return opt_qdeg

def optimal_region(n,p):
	quarantine_cost_range=10
	symptomatic_cost_range=100
	qdegree_list=[0,1,2,3]
	color_list=['r','c','m','y']

	fig,ax=plt.subplots()

	for i in range(n):
		if i%10==9:
			print(i)
		q=random.randint(10,quarantine_cost_range*10)/10
		s=random.randint(1,symptomatic_cost_range)
		qdegree=optimal(p,s,q)
		ax.scatter(q,s,c=color_list[qdegree],s=20,alpha=0.8,edgecolors='none')

	ax.legend()
	ax.grid(True)
	plt.title('Optimal quarantine degree for G(1000,'+str(p)+')')
	plt.show()

#print region of optimal degree given costs for quarantine and symptomatic
def optimal_region2(p):
	quarantine_cost_range=10
	symptomatic_cost_range=100
	qdegree_list=[0,1,2,3]
	color_list=['r','c','m','y']

	fig,ax=plt.subplots()

	for i in range(10,20):
		print(i-10)
		for j in range(10,20):
			qdegree=optimal(p,i/10,j/10)
			ax.scatter(j/10,i/10,c=color_list[qdegree],s=20,alpha=0.8,edgecolors='none')

	ax.legend()
	ax.grid(True)
	plt.title('Optimal quarantine degree for G(1000,'+str(p)+')')
	plt.show()

#optimal_region(300,0.001)
#optimal_region2(0.001)
