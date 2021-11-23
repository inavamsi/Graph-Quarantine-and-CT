import random
import copy
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import Agent
import Graph
import Simulate
import streamlit as st

pgf=False
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

def streamlit_ui():
    st.write("""
    # Efficacy of Contact Tracing for Covid-19
    Finding the optimal sweet spot for contact tracing in a region.
    """)
    st.write("For any queries please email ibe214@nyu.edu")
    st.write("------------------------------------------------------------------------------------")

    st.sidebar.write("World parameters")
    seed=int(st.sidebar.text_input("Enter random seed value", value='42'))
    random.seed(seed)
    graph_choice=st.sidebar.selectbox('Select Graph type', ['G(n,p) Random graph', 'Grid','Country:Afghanistan','Country:Netherland'])

    if graph_choice=='Grid':
    	n=st.sidebar.slider("Value of 'n' for nxn grid", min_value=5 , max_value=50 , value=30 , step=5)
    	p=None
    	days=st.sidebar.slider("Number of days in simulation", min_value=10 , max_value=300 , value=100 , step=10 , format=None , key=None )
    	num_worlds=st.sidebar.slider("Number of times to average simulations over", min_value=1 , max_value=100 , value=50 , step=1 , format=None , key=None )

    else:
    	n=st.sidebar.slider("Number of agents", min_value=250 , max_value=10000 , value=500 , step=250)
    	p=st.sidebar.slider("Probability(p) of an edge in G(n,p) random graph", min_value=0.0 , max_value=1.0 , value=0.26 , step=0.01 , format=None , key=None )
    	p_range=st.sidebar.checkbox("Divide p by 10",value=True)
    	if p_range:
    		p/=10
    	p = float(int(p*1000))/1000
    	days=st.sidebar.slider("Number of days in simulation", min_value=10 , max_value=300 , value=100 , step=10 , format=None , key=None )
    	num_worlds=st.sidebar.slider("Number of times to average simulations over", min_value=1 , max_value=100 , value=1 , step=1 , format=None , key=None )


    st.sidebar.write("Averaging simulation "+str(num_worlds)+" times over graph G("+str(n)+","+str(p)+") for "+str(days)+" days.")

    st.sidebar.write("--------------")
    st.sidebar.write("Contact Tracing parameters")
    error_CT=st.sidebar.slider("Error proportion in identifying contacts", min_value=0.0 , max_value=1.0 , value=0.0 , step=0.01 , format=None , key=None )
    max_degree=st.sidebar.slider("Degree range", min_value=0 , max_value=10 , value=3 , step=1 , format=None , key=None )
    qdegree_list=[]
    for i in range(max_degree+1):
    	qdegree_list.append(i)

    st.sidebar.write("--------------")

    st.sidebar.write("Policy parameters")
    num_exp=st.sidebar.slider("Starting exposed proportion", min_value=0.0 , max_value=1.0 , value=0.01 , step=0.01 , format=None , key=None )
    trace_delay=st.sidebar.slider("Delay in subsequent tracing", min_value=0 , max_value=5 , value=1 , step=1 , format=None , key=None )
    quarantine_time=st.sidebar.slider("Duration of Quarantine", min_value=0 , max_value=20 , value=14 , step=1 , format=None , key=None )

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

    st.pyplot(fig)

    st.write("------------------------------------------------------------------------------------")

    if pgf:
        #st.pyplot(fig2)
        if name1!=None:
            plt.savefig(name1+'.pgf')

    st.header("Cost function")
    st.write("Goal is to minimise Cost function where each of the following attributes contribute respective cost.")
    st.write("Cost function = a(Cumulative Symptomatic) + b(Cumulative Asymptomatic) + c(Cumulative Quarantine)")

    a=st.slider("Cost per unit time of Symptomatic infection",value=13)
    b=st.slider("Cost per unit time of Asymptomatic infection",value=5)
    c=st.slider("Cost per unit time of Quarantine",value=1)

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

    st.pyplot(fig2)

    st.write("------------------------------------------------------------------------------------")

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

streamlit_ui()

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
