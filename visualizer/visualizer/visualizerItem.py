class VisualizerItem(object):
    def __init__(self, ID = 0):
        self._kind_name = ''
        self._id = ID
        self._model = None

    def set_model(self, model):
        if self._model == model:
            return
        self._model = model

    def on_step_update(self, time_step):
        pass

    def on_step_undo(self, time_step):
        pass

    def parse_init_value(self, name, value):
        return 1

    def restart(self):
        return

    def to_init_str(self):
        return ''

    def get_id(self):
        return self._id

    def get_kind_name(self):
        return self._kind_name

class Request(object):
    def __init__(self, product_id = 0, requested = 1):
        super(self.__class__, self).__init__()
        self.product_id = product_id
        self.requested = requested   
        self.delivered = 0
        self.changed = False

class Order(VisualizerItem):
    def __init__(self, ID = 0):
        super(self.__class__, self).__init__(ID)
        self._kind_name = 'order'
        self._station_id = None
        self._requests = []
        self._delivered = []
        self._time_step = 0
        self._is_fulfilled_at = None

    def set_station_id(self, station_id):
        self._station_id = station_id

    def set_time_step(self, time_step):
        self._time_step = time_step

    def set_requested_amount(self, product_id, requested_amount):
        for temp_request in self._requests: 
            if str(temp_request.product_id) == str(product_id):
                temp_request.requested = requested_amount
                return

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

    def remove_request(self, product_id):
        for temp_request in self._requests: 
            if str(temp_request.product_id) == str(product_id):
                self._requests.remove(temp_request)
                if len(self._requests) == 0 and self._model is not None:
                    self._model.remove_item(self)
                return

    def add_request(self, product_id, requested_amount):
        request = None
        for temp_request in self._requests: 
            if str(temp_request.product_id) == str(product_id):
                request = temp_request
        if request is None:
            if requested_amount <= 0:
                requested_amount = 1
            self._requests.append(Request(product_id, requested_amount))
        else:
            request.requested = requested_amount

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

    def is_fulfilled(self, time_step = None):
        if time_step is not None and self._is_fulfilled_at is not None:
            return self._is_fulfilled_at > time_step
        for request in self._requests:
            if request.delivered < request.requested:
                return False
        return True

    def restart(self):
        for request in self._requests:
            request.delivered = 0
        self._delivered = []

    def on_step_update(self, time_step):
        for request in self._requests:
            request.changed = False

    def on_step_undo(self, time_step):
        for request in self._requests:
            request.changed = False

    def to_init_str(self):
        if len(self._requests) == 0:
            return ''

        s = ('init(object(order,'
            + str(self._id) + '),value(pickingStation,'
            + str(self._station_id) + ')).')
        for request in self._requests:
            s += ('\ninit(object(order,'
                + str(self._id) + '),value(line,('
                + str(request.product_id) + ','
                + str(request.requested) + '))).')
        return s

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

    def get_station_id(self):
        return self._station_id

    def get_fulfilled_at(self):
        return self._is_fulfilled_at

    def get_num_requests(self):
        return len(self._requests)

    def iterate_requests(self):
        for request in self._requests:
            yield request

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

    def set_task_group(self, task_group):
        self._task_group = task_group

    def set_task_type(self, task_type):
        self._task_type = task_type

    def set_robot(self, robot):
        if self._robot == robot:
            return
        self._robot = robot
        self._robot.add_task(self)

    def add_checkpoint(self, checkpoint_id, name, checkpoint_number):
        self._checkpoints.append((self._model.get_item('checkpoint', checkpoint_id, True, True), name))
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
                print err
        return 1

    def on_step_update(self, time_step):
        self._changed = False

    def on_step_undo(self, time_step):
        self._changed = False

    def get_task_group(self):
        return self._task_group

    def get_task_type(self):
        return self._task_type

    def get_robot(self):
        return self._robot

    def get_robot_id(self):
        if self._robot is None:
            return None
        return self._robot.get_id()

    def get_changed(self):
        return self._changed

    def get_checkpoints(self):
        return self._checkpoints

    def get_checkpoint_history(self):
        return self._history

    def get_open_checkpoints(self):
        ll = []
        for ele in self._open:
            ll.append(ele[0])
        return ll
