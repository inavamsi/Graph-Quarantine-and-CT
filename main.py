import random
import copy
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import Agent
import Graph
import Simulate

def main(exp_per,days,qdegree,graph_obj,error_CT,disease_paramters):
	
	beta_sy,beta_asy,mu_sy,mu_asy,gamma_sy,gamma_asy,delta=disease_paramters

	agents=[]
	for i in range(graph_obj.size):
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
	transmission_prob['Susceptible']['Exposed']= p_infection(beta_sy,beta_asy)
	transmission_prob['Exposed']['Symptomatic']= p_standard(mu_sy)
	transmission_prob['Exposed']['Asymptomatic']= p_standard(mu_asy)
	transmission_prob['Symptomatic']['Recovered']= p_standard(gamma_sy)
	transmission_prob['Asymptomatic']['Recovered']= p_standard(gamma_asy)
	transmission_prob['Recovered']['Susceptible']= p_standard(delta)

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

def histogram():
	st.write("""
	# Efficacy of Contact Tracing
	Finding the optimal sweet spot for contact tracing in a region.
	""")
	st.write("For any queries please email ibe214@nyu.edu")
	st.write("------------------------------------------------------------------------------------")

	st.sidebar.write("World parameters")
	graph_choice=st.sidebar.selectbox('Select Graph type', ['G(n,p) Random graph', 'Grid'])
	if graph_choice=='G(n,p) Random graph':
		n=st.sidebar.slider("Number of agents", min_value=250 , max_value=3000 , value=1000 , step=250)
		p=st.sidebar.slider("Probability(p) of an edge in G(n,p) random graph", min_value=0.0 , max_value=1.0 , value=0.26 , step=0.01 , format=None , key=None )
		p_range=st.sidebar.checkbox("Divide p by 10",value=True)
		if p_range:
			p/=10
		days=st.sidebar.slider("Number of days in simulation", min_value=1 , max_value=300 , value=100 , step=1 , format=None , key=None )
		num_worlds=st.sidebar.slider("Number of times to average simulations over", min_value=1 , max_value=100 , value=3 , step=1 , format=None , key=None )
	
	elif graph_choice=='Grid':
		n=st.sidebar.slider("Value of 'n' for nxn grid", min_value=5 , max_value=50 , value=30 , step=5)
		p=-1
		days=st.sidebar.slider("Number of days in simulation", min_value=1 , max_value=300 , value=100 , step=1 , format=None , key=None )
		num_worlds=st.sidebar.slider("Number of times to average simulations over", min_value=1 , max_value=100 , value=50 , step=1 , format=None , key=None )

	st.sidebar.write("Averaging simulation "+str(num_worlds)+" times over graph G("+str(n)+","+str(p)+") for "+str(days)+" days.")
	
	st.sidebar.write("--------------")
	st.sidebar.write("Contact Tracing parameters")
	error_CT=st.sidebar.slider("Error proportion in identifying contacts", min_value=0.0 , max_value=1.0 , value=0.0 , step=0.01 , format=None , key=None )
	max_degree=st.sidebar.slider("Degree range", min_value=0 , max_value=10 , value=4 , step=1 , format=None , key=None )
	qdegree_list=[]
	for i in range(max_degree+1):
		qdegree_list.append(i)

	st.sidebar.write("--------------")

	st.sidebar.write("Disease parameters")
	num_exp=st.sidebar.slider("Starting exposed proportion", min_value=0.0 , max_value=1.0 , value=0.01 , step=0.01 , format=None , key=None )
	beta_sy=st.sidebar.slider("Rate of infection due to Symptomatic : Susceptible->Exposed", min_value=0.0 , max_value=1.0 , value=0.3 , step=0.01 , format=None , key=None )
	beta_asy=st.sidebar.slider("Rate of infection due to Asymptomatic : Susceptible->Exposed", min_value=0.0 , max_value=1.0 , value=0.3 , step=0.01 , format=None , key=None )
	
	if p==-1:
		mu_sy=st.sidebar.slider("Rate of Exposed->Symptomatic", min_value=0.0 , max_value=1.0 , value=0.1 , step=0.01 , format=None , key=None )
		mu_asy=st.sidebar.slider("Rate of Exposed->Asymptomatic", min_value=0.0 , max_value=1.0 , value=0.25 , step=0.01 , format=None , key=None )
	else:
		mu_sy=st.sidebar.slider("Rate of Exposed->Symptomatic", min_value=0.0 , max_value=1.0 , value=0.3 , step=0.01 , format=None , key=None )
		mu_asy=st.sidebar.slider("Rate of Exposed->Asymptomatic", min_value=0.0 , max_value=1.0 , value=0.3 , step=0.01 , format=None , key=None )
	gamma_sy=st.sidebar.slider("Rate of recovery : Symptomatic:->Recovered", min_value=0.0 , max_value=1.0 , value=0.1 , step=0.01 , format=None , key=None )
	gamma_asy=st.sidebar.slider("Rate of recovery : Asymptomatic:->Recovered", min_value=0.0 , max_value=1.0 , value=0.1 , step=0.01 , format=None , key=None )
	delta=st.sidebar.slider("Rate of unimmunisation : Recovered->Susceptible", min_value=0.0 , max_value=1.0 , value=0.0 , step=0.01 , format=None , key=None )
	disease_paramters=beta_sy,beta_asy,mu_sy,mu_asy,gamma_sy,gamma_asy,delta
	st.sidebar.write("--------------")
	individual_types=['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']
	hdict={}
	for s in individual_types:
		hdict[s]=[0]*len(qdegree_list)
	hdict['Quarantined']=[0]*len(qdegree_list)
	for qdegree in qdegree_list:
		for i in range(num_worlds):
			if p==-1:
				graph_obj=Graph.Grid(n)
			else:
				graph_obj = Graph.RandomGraph(n,p,True)
			sdict,qlist = main(num_exp,days,qdegree,graph_obj,error_CT,disease_paramters)
			for state in sdict.keys():
				for j in range(len(sdict[state])):
					hdict[state][qdegree]+=sdict[state][j]
			for k in range(len(qlist)):
				hdict['Quarantined'][qdegree]+=qlist[k]

	for qdegree in qdegree_list:
		for key in hdict.keys():
			hdict[key][qdegree]/=num_worlds

	labels=qdegree_list
	x = np.arange(len(labels))  # the label locations
	width = 0.2  # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(x-width, hdict['Symptomatic'], width, label='Symptomatic')
	rects2 = ax.bar(x, hdict['Asymptomatic'], width, label='Asymptomatic')
	rects4 = ax.bar(x+width, hdict['Quarantined'], width, label='Quarantined')

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Cumulative Hours')
	ax.set_xlabel('Quarantine degree')
	if p==-1:
		ax.set_title('Effects of different degrees of quarantine on '+str(n)+'x'+str(n)+' grid')
	else:
		ax.set_title('Effects of different degrees of quarantine on G('+str(n)+','+str(p)+')')
	ax.set_xticks(x)
	ax.set_xticklabels(labels)
	ax.legend()

	fig.tight_layout()

	st.pyplot(fig)

	st.write("------------------------------------------------------------------------------------")

	st.header("Cost function")
	st.write("Goal is to minimise Cost function where each of the following attributes contribute respective cost.")
	st.write("Cost function = a(Cumulative Symptomatic) + b(Cumulative Asymptomatic) + c(Cumulative Quarantine)")

	a=st.slider("Cost per unit time of Symptomatic infection",value=13)
	b=st.slider("Cost per unit time of Asymptomatic infection",value=5)
	c=st.slider("Cost per unit time of Quarantine",value=1)

	st.write("For better results please change(on the left) the number of times to average the simulation over.")
	cost_list=[]
	for i in range(len(hdict['Symptomatic'])):
		cost=a*hdict['Symptomatic'][i]+b*hdict['Asymptomatic'][i]+c*hdict['Quarantined'][i]
		cost_list.append(cost)

	fig2, ax2 = plt.subplots()
	rects = ax2.bar(x, cost_list, width)

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax2.set_ylabel('Cost')
	ax2.set_xlabel('Quarantine degree')
	if p==-1:
		ax2.set_title('Costs of different degrees of quarantine on '+str(n)+'x'+str(n)+' grid')
	else:
		ax2.set_title('Costs of different degrees of quarantine on G('+str(n)+','+str(p)+')')
	ax2.set_xticks(x)
	ax2.set_xticklabels(labels)

	fig2.tight_layout()

	st.pyplot(fig2)



#Histogram of cumulative hours(yaxis) vs qdegree(x axis)
histogram()


