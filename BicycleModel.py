import sys
#sys.path.append('/home/brownlab/.local/lib/python3.4/site-packages')
# sys.path.append( '/home/brownlab/Desktop/blender-2.73-linux-glibc211-x86_64/2.73/python/lib/python3.4/site-packages')
# sys.path.append( '/home/brownlab/Desktop/blender-2.73-linux-glibc211-x86_64/2.73/scripts/freestyle/modules')
# sys.path.append( '/home/brownlab/Desktop/blender-2.73-linux-glibc211-x86_64/2.73/scripts/addons/modules')
# sys.path.append( '/home/brownlab/.config/blender/2.73/scripts/addons/modules')
# sys.path.append('/home/brownlab/Desktop/blender-2.79b-linux-glibc219-x86_64/2.79/python/lib/python3.4/site-packages')
# sys.path.append('/usr/lib/python3/dist-packages')
# print("PATH")
# print(sys.path)

#sys.path.append("/usr/local/lib/python3.4/dist-packages/")
#sys.path.append("/usr/lib/python3/dist-packages/")
#sys.path.append("/usr/local/lib/python3.4/dist-packages/numpy-1.12.0.dev0+4c415d2-py3.4-linux-x86_64.egg/")
#import numpy
from numpy import *#array,dot,cos,sin,sqrt,tan
from pacejkatire_numba import PacejkaTire
from matplotlib.pyplot import *

#from matplotlib.pyplot import *

class BicycleModel:

    def __init__(self,a = 0.8,b = 1.5,m = 1000.0,I=2000.0,U=20.0,Cf=100000.0,Cr=100000.0,mu=1.0,dT=0.01,tiretype='pacejka',drive='rear',bias=0.3,autopilot_gain = 1, xinit = 0, yinit = 0, zinit = 0,steering_actuator = 'on'):
        """ 
        BicycleModel(a = 1.2,b = 1.0,m = 1000.0,I=2000.0,U=20.0,Cf=-100000.0,Cr=-100000.0,mu=1.0,dT=0.01,tiretype='dugoff',coords='local'))
        This is a bicycle model. It can use a dugoff tire model or a linear tire model.

        Right now, there is only front/rear asymmetrical braking (no left/right bias) so steering with the brakes is not an option.

        Right now, very simple engine model with constant power. See euler_update for details. planning to break these out soon.

         """
         #maximum steer velocity taken from these: https://www.abdynamics.com/en/products/track-testing/driving-robots/steering-robots
         #asusming a 20:1 hand:road ratio
        self.max_steer_vel = 1600*pi/180.*1.0/20#rad/s, the max amount of ROADWHEEL velocity the motor can make.
        self.a = a
        self.b = b
        self.m = m
        self.I = I
        self.U = U
        self.Caf = Cf
        self.Car = Cr
        self.dT = dT
        #self.tire = DugoffTire()#pass arguments eventually
        self.mu = mu
        self.tiretype = tiretype
        self.drive = drive
        self.bias = bias
        self.Fyf = 0
        self.Fyr = 0
        self.Fxf = 0
        self.Fxr = 0
        self.alpha_f = 0
        self.alpha_r = 0
        self.autopilot_gain=autopilot_gain
        self.steer_limit = 0.25 #radioans
        self.cruise_gain = 5
        #calculate vertical tire forces TODO roll model? Longitudinal Weight Transfer?
        self.Fzf = self.m*self.b/(self.a+self.b)*9.81
        self.Fzr = self.m*self.a/(self.a+self.b)*9.81
        self.pacejkatire_front = PacejkaTire(self.Fzf/2,mu,mu)
        self.pacejkatire_rear = PacejkaTire(self.Fzf/2,mu,mu)

        # Steering actuator dynamics
        self.steering_actuator = steering_actuator
        self.z = 0.9
        self.w = 15
        self.delta_r = 0
        self.delta_rdot = 0
        self.delta_rold = 0
        self.e = 0
        self.e_old = 0
        self.delta = 0
        self.deltadot = 0
        self.deltaold = 0

        #engine stuff TODO:
        self.power  = 20000 #~100 HP  (100 KW) engine, constant power all the time. For now.

        #aero stuff: taken from a Nissan Leaf drag area 7.8 ft^2 0.725 m^2, Cd 0.32
        self.CdA = .32


        #state order is y,v,x,u,psi,r
        self.x = array([yinit,0,xinit,0,0,0])
        self.xdot = zeros(6)

    def dugoffFy(self,alpha,Fz,mu=1.5,Fx=0,Ca=100000):
        if abs(alpha)>0:
            mufz = sqrt((mu*Fz)**2-Fx**2)#De-rate lateral force capacity for braking
            lam= mufz/(2*Ca*abs(tan(alpha))) #lambda
            if lam>=1:
                flam = 1
            else:
                flam = (2-lam)*lam
            Fy = -Ca*tan(alpha)*flam
        else:
            Fy=0
        return Fy

    def state_eq(self,x,t,Fxf,Fxr,delta):
        """ state_eq(self,x,t,Fx,delta):
            returns state derivatives for odeint"""

        if abs(Fxf/self.Fzf)>self.mu: #make sure we can't apply any more brakes than makes sense.
            Fxf = self.Fzf*self.mu*sign(Fxf)
        if abs(Fxr/self.Fzr)>self.mu: #make sure we can't apply any more brakes than makes sense.
            Fxr = self.Fzr*self.mu*sign(Fxr)
        #calculate slip angles
        if abs(x[3])>0:
            self.alpha_f = 1/x[3]*(x[1]+self.a*x[5])-delta
            self.alpha_r = 1/x[3]*(x[1]-self.b*x[5]) 
            #print self.alpha_f,self.alpha_r
        else:#if the car is only spinning, but not driving forward, then alpha is nonsense
            self.alpha_f = 0
            self.alpha_r = 0

        #calculate tire forces
        if self.tiretype=='dugoff':
            #if the car is moving, use a real tire model
            if self.x[3]>0:
                self.Fyf = self.dugoffFy(self.alpha_f,self.Fzf,self.mu,Fxf,self.Caf)
                self.Fyr = self.dugoffFy(self.alpha_r,self.Fzr,self.mu,Fxr,self.Car)
            else:
                #the car isn't really moving, so use static friction
                self.Fyf = -self.Fzf*self.mu*sign(self.x[1]+self.a*self.x[5])
                self.Fyr = -self.Fzr*self.mu*sign(self.x[1]-self.b*self.x[5])
        elif self.tiretype=='pacejka':
            if self.x[3]>0:
                #calculate effective Calphas RIGHT NOW
                Fyf_high = 2*self.pacejkatire_front.calcFy_xforce(self.Fzf/2,self.alpha_f+.01,Fxf,0)
                Fyf_low = 2*self.pacejkatire_front.calcFy_xforce(self.Fzf/2,self.alpha_f-.01,Fxf,0)
                Fyr_high = 2*self.pacejkatire_rear.calcFy_xforce(self.Fzr/2,self.alpha_r+.01,Fxr,0)
                Fyr_low = 2*self.pacejkatire_rear.calcFy_xforce(self.Fzr/2,self.alpha_r-.01,Fxr,0)
                self.Caf = abs(Fyf_high-Fyf_low)/(.02)
                self.Car = abs(Fyr_high-Fyr_low)/(.02)

                self.Fyf = 2*self.pacejkatire_front.calcFy_xforce(self.Fzf/2,self.alpha_f,Fxf,0)
                self.Fyr = 2*self.pacejkatire_rear.calcFy_xforce(self.Fzr/2,self.alpha_r,Fxr,0)
            else:
                #the car isn't really moving, so use static friction
                self.Fyf = -self.Fzf*self.mu*sign(self.x[1]+self.a*self.x[5])
                self.Fyr = -self.Fzr*self.mu*sign(self.x[1]-self.b*self.x[5])
        else:
            if self.x[3]>0:
                self.Fyf = -self.alpha_f*self.Caf
                self.Fyr = -self.alpha_r*self.Car
            else:
                #the car isn't really moving, so use static friction
                self.Fyf = -self.Fzf*self.mu*sign(self.x[1]+self.a*self.x[5])
                self.Fyr = -self.Fzr*self.mu*sign(self.x[1]-self.b*self.x[5])

        Ydot = x[1]*cos(x[4])+x[3]*sin(x[4]) #north velocity NOT local!
        vdot = -x[3]*x[5] + 1/self.m*(self.Fyf+self.Fyr+Fxf*delta) #derivative of local lateral velocity
        Xdot = x[3]*cos(x[4])-x[1]*sin(x[4]) #East velocity NOT local!
        Udot = x[5]*x[1]+(Fxf+Fxr-self.Fyf*delta)/self.m #this is the derivative of local forward speed
        Psidot = x[5]
        rdot = (self.a*(self.Fyf+Fxf*delta)-self.b*self.Fyr)/self.I #cosines in there? Small angle? Sounds/Looks OK...
        #print array([[Ydot],[vdot],[Xdot],[Udot],[Psidot],[rdot]])
        return array([Ydot,vdot,Xdot,Udot,Psidot,rdot])

    def calc_inputs(self,brake,gas,steer):
        #first calculate engine power accepting an input from 0 to 1
        #gas = -gas
        if gas<0:
            gas = 0
        if abs(gas)>1:
            gas = 1
            
        if self.x[3]>0:
            Engine_Force = gas * self.power/self.x[3]
            if Engine_Force>self.mu*self.m*9.81:
                Engine_Force = self.mu*self.m*9.81
        else:
            Engine_Force = gas*self.mu*self.m*9.81
        
        if Engine_Force<0:
            Engine_Force = 0

            ############## ABS GOES HERE ###############
        #now calculate the brake forces accepting an input from 0 to 1
        total_brake_force = brake * (self.m*9.81) #max brakes out. TODO model brake fade and speed dependence
        front_brake_force = total_brake_force*(1-self.bias)#so the brake bias of 1 means all rear brakes
        rear_brake_force = total_brake_force*self.bias

        if front_brake_force > (self.m*9.81*self.mu*self.b/(self.a+self.b)):
            front_brake_force = self.m*9.81*self.mu*self.b/(self.a+self.b)

        if rear_brake_force > (self.m*9.81*self.mu*self.a/(self.a+self.b)):
            rear_brake_force = self.m*9.81*self.mu*self.a/(self.a+self.b)

        if self.U>0:
            if self.drive=='rear':
                Fxf = -front_brake_force
                Fxr = -rear_brake_force +Engine_Force
            elif self.drive=='all':
                Fxf = -front_brake_force+Engine_Force/2
                Fxr = -rear_brake_force+Engine_Force/2
            else:
                Fxf = -front_brake_force+Engine_Force
                Fxr = -rear_brake_force
        else:
            if self.drive=='rear':
                Fxf = -front_brake_force*sign(self.x[3])
                Fxr = -rear_brake_force*sign(self.x[3]) +Engine_Force
            elif self.drive=='all':
                Fxf = -front_brake_force*sign(self.x[3])+Engine_Force/2
                Fxr = -rear_brake_force*sign(self.x[3])+Engine_Force/2
            else:
                Fxf = -front_brake_force*sign(self.x[3])+Engine_Force
                Fxr = -rear_brake_force*sign(self.x[3])
        
        return Fxf,Fxr,steer

    def cruise(self,setspeed):
        gas = self.cruise_gain*(setspeed-self.U)#Just p-control for the moment TODO
        
        if gas<0:
            gas = 0
        return gas

    def ACC(self,setspeed,obsloc,obsvel):
        #this is for adaptive cruise control. NOT TESTED PROB DOESNT WORK. ASSUMES obstacle is directly in front.
        #first set nominal gas
        gas = self.cruise(setspeed)
        #now modify gas for obstacle
        distance_to_obs = obsloc-self.x
        if distance_to_obs>0: #if the obstacle is actually in front of us
            pass


    def euler_update(self,brake=0,gas=0,steer=0,cruise = 'on',setspeed=20.0,autopilot='off',mpc='off',patherror=0):
        Fxf,Fxr,steer = self.calc_inputs(brake,gas,steer)
        if cruise=='on': #TODO make this better. Hardcoded and awful for now...
            gas = self.cruise(setspeed)
            Fxf,Fxr,steer = self.calc_inputs(brake,gas,steer)
        if autopilot=='on':
            steer = self.autopilot_gain*patherror #VERY simple autopilot. Path error can be previewed, or can be angle, or whatever.
            if abs(steer)>self.steer_limit:
                steer = sign(steer)*self.steer_limit
            #print steer
            Fxf,Fxr,steer = self.calc_inputs(brake,gas,steer)
        

        #this should have taken casre of all contingencies and got us the correct inputs for the car.
        self.xdot = self.state_eq(self.x,0,Fxf,Fxr,steer)
        self.x = self.x+self.dT*self.xdot #this should update the states
        self.U = self.x[3]
        #print("actual inputs passed:     "+str(Fxf)+","+str(Fxr)+","+str(steer))
        return self.x,self.xdot

    def heuns_update(self,brake=0,gas=0,steer=0,cruise = 'on',setspeed=20.0,autopilot='off',mpc='off',patherror=0):
       
        # Update steering actuator
        if self.steering_actuator == 'on':
            steer = self.steering_update(steer)

        Fxf,Fxr,steer = self.calc_inputs(brake,gas,steer)
        if cruise=='on': #TODO make this better. Hardcoded and awful for now...
            gas = self.cruise(setspeed)
            Fxf,Fxr,steer = self.calc_inputs(brake,gas,steer)
        if autopilot=='on':
            steer = self.autopilot_gain*patherror #VERY simple autopilot. Path error can be previewed, or can be angle, or whatever.
            if abs(steer)>self.steer_limit:
                steer = sign(steer)*self.steer_limit
            #print steer
            Fxf,Fxr,steer = self.calc_inputs(brake,gas,steer)

        #this should have taken case of all contingencies and got us the correct inputs for the car.
        k1x = self.state_eq(self.x,0,Fxf,Fxr,steer) # Calvulate k1
        xhat = self.x + self.dT*k1x # Find x_hat
        k2x = self.state_eq(xhat,0,Fxf,Fxr,steer) # Calcaulte k2 using x_hat
        self.xdot = (k1x+k2x)/2 # Find xdot by averaging k1 and k2

        self.x = self.x + self.xdot*self.dT
        self.U = self.x[3]

        return self.x,self.xdot,steer

    def rk_update(self,brake=0,gas=0,steer=0,cruise = 'on',setspeed=20.0,autopilot='off',mpc='off',patherror=0):
       
        # Update steering actuator
        if self.steering_actuator == 'on':
            steer = self.steering_update(steer)

        Fxf,Fxr,steer = self.calc_inputs(brake,gas,steer)
        if cruise=='on': #TODO make this better. Hardcoded and awful for now...
            gas = self.cruise(setspeed)
            Fxf,Fxr,steer = self.calc_inputs(brake,gas,steer)
        if autopilot=='on':
            steer = self.autopilot_gain*patherror #VERY simple autopilot. Path error can be previewed, or can be angle, or whatever.
            if abs(steer)>self.steer_limit:
                steer = sign(steer)*self.steer_limit
            #print steer
            Fxf,Fxr,steer = self.calc_inputs(brake,gas,steer)

        #this should have taken case of all contingencies and got us the correct inputs for the car.
        k1x = self.state_eq(self.x,0,Fxf,Fxr,steer) # Calvulate k1
        xhat1 = self.x + self.dT*k1x/2 # Find x_hat1
        k2x = self.state_eq(xhat1,0,Fxf,Fxr,steer) # Calcaulte k2 using x_hat1
        xhat2 = self.x + self.dT*k2x/2 # Find x_hat2
        k3x = self.state_eq(xhat2,0,Fxf,Fxr,steer) # Calcaulte k3 using x_hat2
        xhat3 = self.x + self.dT*k3x # Find x_hat3
        k4x = self.state_eq(xhat3,0,Fxf,Fxr,steer) # Calcaulte k4 using x_hat3

        # Calculate xdot
        self.xdot = (k1x+2*k2x+2*k3x+k4x)/6 # Find xdot by averaging k1 and k2

        self.x = self.x + self.xdot*self.dT
        self.U = self.x[3]

        return self.x,self.xdot,steer


    def euler_predict(self,x,brake=0,gas=0,steer=0,dT=0.1):
        Fxf,Fxr,steer = self.calc_inputs(brake,gas,steer)
        self.xdot = self.state_eq(x,0,Fxf,Fxr,steer)
        x = x+self.dT*self.xdot #this should update the states
        return x,self.xdot


    def steering_statederivs(self, delta, deltadot, delta_r, delta_rdot):
        deltaddot = 2 * self.z * self.w * (delta_rdot - deltadot) + self.w * self.w * (delta_r - delta)
        return [deltadot, deltaddot]
  
    def steering_update(self, delta_r):
        self.delta_r = delta_r;
        self.delta_rdot = (self.delta_r - self.delta_rold) / self.dT;
        self.deltadot = (self.delta - self.deltaold) / self.dT;
        if(abs(self.deltadot)>self.max_steer_vel):
            self.deltadot = sign(self.deltadot)*self.max_steer_vel
        self.deltaold = self.delta;
        self.delta_rold = self.delta_r;
        #self uses Heun's method (trapezoidal)
        xdot1 = self.steering_statederivs(self.delta, self.deltadot, self.delta_r, self.delta_rdot);
        #first calculation
        deltaprime = self.delta + xdot1[0] * self.dT;
        deltadotprime = self.deltadot + xdot1[1] * self.dT;
        if(abs(deltadotprime)>self.max_steer_vel):
            deltadotprime = sign(self.deltadot)*self.max_steer_vel
        #now compute again
        xdot2 = self.steering_statederivs(deltaprime, deltadotprime, self.delta_r, self.delta_rdot);
        #now compute the final update
        self.delta = self.delta + self.dT / 2 * (xdot1[0] + xdot2[0]);
        self.deltadot = self.deltadot + self.dT / 2 * (xdot1[1] + xdot2[1]);



        if (self.delta > self.steer_limit):
            self.delta = self.steer_limit

        if (self.delta < -self.steer_limit):
            self.delta = -self.steer_limit

        return self.delta;

    # def minError(self,uvec,roadvec,speedvec,xv,Rsteer,Rgas,Rbrake,Qroad,Qspeed,dT):
    #     """ minError(uvec,rvec,xvehicle) returns the objective value for minimizing vehicle-road error over a prediction horizon.
    #     uvec should be an array of length N where N is the prediction horizon.
    #     rvec should also be an array of length N where N is the prediction horizon.
    #     bmodel is a BicycleModel object, with built-in discretization at the proper timestep.
    #     This function is designed to be used in conjunction with a scipy.optimize minimize call. """
    #     J = 0 #initialize the objective to zero
    #     #print uvec
    #     brakevec = uvec[0:len(roadvec)]#first row is brake
    #     gasvec = uvec[len(roadvec):2*len(roadvec)]#second is brake
    #     steervec = uvec[2*len(roadvec):]
    #     #print len(brakevec),len(gasvec),len(steervec)
    #     #now loop through and update J for every timestep in the prediction horizon.
    #     #TODO this is something to do later: make the J look at lateral error, not y-error so we can go with closed paths etc.
    #     for ind in range(0,len(roadvec)): #compute for each step in the prediction horizon
    #         #print ind
    #         xv = self.euler_predict(xv,brakevec[ind],gasvec[ind],steervec[ind],dT)
    #         J=J+(Qroad*(roadvec[ind]-xv[0])**2+Qspeed*(speedvec[ind]-xv[3])**2+Rsteer*steervec[ind]**2+Rbrake*brakevec[ind]**2+Rgas*gasvec[ind]**2) #SIMPLE! just add the square of the error to the objective function!
    #         #print J
    #     return J

    # def MPC_auto(self,xv,speedref,roadref,unow=None,Rsteer=1,Rgas=1,Rbrake=1,Qroad=1,Qspeed=10,dT=0.1):
    #     #this is where the MPC autopilot code goes.
    #     if unow is None:
    #         u0 = random.randn(3,len(speedref))#grab an initial guess for the gas, brake, and steer values.
    #     else:
    #         u0 = unow
    #     #print u0
    #     umpc = minimize(self.minError,u0,args=(roadvec,speedvec,xv,Rsteer,Rgas,Rbrake,Qroad,Qspeed,dT),method='BFGS',options={'xtol': 1e-12, 'disp': True,'eps':.0001,'gtol':.0001}) # (BFGS)let minimize (scipy) do the optimization!     
    #     brake,gas,steer =umpc.x[0],umpc.x[10],umpc.x[20]
    #     print gas,umpc.x[10:20]

    #     return brake,gas,steer
    #     #brake,gas,steer = umpc[0,0],umpc[1,0],umpc[2,0] #optimal inputs are the first in the horizon optimized by MPC.
    #     #return brake,gas,steer

    def minError(self,steervec,gas,brake,roadvec,xv,Rsteer,Qroad,Qacc,dT):
        """ minError(uvec,rvec,xvehicle) returns the objective value for minimizing vehicle-road error over a prediction horizon.
        uvec should be an array of length N where N is the prediction horizon.
        rvec should also be an array of length N where N is the prediction horizon.
        bmodel is a BicycleModel object, with built-in discretization at the proper timestep.
        This function is designed to be used in conjunction with a scipy.optimize minimize call. 

        NOTE: This takes a SCALAR gas and brake value, gleaned from a separate ACC/cruise control algorithm.

        """
        J = 0 #initialize the objective to zero
        #print len(brakevec),len(gasvec),len(steervec)
        #now loop through and update J for every timestep in the prediction horizon.
        #TODO this is something to do later: make the J look at lateral error, not y-error so we can go with closed paths etc.
        for ind in range(0,len(steervec)): #compute for each step in the prediction horizon
            #print ind
            #calculate states AND derivatives so that we can calculate acceleration.
            xv,xdot = self.euler_predict(xv,brake,gas,steervec[ind],dT)
            #now acceleration in the y-direction is vdot + U*r
            y_acc = xdot[1]+xv[3]*xv[5]
            #print xv
            J=J+(Qroad*(roadvec[ind]-xv[0])**2+Qacc*y_acc**2+Rsteer*steervec[ind]**2) #SIMPLE! just add the square of the error to the objective function!
            #print J
        return J

    def MPC_auto(self,xv,roadref,brake,gas,unow=None,Rsteer=0,Qroad=1,Qacc=.0005,dT=0.1):
        #this is where the MPC autopilot code goes.
        if unow is None:
            u0 = random.randn(len(roadref))#grab an initial guess for the gas, brake, and steer values.
        else:
            u0 = unow
        #print u0
        umpc = minimize(self.minError,u0,args=(gas,brake,roadvec,xv,Rsteer,Qroad,Qacc,dT),method='BFGS',options={'xtol': 1e-12, 'disp': False,'eps':.0001,'gtol':.0001}) # (BFGS)let minimize (scipy) do the optimization!     
        steer =umpc.x[0]
        return steer,umpc.x
        #brake,gas,steer = umpc[0,0],umpc[1,0],umpc[2,0] #optimal inputs are the first in the horizon optimized by MPC.
        #return brake,gas,steer







if __name__=='__main__':
    """ This is the demo for the Dugoff bicycle model car"""
    
    opt = 1 #change this (1 or 2) to look at open-loop vs. closed-loop stuff. 1 is open loop, 2 is closed loop

    if opt==3:
        car = BicycleModel(autopilot_gain=.02,dT=0.01)
        car.x[0] = 0.5
        simtime = 20
        
        #now we will build a road upon which the car should drive. We will define a road by an X, a Y, an S, and a speed profile.
        granularity = .25 #meter.
        roadlength = 300
        roadx = arange(0,roadlength,granularity)
        roady = zeros(len(roadx))
        #now a speed profile. Make it constant for now.
        speedlimit =20 #m/s
        roadspeed = speedlimit*ones(len(roadx))
        #now put in a lane change halfway down the road that will last 2 sec
        lanewidth = 4 #meters
        LC_time = 3 #seconds
        LC_x = arange(0,speedlimit*LC_time,granularity) #this is how long in the x-direction the lane change should take
        LC_y = lanewidth/2*(1-cos(LC_x*(pi/(speedlimit*LC_time))))
        roady[roadlength/2:roadlength/2+len(LC_x)] = LC_y
        roady[roadlength/2+len(LC_x):]=lanewidth

        #now let's plot our road.
        figure()
        plot(LC_x,LC_y)
        figure()
        subplot(2,1,1)
        plot(roadx,roady)
        ylabel('road y-position (m)')
        subplot(2,1,2)
        plot(roadx,roadspeed)
        xlabel('road x-position (m)')
        ylabel('speed (m/s)')
        #show()

        #now let's simulate the car driving on said road with the simple steering autopilot and with MPC
        t = arange(0,simtime,car.dT)
        #we will assemble what we need for the MPC driver, and use the "farthest ahead" point to drive the simple autopilot.
        xvec = car.x
        dt_predict = 0.1 #prediction timestep for MPC
        Nsteps = 10 #prediction horizon for MPC
        preview_time = dt_predict*Nsteps #seconds
        brake,gas,steer = 0,1,0
        unow = random.randn(10)
        steervec = zeros(len(t))
        steervec_mpc = zeros(len(t))


        for ind in range(1,len(t)):
            print (ind)
            #first look up the y of the road
            if car.x[3]==0:
                #if car is not moving, pretend that it is so that preview vector doesn't go crazy.
                preview_dist_vector = arange(0,(Nsteps)*dt_predict,dt_predict)*0.1
            else:
                preview_dist_vector = arange(0,(Nsteps)*dt_predict,dt_predict)*car.x[3]

            #now figure out what the previewed vector of road y-positions is. Use interpolation for this.
            roadvec = interp(car.x[2]+preview_dist_vector,roadx,roady,left=0,right=0)
            speedvec = interp(car.x[2]+preview_dist_vector,roadx,roadspeed,left=0,right=0)
            if len(roadvec)<Nsteps:
                roadvec = roady[-1]*ones(len(preview_dist_vector))
                speedvec = speedlimit*ones(len(preview_dist_vector))
            #print len(preview_dist_vector)

            #update car. use a simple lookahead "lever arm" to pass as a path error.
            x,junk = car.euler_update(steer=0,gas=0,brake=0,cruise='on',autopilot='on',setspeed=speedvec[-1],patherror=(roadvec[-1]-(car.x[0]+preview_dist_vector[-1]*sin(car.x[4]))))
            xvec = vstack((xvec,x))

        figure()
        subplot(3,1,1)
        plot(t,xvec[:,1])
        ylabel('lateral velocity')
        subplot(3,1,2)
        plot(t,xvec[:,3])
        legend(['Simple Autopilot'])
        ylabel('forward velocity')
        subplot(3,1,3)
        plot(t,xvec[:,5])
        ylabel('yaw rate')
        xlabel('Time (s)')


        figure()
        plot(xvec[:,2],xvec[:,0],roadx,roady)
        #axis('equal')
        xlabel('East (m)')
        ylabel('North (m)')
        legend(['Simple Autopilot','road'])
        show()


    if opt==2:
        car = BicycleModel(autopilot_gain=.05,dT=0.01)
        car.x[0] = 0.5
        carmpc = BicycleModel()
        carmpc.x[0] = 0.5
        simtime = 20
        

        #now we will build a road upon which the car should drive. We will define a road by an X, a Y, an S, and a speed profile.
        granularity = .25 #meter.
        roadlength = 300
        roadx = arange(0,roadlength,granularity)
        roady = zeros(len(roadx))
        #now a speed profile. Make it constant for now.
        speedlimit =10 #m/s
        roadspeed = speedlimit*ones(len(roadx))
        #now put in a lane change halfway down the road that will last 2 sec
        lanewidth = 4 #meters
        LC_time = 4 #seconds
        LC_x = arange(0,speedlimit*LC_time,granularity) #this is how long in the x-direction the lane change should take
        LC_y = lanewidth/2*(1-cos(LC_x*(pi/(speedlimit*LC_time))))
        roady[roadlength/2:roadlength/2+len(LC_x)] = LC_y
        roady[roadlength/2+len(LC_x):]=lanewidth

        #now let's plot our road.
        figure()
        plot(LC_x,LC_y)
        figure()
        subplot(2,1,1)
        plot(roadx,roady)
        ylabel('road y-position (m)')
        subplot(2,1,2)
        plot(roadx,roadspeed)
        xlabel('road x-position (m)')
        ylabel('speed (m/s)')
        #show()

        #now let's simulate the car driving on said road with the simple steering autopilot and with MPC
        t = arange(0,simtime,car.dT)
        #we will assemble what we need for the MPC driver, and use the "farthest ahead" point to drive the simple autopilot.
        xvec = car.x
        xmpcvec = carmpc.x

        dt_predict = 0.1 #prediction timestep for MPC
        Nsteps = 10 #prediction horizon for MPC
        preview_time = dt_predict*Nsteps #seconds
        brake,gas,steer = 0,1,0
        unow = random.randn(10)
        steervec = zeros(len(t))
        steervec_mpc = zeros(len(t))


        for ind in range(1,len(t)):
            #first look up the y of the road
            if car.x[3]==0:
                #if car is not moving, pretend that it is so that preview vector doesn't go crazy.
                preview_dist_vector = arange(0,(Nsteps)*dt_predict,dt_predict)*0.1
            else:
                preview_dist_vector = arange(0,(Nsteps)*dt_predict,dt_predict)*car.x[3]

            #now figure out what the previewed vector of road y-positions is. Use interpolation for this.
            roadvec = interp(car.x[2]+preview_dist_vector,roadx,roady,left=0,right=0)
            speedvec = interp(car.x[2]+preview_dist_vector,roadx,roadspeed,left=0,right=0)
            if len(roadvec)<Nsteps:
                roadvec = roady[-1]*ones(len(preview_dist_vector))
                speedvec = speedlimit*ones(len(preview_dist_vector))
            #print len(preview_dist_vector)

            #update car. use a simple lookahead "lever arm" to pass as a path error.
            x,junk = car.euler_update(steer=0,gas=0,brake=0,cruise='on',autopilot='on',setspeed=speedvec[-1],patherror=(roadvec[-1]-(car.x[0]+preview_dist_vector[-1]*sin(car.x[4]))))
            
            if t[ind]/dt_predict==round(t[ind]/dt_predict): #only optimize input if .1 sec has passed
                #MPC_auto(xv,roadref,brake,gas,unow=None,Rsteer=1,Qroad=1,dT=0.1)
                
                brake = 0
                gas = carmpc.cruise(speedlimit)
                steer,unow = carmpc.MPC_auto(carmpc.x,roadvec,brake,gas,unow)#try the MPC algorithm
                #print("running MPC",t[ind]#,unow,roadvec
                #pause(1)
            steervec_mpc[ind] = steer
            #otherwise, leave gas, brake, and steer alone

            xmpc,junk = carmpc.euler_update(brake,gas,steer,cruise='off',autopilot='off')
            #print brake,gas,steer
            #print t[ind]
            xvec = vstack((xvec,x))
            xmpcvec = vstack((xmpcvec,xmpc))

        figure()
        subplot(3,1,1)
        plot(t,xvec[:,1],t,xmpcvec[:,1])
        ylabel('lateral velocity')
        subplot(3,1,2)
        plot(t,xvec[:,3],t,xmpcvec[:,3])
        legend(['Simple Autopilot','mpc'])
        ylabel('forward velocity')
        subplot(3,1,3)
        plot(t,xvec[:,5],t,xmpcvec[:,5])
        ylabel('yaw rate')
        xlabel('Time (s)')

        figure()
        plot(t,steervec_mpc)
        xlabel('Time (s)')
        ylabel('MPC steer angle (rad)')


        figure()
        plot(xvec[:,2],xvec[:,0],xmpcvec[:,2],xmpcvec[:,0],roadx,roady)
        #axis('equal')
        xlabel('East (m)')
        ylabel('North (m)')
        legend(['Simple Autopilot','mpc','road'])
        show()



    if opt ==1:
        car = BicycleModel()
        lincar = BicycleModel(tiretype='linear')
        simtime =10
        t= arange(0,simtime,car.dT)
        steeramp = .07
        steerfreq = .5*2*pi
        steervec = steeramp*sin(steerfreq*t)
        steervec[0:500]=0

        xvec = car.x
        xveclin = lincar.x

        for ind in range(1,len(t)):
            x,junk = car.euler_update(steer=steervec[ind])
            xlin,junk = lincar.euler_update(steer=steervec[ind])
            xvec = vstack((xvec,x))
            xveclin = vstack((xveclin,xlin))

        figure()
        plot(t,steervec)

        figure()
        subplot(3,1,1)
        plot(t,xvec[:,1],t,xveclin[:,1])
        ylabel('lateral velocity')
        subplot(3,1,2)
        plot(t,xvec[:,3],t,xveclin[:,3])
        legend(['Dugoff Tire','Linear Tire'])
        ylabel('forward velocity')
        subplot(3,1,3)
        plot(t,xvec[:,5],t,xveclin[:,5])
        ylabel('yaw rate')
        xlabel('Time (s)')


        figure()
        plot(xvec[:,2],xvec[:,0],xveclin[:,2],xveclin[:,0])
        axis('equal')
        xlabel('East (m)')
        ylabel('North (m)')
        legend(['Dugoff Tire','Linear Tire'])
        show()


