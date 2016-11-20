import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math

def ray_intersects_circle((Ax, Ay), (Bx, By), (Cx, Cy), radius): #A start B end

  E = np.array([Ax, Ay]) 
  L = np.array([Bx, By])
  d = L-E

  C = np.array([Cx, Cy])

  r = radius
  f = E-C
  a = d.dot( d ) ;
  b = 2*f.dot( d ) ;
  c = f.dot( f ) - r*r ;

  discriminant = b*b-4*a*c;
  if( discriminant < 0 ):
    return False,0
  else:

   discriminant = math.sqrt( discriminant );

   # either solution may be on or off the ray so need to test both
   # t1 is always the smaller value, because BOTH discriminant and
   # a are nonnegative.
   t1 = (-b - discriminant)/(2*a);
   t2 = (-b + discriminant)/(2*a);

   # 3x HIT cases:
   #     -o->       --|--> |      | --|->
   # Impale(t1 hit,t2 hit), Poke(t1 hit,t2>1), ExitWound(t1<0, t2 hit), 

   # 3x MISS cases:
   #    -> o           o ->       | -> |
   # FallShort (t1>1,t2>1), Past (t1<0,t2<0), CompletelyInside(t1<0, t2>1)

   if( t1 >= 0 and t1 <= 1 ):
     # t1 is the intersection, and it's closer than t2
     # (since t1 uses -b - discriminant)
     # Impale, Poke

     return True, get_intersect_distance_circle(E,L,C,r) ;


   # here t1 didn't intersect so we are either started
   # inside the sphere or completely past it
   if( t2 >= 0 and t2 <= 1 ):
     # ExitWound
    
     return True, get_intersect_distance_circle(E,L,C,r) ;


   # no intn: FallShort, Past, CompletelyInside
   
   return False,0 ;

def distance(a,b):
  return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)  

# A is ray origin B is Ray end C is circle center
def get_intersect_distance_circle((Ax,Ay),(Bx,By), (Cx, Cy), radius):

  #####################################################################
  # compute the euclidean distance between A and B             
  LAB = math.sqrt( (Bx-Ax)**2+(By-Ay)**2)                       # compute the direction vector D from A to B
  Dx = (Bx-Ax)/LAB                             
  Dy = (By-Ay)/LAB                             

  # compute the value t of the closest point to the circle center (Cx, Cy) 
  t = Dx*(Cx-Ax) + Dy*(Cy-Ay)                              # This is the projection of C on the line from A to B.         
  # compute the coordinates of the point E on line and closest to C    
  Ex = t*Dx+Ax                               
  Ey = t*Dy+Ay                                     # compute the euclidean distance from E to C               
  LEC = math.sqrt( (Ex-Cx)**2+(Ey-Cy)**2 )                       # test if the line intersects the circle
  if( LEC < radius ):                           
    # compute distance from t to circle intersection point
    dt = math.sqrt( radius**2 - LEC**2)                 

    # compute first intersection point                  
    Fx = (t-dt)*Dx + Ax                         
    Fy = (t-dt)*Dy + Ay
    # compute second intersection point
    Gx = (t+dt)*Dx + Ax
    Gy = (t+dt)*Dy + Ay

    #dist A to G is actually the one we want maybe more to check
    
    return distance((Ax,Ay),(Gx,Gy))


def line_intersection(line1, line2):
  xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
  ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])


  def det(a, b):
    return a[0] * b[1] - a[1] * b[0]

  div = det(xdiff, ydiff)
  if div == 0:

    return (False, (-1,-1))

  d = (det(*line1), det(*line2))
  x = det(d, xdiff) / div
  y = det(d, ydiff) / div
  return (True, (x, y))



epsilon = .0001
def is_between(a, c, b):
  crossproduct = (c[1] - a[1]) * (b[0] - a[0]) - (c[0] - a[0]) * (b[1] - a[1])
  if abs(crossproduct) > epsilon : return False  # (or != 0 if using integers)
  dotproduct = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1])*(b[1] - a[1])
  if dotproduct < 0 : return False
  
  squaredlengthba = (b[0] - a[0])*(b[0] - a[0]) + (b[1] - a[1])*(b[1] - a[1])
  if dotproduct > squaredlengthba: return False
  
  return True

  
def ray_intersects_polygon((Ax, Ay), (Bx, By), sides):
  A=(Ax, Ay)
  B=(Bx, By)
  closest = (0,0)
  intersect = False
  dist = 0#ugly
  for side in sides:
    b, li = line_intersection((A,B), side)

    if is_between(A,li,B) and is_between(side[0], li, side[1]):
      new_dist = distance(A,li)

      if not intersect or new_dist < dist:

        closest = li
        dist=new_dist

        intersect=True
        
  return intersect,dist


class bounded_sensor:

  goal_dist = .2
  def distance(_,a,b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)  
  def __init__(_, ray_count, ray_width, ray_length, x_pos, y_pos):
    _.ray_count = ray_count 
    _.ray_length = ray_length
    _.x_pos= x_pos
    _.y_pos= y_pos
    _.ray_width = ray_width #degrees
    _.ray_angle = 0 # degrees

  def set_ray_angle(_, angle): #degrees
    _.ray_angle = angle

  def set_pos(_, x, y):
    _.x_pos = x
    _.y_pos = y

  def get_ray_lines(_):

    #clockwise most ray is half the width from the center (ray angle)
    angles = []
    if _.ray_count == 1:
      angle_between = 0
    else:
      angle_between = 1.0*_.ray_width/(_.ray_count-1)


    start_angle = (_.ray_angle-_.ray_width/2.0)%360


    lines = []
    for i in range(_.ray_count):

      angle = start_angle+i*angle_between
      rad_angle = np.deg2rad(angle)


      dx = _.ray_length*np.cos(rad_angle)
      dy = _.ray_length*np.sin(rad_angle)
      
      lines.append(((_.x_pos,_.y_pos), (_.x_pos+dx, _.y_pos+dy)))


    return lines 
  def ray_visual_lines(_):
    lines = []
    for x in _.get_ray_lines():
      lines.append(x[0])
      lines.append(x[1])
    return lines

  def draw(_, draw, screen):
    lines = [(int(x[0]), int(x[0])) for x in  _.ray_visual_lines()]
    
    draw.lines(screen, (0,0,0), False, _.ray_visual_lines(), 1)

  # each ray returns true or false and a distance to the intersection
  def ray_collisions(_, obj_list, ray_lines):

    sensor_output = []
    collision = False

    #todo migrate this
    #goal = _.distance(_.goal.center, (_.x_pos,_.y_pos)) < _.goal.radius
    
    
    for ray in ray_lines:
      i= False
      d = _.ray_length+1 # make sure we find the closest to the sensor
      for obj in obj_list:

        if obj.shape == 'circle':
          intersect, dist = ray_intersects_circle(ray[0], ray[1], obj.origin, obj.radius)
          #not gonna worry about circles cuz ray stuff is messed up
          if intersect and dist<d:
            d=dist
          
            i=True
        else:
          intersect, dist = ray_intersects_polygon(ray[0], ray[1], obj.get_sides())
          if intersect and dist < d:
            d=dist
            i=True

      sensor_output.append((i,d/_.ray_length))
    return sensor_output
  def connect_env(_,env):
    _.env_objects = env.objects
    _.goal = env.goal

  def sense(_):
    ray_lines = _.get_ray_lines()
    return _.ray_collisions(_.env_objects, ray_lines)
