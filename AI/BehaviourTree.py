from typing import Callable


class BehaviourNode:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def activate(self, *args):
        raise NotImplementedError('Called an abstract method!')
        
    
class ControlFlowNode(BehaviourNode):
    def __init__(self, name: str, parent: BehaviourNode, condition: Callable, children: list[BehaviourNode]):
        super().__init__(name, parent)
        self.condition = condition
        self.children = children
    
    def activate(self, *args):
        return self.condition(*args)

class ExecutionNode(BehaviourNode):
    def __init__(self, name: str, parent: BehaviourNode, executionBehaviour: Callable):
        super().__init__(name, parent)
        self.executionBehaviour = executionBehaviour

    def activate(self, *args):
        return self.executionBehaviour(*args)

class RootNode(BehaviourNode):
    def __init__(self, child: ControlFlowNode):
        super().__init__('Root', parent=None)
        self.child = child
    
    def activate(self):
        return self.child.activate()
    
    
class BahaviourTree:
    def __init__(self, mob):
        self.rootNode = RootNode(None)
        self.mob = mob

    def find_action(self) -> Callable:
        return lambda: print('Finding actions not implemented yet!')

     
if __name__ == '__main__':
    b = BahaviourTree()
    print(b.find_action())