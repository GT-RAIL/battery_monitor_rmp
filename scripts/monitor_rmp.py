#!/usr/bin/env python

"""
Battery monitor for the Segway RMP platform.

Author:  Chris Dunkers, Worcester Polytechnic Institute
Version: June 23, 2014
"""
from rmp_msgs.msg import RMPFeedback, RMPBatteryStatus
from python_ethernet_rmp.system_defines import *
import rospy
import math
import time
import os

class BatteryMonitor:

	def __init__(self):
		"""
		Initialize the subscriptions and publishers of the node.
		"""
		self.battStatusPub = rospy.Publisher('battery_status_rmp', RMPBatteryStatus, queue_size = 'None')

		rospy.Subscriber("rmp_feedback", RMPFeedback, self.get_batt_state)
		
		"""
		Get the battery parameters
		"""
		self.has_front_batt_1 = rospy.get_param('~front_base_batt_1',False)
		self.has_front_batt_2 = rospy.get_param('~front_base_batt_2',False)
		self.has_rear_batt_1 = rospy.get_param('~rear_base_batt_1',False)
		self.has_rear_batt_2 = rospy.get_param('~rear_base_batt_2',False)
		self.has_aux_batt = rospy.get_param('~aux_batt',False)
		
		self.next_check = rospy.Time.now()
		
	def get_batt_state(self, rmp):
		"""
		Read in the current RMP feedback and publish the pose
		:param rmp: the RMP feedback message
		"""
		rmp_items = rmp.sensor_items
		rmp_values = rmp.sensor_values
		
		batt_stat = RMPBatteryStatus()
		
		"""
		get the values for the feedback items needed
		"""
		for x in range(0, len(rmp_items)):
			if rmp_items[x] == 'front_base_batt_1_soc' and self.has_front_batt_1 == True:
				batt_stat.soc_items.append("front_base_batt_1_soc")
				batt_stat.soc_values.append(rmp_values[x])
			elif rmp_items[x] == 'front_base_batt_2_soc' and self.has_front_batt_2 == True:
				batt_stat.soc_items.append("front_base_batt_2_soc")
				batt_stat.soc_values.append(rmp_values[x])
			elif rmp_items[x] == 'rear_base_batt_1_soc' and self.has_rear_batt_1 == True:
				batt_stat.soc_items.append("rear_base_batt_1_soc")
				batt_stat.soc_values.append(rmp_values[x])
			elif rmp_items[x] == 'rear_base_batt_2_soc' and self.has_rear_batt_2 == True:
				batt_stat.soc_items.append("rear_base_batt_2_soc")
				batt_stat.soc_values.append(rmp_values[x])
			elif rmp_items[x] == 'aux_batt_soc' and self.has_aux_batt == True:
				batt_stat.soc_items.append("aux_batt_soc")
				batt_stat.soc_values.append(rmp_values[x])
			
		"""
		Publish the state of charges of the batteries present
		"""	
		batt_stat.header.stamp = rospy.Time.now()
		self.battStatusPub.publish(batt_stat)
		
		if rospy.Time.now() > self.next_check:
			for x in range(0,len(batt_stat.soc_items)):
				if batt_stat.soc_items[x] == 'front_base_batt_1_soc':
					self.send_warning("Front battery one", batt_stat.soc_values[x])
				elif batt_stat.soc_items[x] == 'front_base_batt_2_soc':
					self.send_warning("Front battery two", batt_stat.soc_values[x])
				elif batt_stat.soc_items[x] == 'rear_base_batt_1_soc':
					self.send_warning("Rear battery one", batt_stat.soc_values[x])
				elif batt_stat.soc_items[x] == 'rear_base_batt_2_soc':
					self.send_warning("Rear battery two", batt_stat.soc_values[x])
				elif batt_stat.soc_items[x] == 'aux_batt_soc':
					self.send_warning("Auxiliary battery", batt_stat.soc_values[x])
				
	def send_warning(self, batt, soc):
		if soc < 5:
			self.next_check = rospy.Time.now() + rospy.Duration.from_sec(5*60) #5min
			message = "espeak \"%s has 5 percent remaining\"" % (batt)
			os.system(message)
		if soc < 10:
			self.next_check = rospy.Time.now() + rospy.Duration.from_sec(10*60)	#10min
			message = "espeak \"%s has 10 percent remaining\"" % (batt)
			os.system(message)
		if soc < 20:
			self.next_check = rospy.Time.now() + rospy.Duration.from_sec(15*60) #15min
			message = "espeak \"%s has 20 percent remaining\"" % (batt)
			os.system(message)
		else:
			self.next_check = rospy.Time.now() + rospy.Duration.from_sec(20*60) #20min

if __name__ == "__main__":
	rospy.init_node("rmp_battery_monitor")
	battMonitor = BatteryMonitor()
	rospy.loginfo("RMP Battery Monitor Started")
	rospy.spin()
