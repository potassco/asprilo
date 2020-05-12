# Placeholder, should not be called in actual use
def dummy(*args):
    return

def init(obj, x, y):
    obj.setPos(x,y)

def move(obj, x, y):
    obj.moveBy(x,y)
    print(f"Moved {obj.get_obj_id()} by {x},{y}")
    for hobj in obj.get_held_items():
        move(hobj, x, y)

def _moverev(obj, x, y):
    obj.moveBy(-x, -y)
    for hobj in obj.get_held_items():
        _moverev(hobj, x, y)

def pick_up(obj1, obj_id):
    obj1.pick_up(obj1.scene().get_model().get_items()[obj_id])

def pick_up_all(obj, pickuplist):
    for item in obj.scene().items(obj.scenePos()):
        if item.get_name() in pickuplist:
            obj.pick_up(item)

def put_down(obj, obj_id):
    for item in obj.get_held_items():
        if item.get_obj_id() == obj_id:
            obj.put_down(item)

def put_down_all(obj, pickuplist):
    for item in obj.get_held_items():
        obj.put_down(item)

#TODO: Interface with abstracts
def satisfy(abstract, product, amount):
    return

def demand(abstract, product, amount):
    return

dummy.rev = dummy
init.rev = dummy
move.rev = _moverev
pick_up.rev = put_down
pick_up_all.rev = put_down_all
put_down.rev = pick_up
put_down_all.rev = pick_up_all
satisfy.rev = demand
demand.rev = satisfy