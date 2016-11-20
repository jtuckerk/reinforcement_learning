import sys
class brain_keyboard:
  #needs to be connected to matplotlib graph for input
  def __init__(_, agent):
    _.brain_outputs = []
    _.agent = agent
    pass

  def press(_,event):
    # key = o[0]
    # if key=='up':
    #   _.head_heading(.2)
    # if key=='down':
    #   _.head_heading(-.2)
    # if key=='left':
    #   _.change_heading(10.0)
    # if key=='right':
    #   _.change_heading(-10.0)


    _.brain_outputs = [event.key]

    _.agent.step()


  def connect_key_graph(_, fig):
    fig.canvas.mpl_connect('key_press_event', _.press)
    

  def connect_env(_,env):
    _.connect_key_graph(env.fig)

  def read_input(_,env_input):
    formatted = []
    for a in env_input:
      b = (a[0], round(a[1],2))
      formatted.append(b)


    sys.stdout.flush()



  def output(_):
    o = _.brain_outputs
    _.brain_outputs = 0

    return o

class brain_nn:
  def read_input(_,env_input):
    formatted = []
    for a in env_input:
      b = (a[0], round(a[1],2))
      formatted.append(b)


    sys.stdout.flush()



  def output(_):
    o = _.brain_outputs
    _.brain_outputs = 0

    return o

  def decide(_, observations):
    action = {}
    action['head_heading'] = 5
    action['change_heading'] = 0

    return action
