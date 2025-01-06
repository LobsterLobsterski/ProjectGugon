import sys
from typing import Callable, Dict, List


class BehaviourNode:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def activate(self, *args):
        raise NotImplementedError('Called an abstract method!')
    
    def __repr__(self):
        return f'{type(self).__name__}(name: {self.name}, parent: {self.parent})'
        
    
class ConditionNode(BehaviourNode):
    def __init__(self, name: str, parent: BehaviourNode, condition: Callable, children: list[BehaviourNode]):
        super().__init__(name, parent)
        self.condition = condition
        self.children = children

    
    def activate(self, *args):
        return self.condition(*args)
    
    def get_child_by_index(self, idx: int):
        return self.children[idx]
    
    def print_children(self):
        print(f'Children of {self}')
        for child in self.children:
            print(f'\t{child}')


class ExecutionNode(BehaviourNode):
    def __init__(self, name: str, parent: BehaviourNode, executionBehaviour: Callable):
        super().__init__(name, parent)
        self.executionBehaviour = executionBehaviour

    def activate(self, *args):
        return self.executionBehaviour(*args)
   

class BehaviourTree:
    def __init__(self, mob, tree: Dict[Callable, List[Callable, ]]):
        self.mob = mob
        self.root = self.construct_tree(tree)

    def find_action(self, current_node=None) -> Callable:
        '''
        We search the tree and return the method (action)
        which will be ran by the mob.
        '''
        if current_node == None:
            current_node = self.root

        if isinstance(current_node, ConditionNode):
            condition_result = current_node.activate()
            #idx=int(condition_result)
            if condition_result:
                return self.find_action(current_node.get_child_by_index(1))
            return self.find_action(current_node.get_child_by_index(0))
        
        return current_node.executionBehaviour
    
    def construct_tree(self, tree):
        def get_children_nodes(children: List[Callable, ], recursionLevel=0) -> List[BehaviourNode]:
            nodes = []

            for method in children:
                if method in tree:
                    ### condition method child
                    children_nodes = get_children_nodes(tree[method], recursionLevel+1)
                    node = ConditionNode(method.__name__, None, method, children_nodes)
                    for c in children_nodes:
                        c.parent = node

                    nodes.append(node)

                else:
                    ### action method child
                    nodes.append(ExecutionNode(method.__name__, None, method))

            return nodes

        root_condition_method, root_children_methods = next(iter(tree.items()))
        children_nodes = get_children_nodes(root_children_methods)

        root = ConditionNode(root_condition_method.__name__, None, root_condition_method, children_nodes)
        for c in children_nodes:
            c.parent = root

        return root

    def print_tree(self, node=None, recursion_level=0):
        if not node:
            node = self.root
            print(f'Root: {node}')
        
        for idx, child in enumerate(node.children):
            print('\t'*(recursion_level+1), '\x1B[3mon False:\x1B[23m' if idx%2==0 else '\x1B[3mon True:\x1B[23m',child)
            if isinstance(child, ConditionNode):
                self.print_tree(child, recursion_level+1)

                