import sys
class brain_keyboard:
    #needs to be connected to matplotlib graph for input
    def __init__(_, agent):
        _.brain_outputs = []
        _.agent = agent
        pass

    def press(_,event):


        _.brain_outputs = [event.key]

        _.agent.step()


    def connect_key_graph(_, fig):
        fig.canvas.mpl_connect('key_press_event', _.press)
        

    def connect_env(_,env):
        _.connect_key_graph(env.fig)

    def read_input(_,env_input):
        formatted = []
        for a in env_input['ray_intersection']:
            b = (a[0], round(a[1],2))
            formatted.append(b)
        print formatted
        print env_input
        sys.stdout.flush()



    def output(_):
        o = _.brain_outputs
        _.brain_outputs = 0

        return o
