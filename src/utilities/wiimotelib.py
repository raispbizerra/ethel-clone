import numpy as np
import math

history = np.zeros(100)
history_best = 1
history_cursor = -1
zeroed_weight = 0.

def get_balance_board_sensor_value(sensor, calibrations):
	'''This method returns the weight by sensor
	
	Parameters
	----------
	sensor: int
		Sensor reading
	calibrations: array
		Sensor calibrations
	'''
	
	minimo = calibrations[0]
	medio = calibrations[1]
	maximo = calibrations[2]
	
	if maximo == medio or medio == minimo:
		return 0

	if(sensor < medio):
		return 68. * (sensor - minimo) / (medio - minimo)
	else:
		return 68. * (sensor - medio) / (maximo - medio) + 68.

def calcWeight(readings, calibrations):
	weight = 0.
	for sensor in readings.keys():
		weight += get_balance_board_sensor_value(readings[sensor], calibrations[sensor])
	return weight / 4

def calCoP(readings, calibrations):
	rt = 0
	rb = 1
	lt = 2
	lb = 3
	BSL = 433
	BSW = 238

	F = np.zeros(4)
	for j, sensor in enumerate(calibrations.keys()):
		F[j] = get_balance_board_sensor_value(readings[sensor], calibrations[sensor])

	Kx = (F[lt] + F[lb]) / (F[rt] + F[rb])
	Ky = (F[lt] + F[rt]) / (F[lb] + F[rb])

	return (BSL / 2) * (Kx - 1) / (Kx + 1), (BSW / 2) * (Ky - 1) / (Ky + 1)