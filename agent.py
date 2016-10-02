import sensors
import brain
import numpy as np
import matplotlib.pyplot as plt
import sys

class agent:

    def __init__(_,x=1,y=1,ray_count=3,ray_width=20, ray_dist=.5, sensor_forward=True):
        _.x_pos = x
        _.y_pos = y

        _.heading = 0.0 # degrees 0 at (1,0) 90 at (0,1)

        _.sensor_forward = sensor_forward
        _.sensor = sensors.bounded_sensor(ray_count,ray_width,ray_dist,x,y)
        _.brain = brain.brain_keyboard(_)

        _.body_size = .1
        _.body_points = _.get_body_points()
        
    def connect_env(_,env):
        _.brain.connect_env(env)
        _.sensor.connect_env(env)
        _.env = env
        
    def step(_):

        pre_body_points = _.body_points
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

        post_body_points = _.body_points

        #detect whether the goal has been reached or a crash occured
        goal, crash = _.detect_goal_crash(pre_body_points, post_body_points)

        if goal or crash:
            print goal, crash
        sys.stdout.flush()
        _.env.update_draw()

    def move(_, dx, dy):
        _.x_pos+=dx
        _.y_pos+=dy
        _.body_points = _.get_body_points()
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

        _.body_points = _.get_body_points()
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
        return [_.sensor.draw_obj(), _.draw_agent_obj() ]

    def draw_agent_obj(_):
        return plt.Polygon( _.body_points, fc='black')

    def get_body_points(_):
        points = []
        diag_mag = np.sqrt(2*(_.body_size**2))
        for i in range(4):
            angle = _.heading - 45 -90*(i)
            rad = np.deg2rad(angle)
            x = diag_mag*np.cos(rad)+_.x_pos
            y = diag_mag*np.sin(rad)+_.y_pos

            points.append((x,y))

        return points
        

    def detect_goal_crash(_, pre, post):
        rays = list(zip(pre,post))
        for i in range(len(post)-1):
            rays.append(post[i:i+2])

        rays.append([post[len(post)-1],post[0]])
        intersections = _.sensor.ray_collisions(_.env.objects, rays)

        crash = False
        for intersect_bool, dist in intersections:
            if intersect_bool:
                crash = True

        goal_achieved = False
        for p in post:
            goal = _.env.goal.center
            goal_radius = _.env.goal.radius
            if _.sensor.distance(p, goal) <= goal_radius:
                goal_achieved = True
        return goal_achieved, crash


        
