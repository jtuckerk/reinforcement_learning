import sensors
import brain
import numpy as np
class agent:

    def __init__(_,x=1,y=1,ray_count=3,ray_width=20, ray_dist=.5, sensor_forward=True):
        _.x_pos = x
        _.y_pos = y

        _.heading = 0.0 # degrees 0 at (1,0) 90 at (0,1)

        _.sensor_forward = sensor_forward
        _.sensor = sensors.bounded_sensor(ray_count,ray_width,ray_dist,x,y)
        _.brain = brain.brain_keyboard(_)

    def connect_env(_,env):
        _.brain.connect_env(env)
        _.sensor.connect_env(env)
        _.env = env
        
    def step(_):

        #sense
        env_view = _.sensor.sense()
        #input to brain
        _.brain.read_input(env_view)
        #get output from brain
        o =  _.brain.output()
        #update pos and sensor

        key = o[0]
        if key=='up':
            _.head_heading(.2)
        if key=='down':
            _.head_heading(-.2)
        if key=='left':
            _.change_heading(10.0)
        if key=='right':
            _.change_heading(-10.0)
            
            
        _.env.update_draw()
    
    def move(_, dx, dy):
        _.x_pos+=dx
        _.y_pos+=dy

        _.sensor.set_pos(_.x_pos, _.y_pos)

        if (_.sensor_forward):
            ang = np.rad2deg(np.arctan2(dy,dx))%360
            _.sensor.ray_angle = ang
            #point sensor in direction of motion
            #np.arctan2(run,rise

    def change_heading(_, angle):
        _.heading+=angle
        #shouldnt need this 
        if _.sensor_forward:
            _.sensor.ray_angle = _.heading
    
    #head mag (+-) in direction of heading
    def head_heading(_,mag):

        rad = np.deg2rad(_.heading)
        x_mag = mag*np.cos(rad)
        y_mag = mag*np.sin(rad)
        _.move(x_mag,y_mag)

    #point to specific angle
    def point_sensor(_, abs_angle):
        _.sensor.set_ray_angle(abs_angle)


    def turn_sensor(_, d_theta):
        _.sensor.ray_angle += d_theta

    def draw_objs(_):
        #return agent object and sensor draw object
        return [_.sensor.draw_obj()]

        
