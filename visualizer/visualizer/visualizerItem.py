"""
To add a new kind of visualizer item create a child class
of VisualizerItem in this file and add it in the model.create_item
function to the model. This is the only function in the model
that should be changed. The behaivor and values of the object
should be defined inside of its own class.

To add new properties to a class modify the attributes of a class
and modify the 'parse_init_value', the 'to_init_str', the 'restart', the 'on_step_update' and
the 'on_step_undo' methods to adjust the objects behaivor.

Look at the method definitions of other classes for examples.
"""

class VisualizerItem(object):
    """
    This is the templete class for visualizer item.
    There should never be an instance of this class.
    A visualizer item is a part of the visualizer model
    that is not drawn in any ways on the model view
    but can be represented in the gui.

    Attributes:
    _kind_name: str
        The name of this kind of object.
    _ID: int
        The id of this object.
    _model:
        The model this object belongs to
    """

    def __init__(self, ID = 0):
        """
        Parameters:
        ID : int, optional
            The ID of the object
        """
        self._kind_name = ''
        self._id = ID
        self._model = None

    def set_model(self, model):
        """
        Sets the model of this object.
        Parameters:
        model: model.Model
            The model this object belongs to.
        """

        if self._model == model:
            return
        self._model = model

    def on_step_update(self, time_step):
        """    
        This function is called by the model every time a step forward
        was made. It defines the object specific behavior for time steps.
        Parameters:
        time_step: int
            This represents the current time step.
        """

        pass

    def on_step_undo(self, time_step):
        """
        This function is called by the model every time a step backwards
        was made. It defines the object specific behavior for time steps.
        Parameters:
        time_step: int
            This represents the time step that will be undone.
        """

        pass

    def parse_init_value(self, name, value):
        """
        This function handels the input phrases for every object.
        This is called for every phrase the model receives with the
        following syntax: 
        init(object([object type], [object ID]), value([value name], [value])).
        While [object type] is the same as self._kind_name and [object ID]
        is the ID of the object and is the same as self._id.
        The model decides based on this value the object that receives
        the phrase.

        Returns 1 if the phrase cannot be parsed, -1 if one parameter is
        invalid and 0 if the function succeeded.

        Parameters:
        name: str
            This is the name of the value.
        value: clingo.symbol.Symbol
            This is the actual value. It contains the [value]
            part of the phrase.
        """

        if value is None or name is None:
            return -1
        return 1

    def restart(self):
        """
        Resets the object to its original values.
        """

        return

    def to_init_str(self):
        """
        Converts the object to a string that represents its values.
        This function is used to send the whole model to a solver
        and to save a instance to a file.
        """

        return ''

    def get_id(self):
        """
        Returns the id of the object.
        """

        return self._id

    def get_kind_name(self):
        """
        Returns the name of the object.
        """
        return self._kind_name

class Request(object):
    """
    This class represents a single request or order line.

    Attributes:
    product_id : int
        The ID of the requested product
    requested : int
        The amount of requested products
    delivered : int
        The amount of already delivered products
    changed : bool
        Saves whether this request was edited 
        at the last time step.
    """

    def __init__(self, product_id = 0, requested = 1):
        """
        Parameters:
        product_id : int, optional
            The ID of the requested product
        requested : int, optional
            The amount of requested products
        """

        super(self.__class__, self).__init__()
        self.product_id = product_id
        self.requested = requested   
        self.delivered = 0
        self.changed = False


class Order(VisualizerItem):
    """
    This class represents an order. It consist out of one
    or more requests.

    Attributes:
    _kind_name: str
        The name of this kind of object. This is always 'order'.
    _station_id: int
        The destination packing station for an order
    _requests: list
        A list of one or more requests
    _delivered: list
        A list of triples that contains a time step,
        a product id and a delivered amount.
    _time_step: int
        At this time step this order occurred.
    _is_fullfilled_at:
        At this time step this order is fulfilled.
        This will be 'None' until this time step will
        be reached for the first time.
    """

    def __init__(self, ID = 0):
        """
        Parameters:
        product_id : int, optional
            The ID of the order
        """

        super(self.__class__, self).__init__(ID)
        self._kind_name = 'order'
        self._station_id = None
        self._requests = []
        self._delivered = []
        self._time_step = 0
        self._is_fulfilled_at = None

    def set_station_id(self, station_id):
        """
        Sets the packing station for an order.
        """

        self._station_id = station_id

    def set_time_step(self, time_step):
        """
        Sets the time step in which an order occurs.
        """

        self._time_step = time_step

    def set_requested_amount(self, product_id, requested_amount):
        """
        Sets the amount of requested products.
        This function only overrides requests and does not
        add new requests to the order. To add new requests
        use the add_request function.

        Parameters:
        product_id: int
            The id of a product
        requested_amount: int
            The requested amount
        """

        for temp_request in self._requests: 
            if str(temp_request.product_id) == str(product_id):
                temp_request.requested = requested_amount
                return


    def parse_init_value(self, name, value):
        """
        This function parses input phrases for orders. 
        See VisualizerItem.parse_init_value for detailed informations.

        Returns 1 if the phrase cannot be parsed, -1 if one parameter is
        invalid and 0 if the function succeeded.

        Parameters:
        name: str
            This is the name of the value.
        value: clingo.symbol.Symbol
            This is the actual value. It contains the [value]
            part of the phrase.
        """

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

    def remove_request(self, product_id):
        """
        Removes a request from an order.
        !This function will remove the order from the model if it deletes
        the last request of this order.

        Parameters:
            product_id: int
                The id of the product that will be removed.
        """

        for temp_request in self._requests: 
            if str(temp_request.product_id) == str(product_id):
                self._requests.remove(temp_request)
                if len(self._requests) == 0 and self._model is not None:
                    self._model.remove_item(self)
                return

    def add_request(self, product_id, requested_amount):
        """
        Adds a request to an order.
        If the item already is requested by this order the requested
        amount will be added to the existing request.

        Parameters:
        product_id: int
            The id of the product that will be added
        requested_amount: 
            The requested amount
        """

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

    def deliver(self, product_id, delivered_amount, time_step):
        """
        This function will be called if a robot delivers a product to
        this order. This function is also be used to undo a delivery by
        using a negative delivered amount.

        Parameters:
        product_id: 
            The id of the deliverd product.
        delivered_amount: The delivered amount. If this
        value is 0 all requested products of a request will be delivered.
        product_id: 
            The current time step.
        """

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


    def is_fulfilled(self, time_step = None):
        """
        Checks whether the order is fulfilled at the given time step.
        This only works correctly if the given or the fulfill time step
        was already reached.        
        """

        if time_step is not None and self._is_fulfilled_at is not None:
            return self._is_fulfilled_at > time_step
        for request in self._requests:
            if request.delivered < request.requested:
                return False
        return True

    def restart(self):
        """
        Resets the delivered amount for every request to 0.
        """

        for request in self._requests:
            request.delivered = 0
        self._delivered = []

    def on_step_update(self, time_step):
        """
        Resets the changed flag at every time step.
        """

        for request in self._requests:
            request.changed = False

    def on_step_undo(self, time_step):
        """
        Resets the changed flag at every time step.    
        """

        for request in self._requests:
            request.changed = False

    def to_init_str(self):
        """
        Converts the order to a string that represents the order.
        This function is used to send the orders to a solver
        and to save orders to a file.
        """

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


    def to_delivered_str(self):
        """
        This function creates and returns a list of strings
        that represents all already delivered products.
        """

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

    def get_station_id(self):
        """
        Returns the id of the packing station of an order.
        """

        return self._station_id

    def get_fulfilled_at(self):
        """
        Returns None if the order was not fulfilled yet.
        Else returns the time step at which the order was fulfilled.
        """

        return self._is_fulfilled_at

    def get_num_requests(self):
        """
        Returns the count of requests.
        """
        return len(self._requests)

    def iterate_requests(self):
        """
        Iterates through every request.
        """
        for request in self._requests:
            yield request


class Task(VisualizerItem):
    """
    This class represents a task. It consists out of one
    or more checkpoints. A task is completed when a robot
    has visited all checkpoints in a certain order.

    Attributes:
    _kind_name: str
        The name of this kind of object. This is always 'task'.
    _task_group: str
        The group of this task
    _task_type: str
        The type of this task
    _robot: visualizerGraphicItem.Robot
        The robot to fulfill the task
    _changed: bool
        Saves whether this request was edited 
        at the last time step.
    _checkpoints: visualizerGraphicItem.Checkpoint
        A list of checkpoints
    _open:
        A list of tuples that contains the name and
        the checkpoint.
    _history:
        A list of visited checkpoints
    """

    def __init__(self, ID = 0):
        """
        Parameters:
        product_id : int, optionale
            The ID of the order
        """
        super(self.__class__, self).__init__(ID)
        self._kind_name = 'task'
        self._task_group = None
        self._task_type = None
        self._robot = None
        self._changed = False
        self._checkpoints = []
        self._open = []
        self._history = []

    def set_task_group(self, task_group):
        """
        Sets the group of a task.
        """
        self._task_group = task_group

    def set_task_type(self, task_type):
        """
        Sets the type of a task.
        """
        self._task_type = task_type

    def set_robot(self, robot):
        """
        Assigns a robot to a task.
        Also adds this task to the robots tasks.
        """

        if self._robot == robot:
            return
        self._robot = robot
        self._robot.add_task(self)

    def add_checkpoint(self, checkpoint_id, name, checkpoint_number):
        """
        Adds a new checkpoint to the task.

        Parameters:
        checkpoint_id: int
            The id of the checkpoint
        name: str
            The name of the checkpoint
        checkpoint_number: int
            The chronological number of the checkpoint
        """

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

    def visit_checkpoint(self, checkpoint):
        """
        This function is be called if the assigned robot 
        reached a checkpoint.

        Parameters:
        checkpoint: visualizerGraphicItem.Checkpoint
            The checkpoint that was reached
        """

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

    def unvisit_checkpoint(self, checkpoint):
        """
        This function will be called if a time step was be undone 
        in which a checkpoint was reached.

        Parameters:
        checkpoint: visualizerGraphicItem.Checkpoint
            The checkpoint that was reached
        """

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

    def parse_init_value(self, name, value):
        """
        This function parses input phrases for tasks. 
        See VisualizerItem.parse_init_value for detailed informations.

        Returns 1 if the phrase cannot be parsed, -1 if one parameter is
        invalid and 0 if the function succeeded.

        Parameters:
        name: str
            This is the name of the value.
        value: clingo.symbol.Symbol
            This is the actual value. It contains the [value]
            part of the phrase.
        """

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

    def on_step_update(self, time_step):
        """
        Resets the changed flag at every time step.
        """

        self._changed = False

    def on_step_undo(self, time_step):
        """
        Resets the changed flag at every time step.
        """

        self._changed = False

    def get_task_group(self):
        """
        Returns the task group.
        """
        return self._task_group

    def get_task_type(self):
        """
        Returns the task type.
        """
        return self._task_type

    def get_robot(self):
        """
        Returns the assigned robot.
        """
        return self._robot

    def get_robot_id(self):
        """
        Returns the id of the assigned robot.
        """

        if self._robot is None:
            return None
        return self._robot.get_id()

    def get_changed(self):
        """
        Returns whether this task has been changed in this time step.
        Returns true if a checkpoint ws reached.
        """

        return self._changed

    def get_checkpoints(self):
        """
        Returns the list of checkpoints.
        """

        return self._checkpoints

    def get_checkpoint_history(self):
        """
        Returns the history of reached checkpoints.
        """

        return self._history

    def get_open_checkpoints(self):
        """
        Returns a list of unreached checkpoints.
        """

        ll = []
        for ele in self._open:
            ll.append(ele[0])
        return ll
