# Import libraries
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt



# Creating figure
fig = plt.figure(figsize = (10, 7))
ax = plt.axes(projection ="3d")


error_list=[0,0.1,0.2]
delay_list=[0,1,2]
qtime_list=[12,14,16]
dict_3d={0: {0: {12: 3, 14: 3, 16: 3}, 1: {12: 0, 14: 3, 16: 3}, 2: {12: 0, 14: 3, 16: 3}}, 0.1: {0: {12: 0, 14: 3, 16: 3}, 1: {12: 0, 14: 0, 16: 3}, 2: {12: 0, 14: 0, 16: 0}}, 0.2: {0: {12: 0, 14: 0, 16: 0}, 1: {12: 0, 14: 0, 16: 0}, 2: {12: 0, 14: 0, 16: 0}}}

for index,error in enumerate(error_list):
    for delay in delay_list:
        for qtime in qtime_list:
            if dict_3d[error][delay][qtime]==3:
                ax.scatter3D(error,delay,qtime, color = "green",s=3000)
            if dict_3d[error][delay][qtime]==0:
                ax.scatter3D(error,delay,qtime, color = "red",s=3000)




# Creating plot

plt.title("simple 3D scatter plot")

# show plot
plt.show()
