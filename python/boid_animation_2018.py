#kaitai
#2018/06/26
'''README.txt
kaitai
2018/06/26

Report for boid simulation:

The simulation is made with Python version 3.5.

required Python packages:
numpy
matplotlib

The returnables include:
readme
python file
simple animation

The script:
The script can be run in the command prompt by command "py -3.5 boid_animation_2018.py". (Requires Python 3.5 and packages mentioned above.)
There is no way to pass command line arguments but the modifications must be done in the code to change boid count, spawning area, altering the rule weights and so on.
(There initial goal was to make a  better GUI for it but unexpected problems with tkinter took lot of time. 
The GUI implementation is not included since it's not providing much additional functionality at this point.)

The scripts simulates boid movement in a window in real-time. They will gather up and start going right with the current parameters. 
They can be followed manually by panning or zooming the view.
The view will be automatically scaled when more boids created in the beginning. Also, many behavioural properties are affected by the boid count,
so that the visualization looks better even when 1000 boids are in the place. The tested boid counts were ranging from 10 to 3000. 
High number of boids caused much lag though (and eventually the program ran out of memory).

Boids:
The boid count can be initialized
The boid positions are initialized by uniform distribution in the specified area (point/rectangle).
The initial average speed defines the global movement.
And more.

The boids follow three rules:
They match velocity to neighbours.
They move towards the global middle point of the boids.
They avoid collisions with each other.

At this point, the collision avoidance has the highest impact to the behaviour.


Other:
The code was initially adopted on the internet, but I realized there was many things to improve (which I did do). 
However, the references are still included in the code and it is well (excessively) commented.

'''

#the ideas adopted from http://github-pages.ucl.ac.uk/rsd-engineeringcourse/ch01data/084Boids.html

#NOTE:  the code will have many (excess) commenting for I will remember what everything does
#       also after a year.

#for fast calculations
import numpy as np

#for animations
from matplotlib import animation
from matplotlib import pyplot as plt

#for GUI
#import tkinter as Tk
#from tkinter import canvas
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#limit the particle count
particle_count = 5

MAX_VELOCITY = 50 #define max velocity for particles
AVG_X_VEL = 30
AVG_Y_VEL = 0

#limit the area (in 2D space)
limits_x = 10000 + min(int(particle_count/10)*1000, 10000)
limits_y = 10000 + min(int(particle_count/10)*1000,10000)
area_limits = np.array([limits_x+5000,limits_y])

#area_limits = np.array([50000,15000]) #hard coded values (the particles may appear outside the figure)



#Define particle spawning area

####around middle, close to y-axis
##part_lim_lower = [limits_x/5, limits_y/2 - min(particle_count*20, 2000)] 
##part_lim_upper = [limits_x/5 + min(particle_count*2*20, 4000), limits_y/2 + min(particle_count*20, 2000)]

####everywhere within the limits
part_lim_lower = [0,0]
part_lim_upper =area_limits

#### All spawn in the middle point
##part_lim_lower = area_limits/2
##part_lim_upper =area_limits/2

def new_particles(count, lower_bounds, upper_bounds):
    '''
    Creates new particles and randomizes the locations within initial bounds.

    Bounds are defined for each dimensions separately
    '''
    width = upper_bounds - lower_bounds
    return (lower_bounds[:,np.newaxis] + np.random.rand(2, count) * width[:, np.newaxis])


#initializes x and y points for as many particles as defined in particle_count (newaxis uses area limit dimension) randomly
positions=new_particles(particle_count, np.array(part_lim_lower), np.array(part_lim_upper))

#initializes velocities
velocities=new_particles(particle_count, np.array([-20+AVG_X_VEL,-20+AVG_Y_VEL]), np.array([20+AVG_X_VEL,20+AVG_Y_VEL]))

#create figure for animation
colors = np.resize(['b','r','g'], particle_count)
figure = plt.figure()
axes = plt.axes(xlim=(0, area_limits[0]), ylim=(0, area_limits[1]), facecolor = '#DFDFDF')
scatter=axes.scatter(positions[0,:],positions[1,:], marker='o', edgecolor='#333333', lw=0.5, c=colors)



def update_boids(positions, velocities):

       
    #calculate the essentials
    middle=np.mean(positions, 1)
    
    separations = positions[:,np.newaxis,:] - positions[:,:,np.newaxis]
    squared_displacements = separations * separations
    square_distances = np.sum(squared_displacements, 0)

    velocity_differences = velocities[:,np.newaxis,:] - velocities[:,:,np.newaxis]

    #velocity matching
    formation_flying_distance = 5000 + 10 * particle_count
    very_far = square_distances > formation_flying_distance * formation_flying_distance
    velocity_differences_if_close = np.copy(velocity_differences)
    velocity_differences_if_close[0,:,:][very_far] = 0
    velocity_differences_if_close[1,:,:][very_far] = 0
    
    #move to middle point of the particles
    direction_to_middle = positions - middle[:, np.newaxis]

    #collision avoidance
    personal_space = int(max(500,10*MAX_VELOCITY)+500/min(5,particle_count))
    far_away = square_distances > personal_space*personal_space
    separations_if_close = np.copy(separations)
    separations_if_close[0,:,:][far_away] = 0
    separations_if_close[1,:,:][far_away] = 0
    
    #___________________WEIGHTS
    #the weights for each rule: (calculations based on the situation)
    #velocity matching, move to middle, collision avoidance

    formation_flying_strength = 1
    #with high values, particles get stuck / they stick to the formation,
    #low makes them wander around more and not to move the desired direction(try 1 ... 0.01)

    move_to_middle_strength = 0.2/particle_count #more particles --> less room in center --> use inverse relationship

    collision_avoid_strength = 0.05#1
    #higher value makes clumps to spread out faster but causes more extra movement after there is enough personal space for the particles
    #lower values may cause some particles to remain on top of each other and never take their own space.
    
    #update velocities
    velocities -= np.mean(velocity_differences_if_close, 1) * formation_flying_strength
    velocities -= direction_to_middle * move_to_middle_strength
    velocities += np.sum(separations_if_close, 1)*collision_avoid_strength

    #limit speed      
    clipped_vel = np.clip(velocities,-MAX_VELOCITY,MAX_VELOCITY)#limit max velocities
    
    #add random velocity to make them "living"
    v = 10 #variation
    additive_noise = np.random.rand(2, particle_count)*np.array([v,v])[:,np.newaxis]-v/2

    #actual move
    positions += clipped_vel+additive_noise

    
    
def animate(frame):
    update_boids(positions, velocities)
    scatter.set_offsets(positions.transpose())


#create animation
anim=animation.FuncAnimation(figure, animate,
                        np.arange(1, 200), interval=30)

plt.show()


#to create animation - download from https://www.ffmpeg.org/download.html
#and save ffmpeg to the same folder with this python file
#then uncomment following lines and you can make file for the animation.
##FFwriter = animation.FFMpegWriter(fps=30)
##anim.save('basic_animation.mp4', writer = FFwriter)

