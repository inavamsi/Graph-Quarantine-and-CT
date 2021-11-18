import random
import copy
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

class Agent():
	def __init__(self,state,index,schedule_time_left=None):
		self.state=state
		self.index=index
		self.neighbours=[]
		self.quarantined=False
		self.done_CT=False
		self.schedule_time_left=schedule_time_left

		#None implies not quarantined. Otherwise number will start at 1 and increase everyday.
		self.quarantine_state=None
		self.qdegree=None



	def next_state(self,state_info):
		self.state=state_info.state
		self.schedule_time_left=state_info.schedule_time_left

	def new_day(self):
		if self.schedule_time_left!=None:
			self.schedule_time_left-=1
