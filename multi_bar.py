import matplotlib.pyplot as plt
import numpy as np

pgf=False
name='multibar_1b'

if pgf:
    matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
    })

hdict={'Susceptible': [17866.5, 30038.1, 127996.4, 186337.8, 187992.0], 'Exposed': [7476.8, 7239.8, 4103.9, 612.6, 536.5], 'Asymptomatic': [4764.4, 4719.0, 2549.5, 444.6, 363.8], 'Symptomatic': [17724.3, 17100.9, 9517.6, 1528.2, 1332.6], 'Recovered': [154168.0, 142902.2, 57832.6, 13076.8, 11775.1], 'Quarantined': [0.0, 19825.2, 70386.3, 49247.1, 57212.6]}
print(hdict)

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
plt.xlabel('Degree of trace and quarantine', fontweight ='bold', fontsize = 15)
plt.ylabel('Cumulative cost', fontweight ='bold', fontsize = 15)
plt.xticks([r for r in range(5)])

plt.legend()
plt.show()

if pgf:
    #st.pyplot(fig2)
    if name2!=None:
        plt.savefig(name+'.pgf')
