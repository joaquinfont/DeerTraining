import operator;
from numpy import *;
from TraitResultObject import TraitResult;
from GenDevelopment import *;
import sys
from BicycleModel import *
from Deer import *
from Driver import *

def BinaryConversion(ind):

	resolution = 5

	# Set minimum and maximum values

	Psi0_min = -3.14/2 # radians
	Psi0_max = 3.14/2 # radians

	SigmaPsi_min = 0 # radians
	SigmaPsi_max = 0.45*3.24 # radians

	tturn_min = 0.4 # seconds
	tturn_max = 2.5 # seconds

	Vmax_min = 5 # m/s
	Vmax_max = 18 # m/s

	Tau_min = 0.75 # seconds
	Tau_max = 5 # seconds

	# Divide individual into different binary 
	Psi0_bin = ind[0:resolution]
	SigmaPsi_bin = ind[resolution:2*resolution]
	tturn_bin = ind[2*resolution:3*resolution]
	Vmax_bin = ind[3*resolution:4*resolution]
	Tau_bin = ind[4*resolution:5*resolution]

	# Convert from binary to decimala
	Psi0 = Psi0_min + (Psi0_max - Psi0_min)*float(int(Psi0_bin,2))/((2**resolution)-1)
	SigmaPsi = SigmaPsi_min + (SigmaPsi_max - SigmaPsi_min)*float(int(SigmaPsi_bin,2))/((2**resolution)-1)
	tturn = tturn_min + (tturn_max - tturn_min)*float(int(tturn_bin,2))/((2**resolution)-1)
	Vmax = Vmax_min + (Vmax_max - Vmax_min)*float(int(Vmax_bin,2))/((2**resolution)-1)
	Tau = Tau_min + (Tau_max - Tau_min)*float(int(Tau_bin,2))/((2**resolution)-1)

	#Rrint results
	# print(Psi0)
	# print(SigmaPsi)
	# print(tturn)
	# print(Vmax)
	# print(Tau)

	return array([Psi0,SigmaPsi,tturn,Vmax,Tau])

def TestDeer(deer_ind, n, agent):

	min_distance = zeros(n)

	if agent == "B":
		
		setSpeed = 25
		brake = 'off'
		brakeTime = 0
		yr = 0

	if agent == "C":

		setSpeed = 25
		brake = 'off'
		brakeTime = 0
		yr = 3.5

	if agent == "D":

		setSpeed = 25
		brake = 'on'
		brakeTime = 3
		yr = 0

	if agent == "E":

		setSpeed = 25
		brake = 'on'
		brakeTime = 3
		yr = 3.5


	for k_1 in range(0,n):

		# Where n is the number of drivers we are goin to test each deer against

		deer = Deer(Psi0_Deer = deer_ind[0], Sigma_Psi = deer_ind[1], tturn_Deer = deer_ind[2], Vmax_Deer = deer_ind[3], Tau_Deer = deer_ind[4])

		# Indicate deer initial position
		deer.x_Deer = 80
		deer.y_Deer = -2
	 	# Define simulation time and dt
		simtime = 10
		dt = deer.dT
		t = arange(0,simtime,dt) #takes min, max, and timestep\

	    #now set up the car's parameters		
		car = BicycleModel(dT=dt,U=20)
		steervec = zeros(len(t))

	 	#set up the driver
		driver = Driver(dt = dt)
		drive = zeros(3)

	    #initialize matrices to hold simulation data
	    #car state vector #print array([[Ydot],[vdot],[Xdot],[Udot],[Psidot],[rdot]])
		carx = zeros((len(t),len(car.x)))
		carx[0,:] = car.x

	    #initialize for deer as well
		deerx = zeros((len(t),4))
	    #fill in initial conditions because they're nonzero
		deerx[0,:] = array([deer.Speed_Deer,deer.Psi_Deer,deer.x_Deer,deer.y_Deer])

	    #now simulate!!
		for k in range(1,len(t)):

			carx_now = carx[k-1,:]

			drive[:] = driver.driving(carx = carx_now, deer_x = deerx[k-1,2], setSpeed = setSpeed, brake = brake, yr = yr, brakeTime = brakeTime)

			carx[k,:],junk=car.heuns_update(brake = drive[1], gas = drive[0], steer = drive[2], cruise = 'off')
			deerx[k,:] = deer.updateDeer(car.x[2])

		
		distance = sqrt((carx[:,2]-deerx[:,2])**2+(carx[:,0]-deerx[:,3])**2)



		min_distance[k_1] = min(distance)

		
		print(min_distance)

	# Calculate IQM

	# Sort values from smallest to largest
	min_distance = sorted(min_distance)
	# Eliminate lower and upper quartiles
	min_distance = min_distance[2:6]
	# Calculate the IQM
	avg_min_distance = mean(min_distance)
	# print(avg_min_distance)

	return(avg_min_distance)

if __name__=='__main__':


	generation = 1;
	agent = "C";
	#Select agent:
	# A = Human
	# B = Straight
	# C = Swerve
	# D = Brake
	# E = Hybrid

	Gfname = 'GenerationFiles/generations' + str(agent) + '/generation' + str(generation) + '/Generation' + str(generation) + '.txt';
	IntGfname = 'GenerationFiles/generations' + str(agent) + '/generation' + str(generation) + '/Generation' + str(generation) + 'IntResults.txt';

	intermediatePopulationSize = 10;
	numberOfHumans = 8;
	populationSize = 15;

	n = populationSize
	m = intermediatePopulationSize;
	h = numberOfHumans;

	#should have an array of size m*h (of object values )

	#in some way, read in a text file to fill an array
	with open(Gfname, "r") as ins:
		CurrentGenarray = []
		for line in ins:
			values = line.split()
			deer = TraitResult();
			deer.assign(str(values[0]),float(values[1]));
			CurrentGenarray.append(deer)

	# we now have an arrary of deer objects, paired values of attributes and the corresponding results
	CurrentGenarray.sort(key=operator.attrgetter("result"))


	for x in range(0, len(CurrentGenarray)):
		print CurrentGenarray[x].traits

	for x in range(0, len(CurrentGenarray)):
		print CurrentGenarray[x].result

	NewInterGenArray = [];

	for x in range(0, m):
		develMethod = random.randint(6);
		if develMethod == 0:
			inds = random.choice(len(CurrentGenarray),2);
			print str(x) + ' do single point cross with ' + str(inds[0]) + ' ' + str(inds[1]);
			NewDeer = SinglePoint(CurrentGenarray[inds[0]],CurrentGenarray[inds[1]]);
		if develMethod == 1:
			inds = random.choice(len(CurrentGenarray),2);
			print str(x) + ' do double point cross with ' + str(inds[0]) + ' ' + str(inds[1]);
			NewDeer = DoublePoint(CurrentGenarray[inds[0]],CurrentGenarray[inds[1]]);
		if develMethod == 2:
			inds = random.choice(len(CurrentGenarray),2);
			print str(x) + ' do random point cross with ' + str(inds[0]) + ' ' + str(inds[1]);
			NewDeer = RandomPoint(CurrentGenarray[inds[0]],CurrentGenarray[inds[1]]);
		if develMethod == 3:
			inds = random.choice(len(CurrentGenarray),2);
			print str(x) + ' do and cross with ' + str(inds[0]) + ' ' + str(inds[1]);
			NewDeer = AndCross(CurrentGenarray[inds[0]],CurrentGenarray[inds[1]]);
		if develMethod == 4:
			inds = random.choice(len(CurrentGenarray),2);
			print str(x) + ' do or cross with ' + str(inds[0]) + ' ' + str(inds[1]);
			NewDeer = OrCross(CurrentGenarray[inds[0]],CurrentGenarray[inds[1]]);
		if develMethod == 5:
			inds = random.choice(len(CurrentGenarray),1);
			print str(x) + ' do mutation with ' + str(inds[0]);
			NewDeer = Mutate(CurrentGenarray[inds[0]]);
		NewInterGenArray.append(NewDeer);

	print '';
	for x in range(0, len(CurrentGenarray)):
		print  str(x) + ' ' + str(CurrentGenarray[x].traits) + ' ' + str(CurrentGenarray[x].result);	
	print '';
	for x in range(0, len(NewInterGenArray)):
		print  str(x) + ' ' + str(NewInterGenArray[x].traits) + ' ' + str(NewInterGenArray[x].result);	
	print '';

	#Test deer in intermediate generation
	for index in range(0,m):
		CurrentDeer = BinaryConversion(str(NewInterGenArray[index].traits))
		print CurrentDeer
		NewInterGenArray[index].result = TestDeer(CurrentDeer, 8, agent)
		print NewInterGenArray[index].result

	for x in range(0, n):
		NewInterGenArray.append(CurrentGenarray[x])

	for x in range(0, len(NewInterGenArray)):
		print str(NewInterGenArray[x].traits) + ' ' + str(NewInterGenArray[x].result);	
	print '';

	#Now, total array of intermediate and base generation, with scores

	NewInterGenArray.sort(key=operator.attrgetter("result"))

	for x in range(0, len(NewInterGenArray)):
		print str(NewInterGenArray[x].traits) + ' ' + str(NewInterGenArray[x].result);	
	print '';

	NewBaseGenArray = []

	for x in range(0, n/2):
		NewBaseGenArray.append(NewInterGenArray[0]);
		NewInterGenArray.pop(0)

	for x in range(0,(n+m)/5):
		NewInterGenArray.pop(len(NewInterGenArray)-1)

	for x in range(0, n/2+1):
		randIndex = random.randint(len(NewInterGenArray))
		NewBaseGenArray.append(NewInterGenArray[randIndex]);
		NewInterGenArray.pop(randIndex);


	for x in range(0, len(NewInterGenArray)):
		print str(NewInterGenArray[x].traits) + ' ' + str(NewInterGenArray[x].result);	
	print '';

	for x in range(0, len(NewBaseGenArray)):
		print str(NewBaseGenArray[x].traits) + ' ' + str(NewBaseGenArray[x].result);	
	print '';

	G2fname = 'GenerationFiles/generations' + str(agent) + '/generation' + str(generation+1) + '/Generation' + str(generation+1) + '.txt';

	Gfname = 'GenerationFiles/generations' + str(agent) + '/generation' + str(generation) + '/Generation' + str(generation) + '.txt';

	newGenFile = open(G2fname,'w+');
	newGenFile.close();
	newGenFile = open(G2fname, 'a');
	for x in range(0, len(NewBaseGenArray)):
		newGenFile.write(str(NewBaseGenArray[x].traits) + ' ' + str(NewBaseGenArray[x].result) + '\n');



