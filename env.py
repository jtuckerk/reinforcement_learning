import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import yaml

import pygame
import sys
  
from yaml import load, dump
try:
  from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
  from yaml import Loader, Dumper

GREEN = (0,255,0)
WHITE = (255,255,255)

def point_list_to_int(l):
  nl = []
  for p in l:
    nl.append((int(p[0]), int(p[1])))
    
  return nl


class env:
  
  def __init__(_, width, height, show=False):
    _.width=width
    _.height=height
    _.objects=[]
    _.agents = []
    _.agent_start = None
    _.size = (_.width,_.height)

    _.goal=None
    #environment boundaries
    _.show = show
    if show:
      pygame.init()
      _.screen = pygame.display.set_mode((width,height))
      _.screen.fill((255,255,255))
      pygame.display.update()
      
    _.bounds = _.rectangle((0,0), (width, height), is_border=True)
    _.objects.append(_.bounds)

  def create_goal(_, (x,y), radius):
    _.goal=_.circle((x,y), radius)

  def add_agent(_, agent):
    agent.connect_env(_)
    _.agents.append(agent)

  def add_circle(_,(x0,y0), r):
    _.objects.append(_.circle((x0,y0), r))

  def add_line(_, (p0x, p0y), (p1x,p1y)):
    _.objects.append(_.line((p0x,p1x), (p0y, p1y)))

  def add_rectangle(_,(x0,y0), (w,h)):
    _.objects.append(_.rectangle((x0,y0), (w,h)))

  def add_random_rectangle(_, mean_side_length, var):
    x = np.random.rand()*_.width
    y = np.random.rand()*_.height

    w = np.random.normal(mean_side_length, var, 1)[0]
    h = np.random.normal(mean_side_length, var, 1)[0]

    _.objects.append(_.rectangle((x,y), (w,h)))

  def add_random_polygon(_,radius, variance, sides):
    _.objects.append(_.random_polygon(radius, variance, sides, _.width, _.height))

  def draw_goal(_):
    _.goal.draw(pygame.draw, _.screen, GREEN)

  def draw(_):

    if _.show:
      _.update_draw()

  def update_draw(_):

    if _.show:
      _.screen.fill(WHITE)
      
      _.draw_goal()
      for o in _.objects:
        o.draw(pygame.draw, _.screen)
        
      for a in _.agents:
        a.draw(pygame.draw, _.screen)
    
      pygame.display.update()
    
  def load_from_yaml(_,filename):
    f = open(filename)
    # use safe_load instead load
    try:
      plan = yaml.safe_load(f)

      bounds = plan['bounds']
      _.width = bounds[0]
      _.height = bounds[1]
      _.objects[0] = _.rectangle((0,0), bounds, is_border=True)
      _.bounds = _.objects[0]
      
      if 'goal' in plan:
        g = plan['goal']
        _.create_goal(g['origin'], g['radius'])
      
      if 'agent_start' in plan:
        _.agent_start = plan['agent_start']


      for o in plan['objects']:
        o_type = o.keys()[0] #ugly
        vals = o[o_type]
        if o_type=='circle':
          _.add_circle(vals['origin'], vals['radius'])
        if o_type=='rectangle':
          _.add_rectangle(vals['origin'], vals['size'])
        if o_type=='random_polygon':
          _.add_random_polygon(vals['radius'], vals['variance'], vals['sides'])
        if o_type=='line':
          _.add_line(vals['p0'], vals['p1'])
    except Exception as e:
      print "failed to load environment from yaml: ", e

    f.close()
  class line:
    shape = 'line'

    color = (255,0,0)
    def __init__(_,(p0x,p0y),(p1x,p1y)):
      _.p0x = p0x
      _.p0y = p0y
      _.p1x = p1x
      _.p1y = p1y

    def draw_obj(_):
      return plt.Polygon([(_.p0x,_.p1x), (_.p0y, _.p1y)], lw=1, fc=_.color)
    def draw(_, draw, screen):
      pl = point_list_to_int(_.point_list())

      draw.line(screen, _.color, pl[0], pl[1] , 1)
    
    def get_sides(_):
      return [[(_.p0x,_.p1x), (_.p0y, _.p1y)]]

    def point_list(_):
      return [(_.p0x,_.p0y), (_.p1x, _.p1y)]

  class rectangle:
    shape = 'rectangle'
    color = (255,0,0)
    line_thickness = 2        
    def draw_obj(_):
      if _.is_border:

        return plt.Rectangle(_.origin, _.size[0],_.size[1],fill=None, lw=5, edgecolor='g')
      return plt.Rectangle(_.origin, _.size[0],_.size[1], fc=_.color)

    def draw(_, draw, screen):
      pl = [int(x) for x in [_.origin[0], _.origin[1], _.size[0], _.size[1]]]

      if _.is_border:
        color = GREEN
        thick = 2
      else:
        color = _.color
        thick = 0
      draw.rect(screen,
                color,
                pl,
                thick)

    def get_sides(_):
      return [(_.origin, (_.origin[0]+_.size[0], _.origin[1])),
          (_.origin, (_.origin[0], _.origin[1]+_.size[1])),
          ((_.origin[0]+_.size[0], _.origin[1]), (_.origin[0]+_.size[0], _.origin[1]+_.size[1])),
          ((_.origin[0],_.origin[1]+_.size[1]), (_.origin[0]+_.size[0], _.origin[1]+_.size[1]))]

    def __init__(_, (x0,y0), (width, height), is_border=False):
      _.origin = (x0,y0)
      _.size = [width,height]
      _.is_border = is_border

    def is_inside(_,x,y):
      return (x>=_.origin[0] and x<=_.origin[0]+_.size[0] and y>=_.origin[1] and y<=_.origin[1]+_.size[1])

  class circle:
    shape = 'circle'
    color = (255,255,0)
    line_thickness = 2
    def draw(_, draw, screen, color=None):
      color = color or _.color

      draw.circle(screen,
                  color,
                  point_list_to_int([_.origin])[0],
                  int(_.radius))
      
    def draw_obj(_):
      return plt.Circle(_.origin, radius=_.radius, fc=_.color)
    def __init__(_, (x0,y0), r):
      _.origin = (x0, y0)
      _.radius = r

    def is_inside(_, x,y):
      return math.sqrt((_.origin[0]-x)**2 + (_.origin[1]-y)**2) <= _.radius

  class random_polygon:
    # place objects about the map according to a uniform distribution
    # give them shape about a point according to normal distribution
    shape = 'random_polygon'
    side_list = []
    def unif(_):
      return np.random.rand()

    def gaus(_,var, mean):
      return np.random.normal(mean, var, 1)[0]

    def draw(_, draw, screen):
      pl = point_list_to_int(_.get_sides_lines())
      draw.polygon(screen,
                   _.color,
                   pl, 0)
      
    def draw_obj(_):
      return plt.Polygon(_.get_sides_lines(), fc=_.color)

    def __init__(_, radius, variance, sides, width, height):
      _.side_list = []
      _.radius = radius # approximate size
      _.variance = variance
      _.sides=sides
      _.x = _.unif()*width
      _.y = _.unif()*height
      _.color = (255,0,0)

      s1 = _.gaus(.5, 0)
      s2 = _.gaus(.5, 0)
      s1=1 if s1>0 else -1
      s2=1 if s2>0 else -1
      p1 = _.x+s1*_.gaus(.1,_.radius)*np.cos(np.pi/4), _.y+s2*_.gaus(.1,_.radius)*np.cos(np.pi/4)
      first_point = p1

      for side in range(sides-1):
        #determine angle ~roughly tangent to circle about center point
        x1,y1 = _.new_point(p1, (_.x,_.y), _.variance, _.radius, _.sides)
        _.side_list.append(((p1[0],p1[1]),(x1,y1)))
        p1 = (x1,y1)
      _.side_list.append((p1, first_point))

    def new_point(_,p1, p0, variance, radius, sides):
      rise = p1[1]-p0[1]
      run = p1[0]-p0[0]
      ang = np.rad2deg(np.arctan2(rise,run))
      tang_ang = ((ang+90)%360)

      mean_side_length = 2*radius*np.sin(np.pi/sides)
      side_mag = _.gaus(variance*mean_side_length, mean_side_length)
      new_ang=_.gaus(variance*90, tang_ang+(180.0/sides))
      dx = side_mag*np.cos(new_ang/180.0*np.pi)
      dy = side_mag*np.sin(new_ang/180.0*np.pi)

      x1 = p1[0]+dx
      y1 = p1[1]+dy
      return x1,y1

    def get_sides_lines(_):
      return [x[0] for x in _.get_sides()]

    def get_sides(_):
      return _.side_list

  class create_env:
    def __init__(_,env):

      _.fig, _.ax = plt.subplots()
      _.press=None
      _.x0 = None
      _.y0 = None
      _.x1 = None
      _.y1 = None
      _.goal=None
      _.objects = []
      _.cur_obj = None

      _.start_loc = (0,0)
      _.fig.canvas.mpl_connect('button_press_event', _.on_click)
      _.fig.canvas.mpl_connect('button_release_event', _.on_release)
      _.fig.canvas.mpl_connect('motion_notify_event', _.on_motion)

      _.fig.canvas.mpl_connect('key_press_event', _.key_press)

      _.fig.title = "dont draw outside the white!"

      _.bounds = [env.width, env.height]
      border_w = env.width*.2
      border_h = env.height*.2
      _.ax.set_autoscale_on(False)
      _.ax.axis([0-border_w,env.width+border_w,0-border_h,env.height+border_h])
      _.fig.gca().add_patch(env.bounds.draw_obj())

      _.key='r'
      _.label='Rectangle Draw'
      _.fig.suptitle(_.label, fontsize=20)

      plt.show()

    def on_click(_, event):
      _.x0 = event.xdata
      _.y0 = event.ydata

      if _.key == 'r':
        
        _.cur_obj = plt.Rectangle((_.x0,_.y0), 0, 0)
        _.ax.add_patch(_.cur_obj)

      if _.key == 'i':
        _.cur_obj = plt.Line2D((0,0), (0, 0), lw=2)
        _.ax.add_line(_.cur_obj)


      if _.key == 'g':
        _.cur_obj = plt.Circle((_.x0, _.y0), 0, fc='g')
        _.ax.add_patch(_.cur_obj)


      if _.key == 'x':
        start_loc = (_.x0, _.y0)
        plt.plot(_.x0,_.y0,'ro')

      _.press = event.xdata, event.ydata

      _.ax.figure.canvas.draw()

    def on_release(_, event):
      _.press = None

      _.x1 = event.xdata
      _.y1 = event.ydata

      if _.key =='r':

        _.cur_obj.set_width(_.x1 - _.x0)
        _.cur_obj.set_height(_.y1 - _.y0)
        _.cur_obj.set_xy((_.x0, _.y0))
        _.objects.append(('rectangle',_.cur_obj))

      if _.key == 'i':

        _.cur_obj.set_data((_.x0,_.x1), (_.y0,_.y1))
        _.objects.append(('line',_.cur_obj))

      if _.key == 'g':
        rad = np.linalg.norm(np.array([_.x1,_.y1])- np.array([_.x0,_.y0]))
        _.cur_obj.set_radius(rad)
        del _.goal
        _.goal = _.cur_obj


      _.ax.figure.canvas.draw()


    def on_motion(_, event):
      if _.press == None:
        return

      _.x1 = event.xdata
      _.y1 = event.ydata
      if _.key =='r':

        _.cur_obj.set_width(_.x1 - _.x0)
        _.cur_obj.set_height(_.y1 - _.y0)
        _.cur_obj.set_xy((_.x0, _.y0))

      if _.key == 'i':

        _.cur_obj.set_data((_.x0,_.x1), (_.y0,_.y1))

      if _.key == 'g':
        rad = np.linalg.norm(np.array([_.x1,_.y1])- np.array([_.x0,_.y0]))
        _.cur_obj.set_radius(rad)

      _.ax.figure.canvas.draw()


    def key_press(_, event):

      if event.key not in ['r','i','g', 'a', 'x'] or _.press!=None:
        return

      _.key = event.key

      if _.key == 'r':
        _.label = 'Rectangle Draw'
      if _.key == 'g':
        _.label = 'Place Goal'
      if _.key == 'i':
        _.label = 'Line Draw'
      if _.key == 'x':
        _.label = 'Agent Start Location'
      if _.key =='a':
        _.save_env()

      _.fig.suptitle(_.label, fontsize=20)
      _.ax.figure.canvas.draw()

    def save_env(_):
      plan = {'bounds':None,
          'objects':[],
          'goal':{'origin':None, 'radius':None},
          'agent_start':None}

      plan['bounds'] = _.bounds
      if _.goal:
        plan['goal']['origin'] = [float(_.goal.center[0]), float(_.goal.center[1])]
        plan['goal']['radius'] = float(_.goal.radius)
      if _.start_loc:
        plan['agent_start'] = list(_.start_loc)

      for obj_type, obj in _.objects:

        o={obj_type:{}}
        if obj_type == 'rectangle':
          o[obj_type]['origin'] = [float(obj.xy[0]), float(obj.xy[1])]
          o[obj_type]['size'] = [float(obj.get_width()), float(obj.get_height())]

        if obj_type == 'line':
          p1, p2 = zip(*obj.get_data())
          p1 = [float(p1[0]), float(p1[1])]
          p2 = [float(p2[0]), float(p2[1])]
          o[obj_type]['p0']=p1
          o[obj_type]['p1']=p2

        plan['objects'].append(o)

      output = dump(plan, Dumper=Dumper)

      with open('data.yml', 'w') as outfile:
        yaml.dump(plan, outfile, default_flow_style=False)
      

