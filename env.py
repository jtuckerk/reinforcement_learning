import math
import numpy as np

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

def distance(a,b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

epsilon = .0001
def is_between(a, c, b):
    crossproduct = (c[1] - a[1]) * (b[0] - a[0]) - (c[0] - a[0]) * (b[1] - a[1])
    if abs(crossproduct) > epsilon : return False   # (or != 0 if using integers)
    dotproduct = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1])*(b[1] - a[1])
    if dotproduct < 0 : return False
    
    squaredlengthba = (b[0] - a[0])*(b[0] - a[0]) + (b[1] - a[1])*(b[1] - a[1])
    if dotproduct > squaredlengthba: return False
    
    return True
def is_Between(a,c,b):
    print distance(a,c) + distance(c,b) 
    print distance(a,b)
    return distance(a,c) + distance(c,b) == distance(a,b)

class env:
    width=10
    height=10

    size = (width,height)

    goal=(width,height)
    
    objects=[]

    def __init__(_, width, height):
        _.width=width
        _.height=height



    class rectangle:
        origin = (0,0) #bottom left
        size = (1,1) # width,height
    
        sides= [(origin, (origin[0]+size[0], origin[1])),
                (origin, (origin[0], origin[1]+size[1])),
                ((origin[0]+size[0], origin[1]), (origin[0]+size[0], origin[1]+size[1])),
                ((origin[0],origin[1]+size[1]), (origin[0]+size[0], origin[1]+size[1]))]

        def is_inside(_,x,y):
            return (x>=_.origin and x<=_.origin+_.size[0] and y>=_.origin and y<=_.origin+_.size[1])

        def ray_intersects(_, (Ax, Ay), (Bx, By)):
            A=(Ax, Ay)
            B=(Bx, By)
            closest = (0,0)
            dist = False
            for side in _.sides:
                b, li = line_intersection((A,B), side)

                if is_between(A,li,B) and is_between(side[0], li, side[1]):
                    new_dist = distance(A,li)

                    if not dist or new_dist < dist:

                        closest = li
                        dist=new_dist

            return dist, closest
    class circle:
        origin = (0,0) #bottom left
        radius = 1 # width,height

        def is_inside(_, x,y):
            return math.sqrt((_.origin[0]-x)**2 + (_.origin[1]-y)**2) <= _.radius

        def ray_intersects(_, (Ax, Ay), (Bx, By)):
            E = np.array([Ax, Ay]) 
            L = np.array([Bx, By])
            d = L-E
            Cx = _.origin[0]
            Cy = _.origin[1]
            C = np.array([Cx, Cy])

            r = _.radius
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
              #          -o->             --|-->  |            |  --|->
              # Impale(t1 hit,t2 hit), Poke(t1 hit,t2>1), ExitWound(t1<0, t2 hit), 

              # 3x MISS cases:
              #       ->  o                     o ->              | -> |
              # FallShort (t1>1,t2>1), Past (t1<0,t2<0), CompletelyInside(t1<0, t2>1)

              if( t1 >= 0 and t1 <= 1 ):
                  # t1 is the intersection, and it's closer than t2
                  # (since t1 uses -b - discriminant)
                  # Impale, Poke
                  print "poke","t1:", t1, "t2:",t2
                  return True, _.get_intersect_point(E,L,C,r) ;
                  

              # here t1 didn't intersect so we are either started
              # inside the sphere or completely past it
              if( t2 >= 0 and t2 <= 1 ):
                  # ExitWound
                  print "exit:","t1:", t1, "t2:",t2
                  return True, _.get_intersect_point(E,L,C,r) ;
                  

              # no intn: FallShort, Past, CompletelyInside
              print t1,t2
              return False ;



        def get_intersect_point(_,(Ax,Ay),(Bx,By), (Cx, Cy), radius):

            #####################################################################
            # compute the euclidean distance between A and B                          
            LAB = math.sqrt( (Bx-Ax)**2+(By-Ay)**2)                                   
                                                                                      
            # compute the direction vector D from A to B                              
            Dx = (Bx-Ax)/LAB                                                          
            Dy = (By-Ay)/LAB                                                          
                                                                                      
            # Now the line equation is x = Dx*t + Ax, y = Dy*t + Ay with 0 <= t <= 1. 
                                                                                      
            # compute the value t of the closest point to the circle center (Cx, Cy)  
            Cx = _.origin[0]                                                          
            Cy = _.origin[1]                                                          
            t = Dx*(Cx-Ax) + Dy*(Cy-Ay)                                               
                                                                                      
            # This is the projection of C on the line from A to B.                    
                                                                                      
            # compute the coordinates of the point E on line and closest to C         
            Ex = t*Dx+Ax                                                              
            Ey = t*Dy+Ay                                                              
                                                                                      
            # compute the euclidean distance from E to C                              
            LEC = math.sqrt( (Ex-Cx)**2+(Ey-Cy)**2 )                                  
                                                                                      
            # test if the line intersects the circle                                  
            if( LEC < radius ):                                                     
                # compute distance from t to circle intersection point                
                dt = math.sqrt( radius**2 - LEC**2)                                 
                                                                                      
                # compute first intersection point                                    
                Fx = (t-dt)*Dx + Ax                                                   
                Fy = (t-dt)*Dy + Ay                                                   
                                                                                      
                # compute second intersection point                                   
                #Gx = (t+dt)*Dx + Ax
                #Gy = (t+dt)*Dy + Ay
            
                return (Fx, Fy)


    class randomShape:
        # place objects about the map according to a uniform distribution
        # give them shape about a point according to normal distribution
        side_list = []
        def unif(_):
            return np.random.rand()
        def gaus(_,var, mean):
            return np.random.normal(mean, var, 1)[0]

        def __init__(_, radius, variance, sides, width, height):
            _.side_list = []
            _.radius = radius # approximate size
            _.variance = variance
            
            _.x = _.gaus(.0001, width/2)
            _.y = _.gaus(.0001, height/2)
            print _.x, _.y
            #_.x = _.unif()*width
            #_.y = _.unif()*height

            p1 = _.x+_.gaus(variance*radius,radius)*np.cos(np.pi/4), _.y+_.gaus(variance*radius,radius)*np.cos(np.pi/4)
            first_point = p1


            for side in range(sides-1):
                #determine angle ~roughly tangent to circle about center point
                rise = p1[1]-_.y 
                run = p1[0]-_.x
                
                tang_ang = np.arctan(1.0*rise/run)*180/np.pi
                if run > 0:
                    tang_ang+=90
                elif rise >0:
                    tang_ang+=270

#                tang_ang += (180*(sides-2)/(2*(sides**2)))
                mean_side_length = 2*radius*np.sin(np.pi/sides)
                side_mag =  _.gaus(variance*mean_side_length, mean_side_length)
                dx = side_mag*np.cos(_.gaus(variance*90, tang_ang)/180.0*np.pi)
                dy = side_mag*np.sin(_.gaus(variance*90, tang_ang)/180.0*np.pi)
                
                x1 = p1[0]+dx
                y1 = p1[1]+dy

                print side
                _.side_list.append(((p1[0],p1[1]),(x1,y1)))
                p1 = (x1,y1)

            _.side_list.append((p1, first_point))

# + + : + 90
# - + : +270
# + - : + 90
# - - : 0
