# This is the templete class for visualizer items.
# There should never be an instance of this class.
# A visualizer item is a part of the visualizer model
# that is not drawn in any ways on the model view
# but can be represented in the gui.
# To add a new kind of visualizer item create a child class
# of VisualizerItem in this file and add it in the model.create_item
# function to the model. This is the only function in the model
# that should be changed. The behaivor and values of the object
# should be defindes inside of its own class.
class VisualizerItem(object):
    def __init__(self, ID = 0):
        self._kind_name = ''
        self._id = ID
        self._model = None

    # Sets the model of this item.
    # [Parameter model] should be an instance of the model.Model class.
    def set_model(self, model):
        if self._model == model:
            return
        self._model = model

    # This function is called by the model every time a step forward
    # was made. It defines the item specific behavior for time steps.
    # [Parameter time_step] is the current time step.
    def on_step_update(self, time_step):
        pass

    # This function is called by the model every time a step backwards
    # was made. It defines the item specific behavior for time steps.
    # [Parameter time_step] is the current time step.
    def on_step_undo(self, time_step):
        pass

    # This function handels the input phrases for every item.
    # This is called for every phrase the model receives with the
    # following syntax: 
    # init(object([object type], [object ID]), value([value name], [value])).
    # While [object type] is the same as self._kind_name and [object ID]
    # is the ID of the object and is the same as self._id.
    # The model decides based on this value the object the receives
    # the phrase.
    # [Parameter name] is the name of the value.
    # [value name] part of the phrase. It is represented by an instance 
    # of a clingo.Symbol object.
    # [Parameter value] is the actual value. It contains the [value]
    # part of the phrase. It is represented by an instance of a
    # clingo.Symbol object.
    # Returns 1 if the phrase cannot be parsed, -1 if one parameter is
    # invalid and 0 if the function succeeded.
    def parse_init_value(self, name, value):
        if value is None or name is None:
            return -1
        return 1

    # Resets the item to its original values.
    def restart(self):
        return

    # Converts the item to a string that represents the object.
    # This function is used to send the whole model to a solver
    # and to save a instance to a file.
    def to_init_str(self):
        return ''

    # Returns the id of the item.
    def get_id(self):
        return self._id

    # Returns the name of the item.
    def get_kind_name(self):
        return self._kind_name

#This class represents a single request or order line.
class Request(object):
    def __init__(self, product_id = 0, requested = 1):
        super(self.__class__, self).__init__()
        self.product_id = product_id
        self.requested = requested   
        self.delivered = 0
        self.changed = False

# This class represents an order. It consist out of one
# or more requests.
class Order(VisualizerItem):
    def __init__(self, ID = 0):
        super(self.__class__, self).__init__(ID)
        self._kind_name = 'order'
        self._station_id = None
        self._requests = []
        self._delivered = []
        self._time_step = 0
        self._is_fulfilled_at = None

    # Sets the packing station for an order.
    def set_station_id(self, station_id):
        self._station_id = station_id

    # Sets the time step in which an order occurs.
    def set_time_step(self, time_step):
        self._time_step = time_step

    # Sets the amount of requested products.
    # This function only overrides requests and does not
    # add new requests to the order. To add new requests
    # use the add_request function.
    # [Parameter product_id] is the id of a product.
    # [Parameter requested_amount] is the requested amount.
    def set_requested_amount(self, product_id, requested_amount):
        for temp_request in self._requests: 
            if str(temp_request.product_id) == str(product_id):
                temp_request.requested = requested_amount
                return

    # This function parses input phrases for orders. 
    # See VisualizerItem.parse_init_value for detailed informations.
    # Returns 1 if the phrase cannot be parsed, -1 if one parameter is
    # invalid and 0 if the function succeeded.
    def parse_init_value(self, name, value):
        result = super(self.__class__, self).parse_init_value(name, value)
        if result <= 0: 
            return result
        if name == 'line' and value.arguments is None:
            self.add_request(value, 0)
            return 0
        elif name == 'line' and len(value.arguments) == 2:
            self.add_request(value.arguments[0], value.arguments[1].number)
            return 0
        elif name == 'pickingStation':
            self._station_id = value
            return 0
        return 1

    # Removes a request from an order.
    # !This function will remove the order from the model if it deletes
    # the last request of this order.
    # [Parameter product_id] is the id of a product that should be removed.
    # If the order does not contain this item the function does nothing.
    def remove_request(self, product_id):
        for temp_request in self._requests: 
            if str(temp_request.product_id) == str(product_id):
                self._requests.remove(temp_request)
                if len(self._requests) == 0 and self._model is not None:
                    self._model.remove_item(self)
                return

    # Adds a request to an order.
    # If the item already is requested by this order the requested
    # amount will be added to the existing request.
    # [Parameter product_id] is the id of a product that should
    # be added.
    # [Parameter requested_amount] is the requested amount.
    def add_request(self, product_id, requested_amount):
        request = None
        for temp_request in self._requests: 
            if str(temp_request.product_id) == str(product_id):
                request = temp_request
        #only creates a new request if the product is not already requested
        if request is None:
            if requested_amount <= 0:
                requested_amount = 1
            self._requests.append(Request(product_id, requested_amount))
        else:
            request.requested = requested_amount

    # This function will be called if a robot delivers a product to
    # this order. This function is also be used to undo a deliver by
    # using a negative delivered amount.
    # [Parameter product_id] is the id of the deliverd product.
    # [Parameter delivered_amount] is the delivered amount. If this
    # value is 0 all requested products of a request will be delivered.
    # [Parameter product_id] is the current time step.
    def deliver(self, product_id, delivered_amount, time_step):
        undo = False
        if (time_step, product_id, -delivered_amount) in self._delivered:
            self._delivered.remove((time_step, product_id, -delivered_amount))
            undo = True
        else:
            self._delivered.append((time_step, product_id, delivered_amount))
        for request in self._requests:
            if str(request.product_id) == str(product_id):
                request.delivered += delivered_amount
                request.changed = True
                if delivered_amount == 0 and not undo:
                    request.delivered = request.requested
                elif delivered_amount == 0 and undo:
                    request.delivered = 0
        if self._is_fulfilled_at is None and self.is_fulfilled(time_step):
            self._is_fulfilled_at = time_step

    # Checks whether the order is fulfilled at the given time step.
    # This only works correctly if the given or the fulfill time step
    # was already reached.
    def is_fulfilled(self, time_step = None):
        if time_step is not None and self._is_fulfilled_at is not None:
            return self._is_fulfilled_at > time_step
        for request in self._requests:
            if request.delivered < request.requested:
                return False
        return True

    # Resets the delivers amount for every request to 0.
    def restart(self):
        for request in self._requests:
            request.delivered = 0
        self._delivered = []

    # Resets the changed flag at every time step.
    def on_step_update(self, time_step):
        for request in self._requests:
            request.changed = False

    # Resets the changed flag at every time step.    
    def on_step_undo(self, time_step):
        for request in self._requests:
            request.changed = False

    # Converts the order to a string that represents the order.
    # This function is used to send the orders to a solver
    # and to save orders to a file.
    def to_init_str(self):
        if len(self._requests) == 0:
            return ''

        s = ('init(object(order,'
            + str(self._id) + '),value(pickingStation,'
            + str(self._station_id) + ')).')
        for request in self._requests:
            s += ('init(object(order,'
                + str(self._id) + '),value(line,('
                + str(request.product_id) + ','
                + str(request.requested) + '))).')
        return s

    # This function creates and returns a list of strings
    # that represents all already delivered products.
    def to_delivered_str(self):
        strings = []
        for deliver in self._delivered:
            strings.append('delivered '
                                + str(deliver[2]) + ' units of product '
                                + str(deliver[1]) + ' for order '
                                + str(self._id) + ' at timestep '
                                + str(deliver[0]))
        if self.is_fulfilled():
            strings.append('order ' + str(self._id) + ' is fullfilled')
        return strings

    # Returns the id of the packing station of an order.
    def get_station_id(self):
        return self._station_id

    # Returns None if the order was not fulfilled yet.
    # Else returns the time step at which the order was fulfilled.
    def get_fulfilled_at(self):
        return self._is_fulfilled_at

    #Returns the count of requests.
    def get_num_requests(self):
        return len(self._requests)

    #Iterates through every request.
    def iterate_requests(self):
        for request in self._requests:
            yield request

# This class represents a Task. It consists out of one
# or more checkpoints.
class Task(VisualizerItem):
    def __init__(self, ID = 0):
        super(self.__class__, self).__init__(ID)
        self._kind_name = 'task'
        self._station_id = None
        self._task_group = None
        self._task_type = None
        self._robot = None
        self._changed = False
        self._checkpoints = []
        self._open = []
        self._history = []

    # Sets the group of a task.
    def set_task_group(self, task_group):
        self._task_group = task_group

    # Sets the type of a task.
    def set_task_type(self, task_type):
        self._task_type = task_type

    # Assigns a robot to a task.
    def set_robot(self, robot):
        if self._robot == robot:
            return
        self._robot = robot
        self._robot.add_task(self)

    # Adds a new checkpoint to the task.
    def add_checkpoint(self, checkpoint_id, name, checkpoint_number):
        self._checkpoints.append(
            (self._model.get_item('checkpoint', 
            checkpoint_id, True, True), name))

        index = 0
        for item in self._open:
            if item[1] == checkpoint_number:
                self._open[index] = (name, checkpoint_number)
                return
            elif item[1] < checkpoint_number:
                index += 1
            else:
                break
        self._open.insert(index, (name, checkpoint_number))

    # The function is be called if the assigned robot 
    # reached a checkpoint.
    def visit_checkpoint(self, checkpoint):
        for checkpoint2 in self._checkpoints:
            if checkpoint2[0] == checkpoint:
                self._changed = True
                if len(self._open) > 0:
                    if checkpoint2[1] == self._open[0][0]:
                        self._open.pop(0)
                        self._history.append(checkpoint2[1] + '(*)')
                        checkpoint.visit()
                    else:
                        self._history.append(checkpoint2[1])
                    return
                else:
                    self._history.append(checkpoint2[1])
                    return

    # This function will be called if a time step was be undone 
    # in which a checkpoint was reached.
    def unvisit_checkpoint(self, checkpoint):
        for checkpoint2 in reversed(self._checkpoints):
            if checkpoint2[0] == checkpoint and len(self._history) > 0:
                if self._history[len(self._history)-1] == checkpoint2[1]:
                    self._history.pop()
                    self._changed = True
                    return

                elif self._history[len(self._history)-1] == (checkpoint2[1] + '(*)'):
                    self._history.pop()
                    self._open.insert(0, checkpoint2[1])
                    checkpoint.visit()
                    self._changed = True
                    return

    # This function parses input phrases for tasks. 
    # See VisualizerItem.parse_init_value for detailed informations.
    # Returns 1 if the phrase cannot be parsed, -1 if one parameter is
    # invalid and 0 if the function succeeded.
    def parse_init_value(self, name, value):
        result = super(self.__class__, self).parse_init_value(name, value)
        if result <= 0: 
            return result
        if name == 'group':
            self.set_task_group(str(value))
            return 0
        elif name == 'type':
            self.set_task_type(str(value))
            return 0
        elif name == 'robot':
            if self._model is None:
                return 0
            robot = self._model.get_item('robot', value, True, True)
            self.set_robot(robot)
            return 0
        elif name == 'checkpoint' and len(value.arguments) == 3:
            try:
                self.add_checkpoint(str(value.arguments[0]), str(value.arguments[1]), value.arguments[2].number)
                return 0
            except Exception as err:
                print(err)
        return 1

    # Resets the changed flag at every time step.
    def on_step_update(self, time_step):
        self._changed = False

    # Resets the changed flag at every time step.
    def on_step_undo(self, time_step):
        self._changed = False

    # Returns the task group.
    def get_task_group(self):
        return self._task_group

    # Returns the task type.
    def get_task_type(self):
        return self._task_type

    # Returns the assigned robot.
    def get_robot(self):
        return self._robot

    # Returns the id of the assigned robot.
    def get_robot_id(self):
        if self._robot is None:
            return None
        return self._robot.get_id()

    # Returns whether this task has been changed in this time step.
    # Returns true if a checkpoint ws reached.
    def get_changed(self):
        return self._changed

    # Returns the list of checkpoints.
    def get_checkpoints(self):
        return self._checkpoints

    # Returns the history of reached checkpoints.
    def get_checkpoint_history(self):
        return self._history

    # Returns a list of unreached checkpoints.
    def get_open_checkpoints(self):
        ll = []
        for ele in self._open:
            ll.append(ele[0])
        return ll
