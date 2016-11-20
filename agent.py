import sensors
import brain
import numpy as np
import matplotlib.pyplot as plt
import sys

class agent:

  def __init__(_,x=1,y=1,ray_count=3,ray_width=20, ray_dist=.5, sensor_forward=True, show=False, heading=0):
    _.start_x = x
    _.start_y = y
    _.start_heading = heading 
    _.x_pos = x
    _.y_pos = y

    _.heading = heading # degrees 0 at (1,0) 90 at (0,1)

    _.sensor_forward = sensor_forward
    _.sensor = sensors.bounded_sensor(ray_count,ray_width,ray_dist,x,y)
    _.brain = brain.brain_nn()

    _.body_size = 10
    _.body_points = _.get_body_points()
    _.body_color = (0,0,0)
    _.show = show
    
  def connect_env(_,env):

    _.sensor.connect_env(env)
    _.env = env
 

  def observe(_):
    s = _.sensor.sense()
    sense_array = []
    for detect, dist in s:
      sense_array.append(int(detect))
      sense_array.append(dist)
    pos = [_.x_pos/_.env.width, _.y_pos/_.env.height]
    heading = [_.heading/30]
    return sense_array+pos+heading
  def step(_, action):

    pre_body_points = _.body_points

    _.head_heading(action['head_heading'])
    _.change_heading(action['change_heading'])
    
    post_body_points = _.body_points

    #detect whether the goal has been reached or a crash occured
    goal, crash = _.detect_goal_crash(pre_body_points, post_body_points)

    done = False
    reward = 0
    if goal or crash:
      done = True
      if goal:
        reward = 1
      else:
        reward = -1

    observations = _.observe()

    if _.env.show:
      _.env.update_draw()
    return observations, reward, done, None

  def reset(_):
    _.x_pos = _.start_x
    _.y_pos = _.start_y
    _.body_points = _.get_body_points()
    
    _.heading = _.start_heading
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

  def draw(_, draw, screen):
    #return agent object and sensor draw object
    _.draw_agent_obj(draw, screen)
    _.sensor.draw(draw, screen)

  def draw_agent_obj(_, draw, screen):
    draw.polygon(screen, _.body_color, _.body_points, 0)

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
      goal = _.env.goal.origin
      goal_radius = _.env.goal.radius
      if _.sensor.distance(p, goal) <= goal_radius:
        goal_achieved = True
    return goal_achieved, crash

  def simulate(_, delay=.2 ,states=None):
    if not states:
      states = _.last_states

    positions = states['positions']
    headings = states['headings']

    for i, pos in enumerate(positions):
      heading = headings[i]
      
    
    
