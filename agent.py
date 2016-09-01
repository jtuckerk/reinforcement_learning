import sensors
class agent:
    x_pos = 1
    y_pos = 1

    heading = 0 # % of 360
    sensor = None

    sensor_forward = False
    def __init__(_,x=1,y=1,ray_count=3,ray_width=.1, ray_dist=.5, sensor_forward=False):
        _.sensor = sensors.sensors.bounded_sensor(ray_count,ray_width,ray_dist,x,y)
        
        _.sensor_forward = sensor_forward
        
    def move(dx, dy):
        _.x_pos+=dx
        _.y_pos+=dy

        _.sensor.set_pos(_.x_pos, _.y_pos)

        if (_.sensor_forward):
            #point sensor in direction of motion
            pass

    #point to specific angle
    def point_sensor(_, abs_angle):
        pass

    def turn_sensor(_, d_theta):
        pass

    def draw_objs(_):
        #return agent object and sensor draw object
        return [_.sensor.draw_obj()]

        
