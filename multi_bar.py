import matplotlib.pyplot as plt
import matplotlib
import numpy as np

pgf=True
name='multibar_4b'
title='Comparing costs on G(2000,0.02) graph \n with trace delay of 2 days'
if pgf:
    matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
    })

hdict={'Susceptible': [12649.3, 16129.6, 85793.1, 104682.2, 107806.3], 'Exposed': [7487.0, 7429.3, 5553.3, 4434.3, 4274.9], 'Asymptomatic': [4739.7, 4834.7, 3513.0, 2821.6, 2714.9], 'Symptomatic': [17701.3, 17516.9, 12911.4, 10504.2, 10170.3], 'Recovered': [159422.7, 156089.5, 94229.2, 79557.7, 77033.6], 'Quarantined': [0.0, 20309.8, 89035.7, 115795.6, 113558.3]}

costs=[(1,1,1),(1,2,3),(1,2,5),(1,1,5),(1,2,10)]

'''costs_dict={'Quarantine Cost':[],'Asymptomatic Cost':[],'Symptomatic Cost':[]}
for cost_st in costs:
    (c,b,a)=cost_st
    costs_dict['Quarantine Cost'].append(c)
    costs_dict['Asymptomatic Cost'].append(b)
    costs_dict['Symptomatic Cost'].append(a)'''


cost_list=[[],[],[],[],[]]

for i in range(len(hdict['Symptomatic'])):
    for index,cost_st in enumerate(costs):
        (c,b,a)=cost_st
        cost=a*hdict['Symptomatic'][i]+b*hdict['Asymptomatic'][i]+c*hdict['Quarantined'][i]
        cost_list[index].append(cost)

'''fig2, ax2 = plt.subplots()
rects = ax2.bar(x, cost_list, width)

# Add some text for labels, title and custom x-axis tick labels, etc.
ax2.set_ylabel('Cost')
ax2.set_xlabel('Quarantine degree')
ax2.set_title('Comparing different cost structure for a G(10000,0.001) ER graph')
ax2.set_xticks(x)
ax2.set_xticklabels(labels)

fig2.tight_layout()
plt.show()'''

barWidth = 0.1

# Set position of bar on X axis
br1 = [x-2*barWidth for x in np.arange(len(costs))]
br2 = [x + barWidth for x in br1]
br3 = [x + barWidth for x in br2]
br4 = [x + barWidth for x in br3]
br5 = [x + barWidth for x in br4]

# Make the plot
plt.bar(br1, cost_list[0], color ='r', width = barWidth,edgecolor ='grey', label =costs[0])
plt.bar(br2, cost_list[1], color ='g', width = barWidth,edgecolor ='grey', label =costs[1])
plt.bar(br3, cost_list[2], color ='b', width = barWidth,edgecolor ='grey', label =costs[2])
plt.bar(br4, cost_list[3], color ='c', width = barWidth,edgecolor ='grey', label =costs[3])
plt.bar(br5, cost_list[4], color ='m', width = barWidth,edgecolor ='grey', label =costs[4])
# Adding Xticks
plt.xlabel('Degree of trace and quarantine')
plt.ylabel('Cumulative cost')
plt.xticks([r for r in range(5)])
plt.title(title)
plt.legend()
plt.show()

if pgf:
    plt.savefig(name+'.pgf')
