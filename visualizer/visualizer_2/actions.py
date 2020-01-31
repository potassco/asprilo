# Placeholder, should not be called in actual use
def dummy(*args):
    return

def init(obj, x, y):
    obj.setPos(x,y)

def move(obj, x, y):
    obj.moveBy(x,y)

def _moverev(obj, x, y):
    obj.moveBy(-x, -y)

def pick_up(obj1, obj2):
    obj2.setParent(obj1)

def put_down(obj1, obj2):
    obj2.setParent(obj1.parentItem())

#TODO: Interface with abstracts
def satisfy(abstract, product, amount):
    return

def demand(abstract, product, amount):
    return

dummy.rev = dummy
init.rev = dummy
move.rev = _moverev
pick_up.rev = put_down
put_down.rev = pick_up
satisfy.rev = demand
demand.rev = satisfy