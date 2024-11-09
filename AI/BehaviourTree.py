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
        
    
class ControlFlowNode(BehaviourNode):
    def __init__(self, name: str, parent: BehaviourNode, condition: Callable, children: list[BehaviourNode]):
        super().__init__(name, parent)
        self.condition = condition
        self.children = children
    
    def activate(self, *args):
        return self.condition(*args)
    
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
        self.root = self.constructTree(tree)
        self.print_tree()
        sys.exit()

    def find_action(self) -> Callable:
        '''
        We search the tree and return the method (action)
        which will be ran by the mob
        '''
        return lambda: print('Finding actions not implemented yet!')

    def constructTree(self, tree):
        # print('\nCONSTRUCTING BEHAVIOUR TREE!!!')
        def get_children_nodes(children: List[Callable, ], recursionLevel=0) -> List[BehaviourNode]:
            # print('\n', '\t'*recursionLevel, 'get_children_nodes level:', recursionLevel)
            nodes = []

            for method in children:
                # print('\t'*(recursionLevel+1), 'child method:', method.__name__)
                if method in tree:
                    # print('\t'*(recursionLevel+2), 'conditon method')
                    ### condition method child
                    children_nodes = get_children_nodes(tree[method], recursionLevel+1)
                    node = ControlFlowNode(method.__name__, None, method, children_nodes)
                    for c in children_nodes:
                        c.parent = node

                    nodes.append(node)

                else:
                    # print('\t'*(recursionLevel+2), 'exec method')
                    ### action method child
                    nodes.append(ExecutionNode(method.__name__, None, method))

            return nodes

        root_condition_method, root_children_methods = next(iter(tree.items()))

        # print('root_condition_method:', root_condition_method.__name__)
        # print('\t', [m.__name__ for m in root_children_methods])
        children_nodes = get_children_nodes(root_children_methods)
        # print('root_children_methods:', children_nodes)
        
        root = ControlFlowNode(root_condition_method.__name__, None, root_condition_method, children_nodes)
        for c in children_nodes:
            c.parent = root

        # print('root', root)
        # root.print_children()
        return root

    def print_tree(self, node=None, recursion_level=0):
        if not node:
            node = self.root
            print(f'Root: {node}')
        
        for idx, child in enumerate(node.children):
            print('\t'*(recursion_level+1), '\x1B[3mon False:\x1B[23m' if idx%2==0 else '\x1B[3mon True:\x1B[23m',child)
            if isinstance(child, ControlFlowNode):
                self.print_tree(child, recursion_level+1)