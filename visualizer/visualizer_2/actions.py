def teleport(obj, x, y):
    obj.setPos(x,y)

def move(obj, x, y):
    obj.moveBy(x,y)

def pick_up(obj1, obj2):
    obj2.setParent(obj1)

def put_down(obj1, obj2):
    obj2.setParent(obj1.parentItem())

#TODO: Interface with abstracts
def satisfy(abstract, product, amount):
    return

def demand(abstract, product, amount):
    return
