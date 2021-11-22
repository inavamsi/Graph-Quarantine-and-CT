import random
import copy
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import Agent
import Graph
import Simulate

pgf=True
if pgf:
    matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
    })

def main(exp_per,days,qdegree,graph_obj,error_CT,trace_delay,quarantine_time):
    agents=[]
    for i in range(graph_obj.size):
        state='Susceptible'
        schedule_time_left=0
        if random.random()<exp_per:
            state='Exposed'
            schedule_time_left=random.randint(0,3)
        agent=Agent.Agent(state,i,schedule_time_left)
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

    sim_obj=Simulate.Simulate(graph_obj,agents)
    sim_obj.simulate_days(days,qdegree,error_CT,quarantine_time,trace_delay)
    return sim_obj.state_history,sim_obj.quarantine_history
    #sim_obj.plot()


def average(tdict,number):
    for k in tdict.keys():
    	l=tdict[k]
    	for i in range(len(l)):
    		tdict[k][i]/=number

    return tdict

def histogram(error_CT,name2):
    seed=42
    random.seed(seed)
    graph_choice='G(n,p) Random graph'
    #['G(n,p) Random graph', 'Grid','Country:Afghanistan','Country:Netherland']

    n=2000
    p=0.008
    days=100
    num_worlds=10
    #error_CT=0
    max_degree=4
    num_exp=0.01
    trace_delay=1
    quarantine_time=14

    a=3
    b=2
    c=1
    name1='multibar_4'
    #name2=None

    qdegree_list=[]
    for i in range(max_degree+1):
        qdegree_list.append(i)

    individual_types=['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']
    hdict={}
    for s in individual_types:
    	hdict[s]=[0]*len(qdegree_list)
    hdict['Quarantined']=[0]*len(qdegree_list)
    for qdegree in qdegree_list:
        print("Running degree.. "+str(qdegree))
        for i in range(num_worlds):
        	if graph_choice=='Grid':
        		graph_obj=Graph.Grid(n)
        	elif graph_choice=='Country:Afghanistan':
        		graph_obj=Graph.FamilyGraph(n,p,[0,0.03,0.06,0.14,0.23,0.6,1],True)
        	elif graph_choice=='Country:Netherland':
        		graph_obj=Graph.FamilyGraph(n,p,[0.35,0.58,0.81,0.9,0.99,1],True)
        	elif graph_choice=='G(n,p) Random graph':
        		graph_obj = Graph.RandomGraph(n,p,True)
        	sdict,qlist = main(num_exp,days,qdegree,graph_obj,error_CT,trace_delay,quarantine_time)
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
    if graph_choice=='Grid':
    	ax.set_title('Effects of different degrees of quarantine on '+str(n)+'x'+str(n)+' grid')
    elif graph_choice=='G(n,p) Random graph':
    	ax.set_title('Effects of different degrees of quarantine on G('+str(n)+','+str(p)+')')
    elif graph_choice=='Country:Afghanistan':
    	ax.set_title('Effects of different degrees of quarantine on \n Afghanistan with underlying G('+str(n)+','+str(p)+')')
    elif graph_choice=='Country:Netherland':
    	ax.set_title('Effects of different degrees of quarantine on \n Netherland with underlying G('+str(n)+','+str(p)+')')

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()

    plt.show()
    print(hdict)

    if pgf:
        #st.pyplot(fig2)
        if name1!=None:
            plt.savefig(name1+'.pgf')

    cost_list=[]
    for i in range(len(hdict['Symptomatic'])):
    	cost=a*hdict['Symptomatic'][i]+b*hdict['Asymptomatic'][i]+c*hdict['Quarantined'][i]
    	cost_list.append(cost)

    fig2, ax2 = plt.subplots()
    rects = ax2.bar(x, cost_list, width)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax2.set_ylabel('Cost')
    ax2.set_xlabel('Quarantine degree')
    if graph_choice=='Grid':
    	ax.set_title('Cost of different degrees of quarantine on '+str(n)+'x'+str(n)+' grid')
    elif graph_choice=='G(n,p) Random graph':
    	ax.set_title('Cost of different degrees of quarantine on G('+str(n)+','+str(p)+') \n with ' +str(error_CT)+'% error in tracing')
    elif graph_choice=='Country:Afghanistan':
    	ax.set_title('Cost of different degrees of quarantine on \n Afghanistan with underlying G('+str(n)+','+str(p)+')')
    elif graph_choice=='Country:Netherland':
    	ax.set_title('Cost of different degrees of quarantine on \n Netherland with underlying G('+str(n)+','+str(p)+')')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)

    fig2.tight_layout()

    plt.show()

    if pgf:
        #st.pyplot(fig2)
        if name2!=None:
            plt.savefig(name2+'.pgf')

    print("Log")
    print("Random Seed value: "+str(seed))
    print("Graph type: "+graph_choice)
    print("Number of agents: "+str(n))
    print("Probability: "+str(p))
    print("Number of days: "+str(days))
    print("Number of worlds: "+str(num_worlds))
    print("Error in tracing: "+str(error_CT))
    print("Degree range: "+str(max_degree))
    print("Trace delay: "+str(trace_delay))
    print("quarantine_time: "+str(quarantine_time))
    print("Starting exposed proportion: "+str(num_exp))
    print("Cost per unit time of Symptomatic infection: "+str(a))
    print("Cost per unit time of Asymptomatic infection: "+str(b))
    print("Cost per unit time of Quarantine: "+str(c))

histogram(0,'error_0')
histogram(0.2,'error_20')
histogram(0.4,'error_40')

#Histogram of cumulative hours(yaxis) vs qdegree(x axis)
def hdict_qdegree(error_CT,trace_delay, quarantine_time):
    seed=42
    random.seed(seed)
    graph_choice='G(n,p) Random graph'
    #['G(n,p) Random graph', 'Grid','Country:Afghanistan','Country:Netherland']

    n=2000
    p=0.006
    days=100
    num_worlds=10
    num_exp=0.01

    name1='multibar_4'
    name2=None

    qdegree_list=[]
    for i in range(4):
        qdegree_list.append(i)

    individual_types=['Susceptible','Exposed','Asymptomatic','Symptomatic','Recovered']
    hdict={}
    for s in individual_types:
    	hdict[s]=[0]*len(qdegree_list)
    hdict['Quarantined']=[0]*len(qdegree_list)
    for qdegree in qdegree_list:
        print("Running degree.. "+str(qdegree))
        for i in range(num_worlds):
        	if graph_choice=='Grid':
        		graph_obj=Graph.Grid(n)
        	elif graph_choice=='Country:Afghanistan':
        		graph_obj=Graph.FamilyGraph(n,p,[0,0.03,0.06,0.14,0.23,0.6,1],True)
        	elif graph_choice=='Country:Netherland':
        		graph_obj=Graph.FamilyGraph(n,p,[0.35,0.58,0.81,0.9,0.99,1],True)
        	elif graph_choice=='G(n,p) Random graph':
        		graph_obj = Graph.RandomGraph(n,p,True)
        	sdict,qlist = main(num_exp,days,qdegree,graph_obj,error_CT,trace_delay,quarantine_time)
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

    return hdict


def plot_3d():
    error_list=[0,0.1,0.2,0.3,0.4,0.5]
    delay_list=[0,1,2,3]
    qtime_list=[12,14,16,18]
    dict_3d={}
    for error in error_list:
        dict_3d[error]={}
        for delay in delay_list:
            dict_3d[error][delay]={}
            for qtime in qtime_list:
                dict_3d[error][delay][qtime]=None

    for index,error in enumerate(error_list):
        print(index)
        for delay in delay_list:
            for qtime in qtime_list:
                dict_3d[error][delay][qtime]=hdict_qdegree(error, delay, qtime)

    print(dict_3d)
