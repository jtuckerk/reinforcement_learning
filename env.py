import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import yaml

class env:
    width=10
    height=10

    size = (width,height)

    goal=(width,height)
    
    objects=[]

    agents = []
    
    def __init__(_, width, height):
        _.width=width
        _.height=height

        #environment boundaries

        bounds = _.rectangle((0,0), (width, height), is_border=True) 
        _.objects.append(bounds)

    def add_circle(_,(x0,y0), r):
        _.objects.append(_.circle((x0,y0), r))

    def add_rectangle(_,(x0,y0), (w,h)):
        _.objects.append(_.rectangle((x0,y0), (w,h)))

    def add_random_polygon(_,radius, variance, sides):
        _.objects.append(_.random_polygon(radius, variance, sides, _.width, _.height))

    def draw(_):
        plt.axes()
        for o in _.objects:
            plt.gca().add_patch(o.draw_obj())

        for a in _.agents:
            for o in a.draw_objs():
                plt.gca().add_patch(o)
        plt.axis('scaled')
        plt.show()

    def load_from_yaml(_,filename):
        f = open(filename)
        # use safe_load instead load
        try:
            plan = yaml.safe_load(f)

            bounds = plan['bound']
            _.width = bounds[0]
            _.height = bounds[1]
            _.objects[0] = _.rectangle((0,0), bounds, is_border=True)


            for o in plan['objects']:
                o_type = o.keys()[0] #ugly
                vals = o[o_type]
                if o_type=='circle':
                    _.add_circle(vals['origin'], vals['radius'])
                if o_type=='rectangle':
                    _.add_rectangle(vals['origin'], vals['size'])
                if o_type=='random_polygon':
                    _.add_random_polygon(vals['radius'], vals['variance'], vals['sides'])
        except Exception as e:
            print "failed to load environment from yaml: ", e
                        
        f.close()
    class rectangle:
        shape = 'rectangle'
        is_border = False
        origin = [0,0] #bottom left
        size = [1,1] # width,height

        color = 'b'
        def draw_obj(_):
            if _.is_border:

                return plt.Rectangle(_.origin, _.size[0],_.size[1],fill=None, lw=5, edgecolor='g')
            return plt.Rectangle(_.origin, _.size[0],_.size[1], fc=_.color)
        
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
            return (x>=_.origin and x<=_.origin+_.size[0] and y>=_.origin and y<=_.origin+_.size[1])

    class circle:
        shape = 'circle'
        origin = (0,0) 
        radius = 1
        color = 'b'
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

        def draw_obj(_):
            return plt.Polygon(_.get_sides_lines(), fc='b')
            
        def __init__(_, radius, variance, sides, width, height):
            _.side_list = []
            _.radius = radius # approximate size
            _.variance = variance
            _.sides=sides
            _.x = _.unif()*width
            _.y = _.unif()*height

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
            tang_ang = np.arctan2(run,rise)*180/np.pi

            if run > 0 and rise > 0:
                tang_ang+=90
            if run >0 and rise <0:
                    tang_ang+=90
            if run <0 and rise > 0:
                tang_ang = (tang_ang+90+360)%360
            if run<0 and rise<0:
                tang_ang += 360+90

            tang_ang*=-1
            tang_ang+=90
            mean_side_length = 2*radius*np.sin(np.pi/sides)
            side_mag = _.gaus(variance*mean_side_length, mean_side_length)
            new_ang=_.gaus(variance*90, tang_ang-(180/sides))
            dx = side_mag*np.cos(new_ang/180.0*np.pi)
            dy = side_mag*np.sin(new_ang/180.0*np.pi)

            x1 = p1[0]+dx
            y1 = p1[1]+dy
            return x1,y1

        def get_sides_lines(_):
            return [x[0] for x in _.get_sides()]

        def get_sides(_):
            return _.side_list
