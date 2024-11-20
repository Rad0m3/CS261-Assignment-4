# Name:John Fletcher
# OSU Email: fletjohn@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: Assignment 4
# Due Date: 11/12/2024
# Description: Implementation of binary search tree class


import random
from queue_and_stack import Queue, Stack
from bst import BSTNode, BST


class AVLNode(BSTNode):
    """
    AVL Tree Node class. Inherits from BSTNode
    DO NOT CHANGE THIS CLASS IN ANY WAY
    """
    def __init__(self, value: object) -> None:
        """
        Initialize a new AVL node
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        # call __init__() from parent class
        super().__init__(value)

        # new variables needed for AVL
        self.parent = None
        self.height = 0

    def __str__(self) -> str:
        """
        Override string method
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return 'AVL Node: {}'.format(self.value)


class AVL(BST):
    """
    AVL Tree class. Inherits from BST
    """

    def __init__(self, start_tree=None) -> None:
        """
        Initialize a new AVL Tree
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        # call __init__() from parent class
        super().__init__(start_tree)

    def __str__(self) -> str:
        """
        Override string method
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        values = []
        super()._str_helper(self._root, values)
        return "AVL pre-order { " + ", ".join(values) + " }"

    def is_valid_avl(self) -> bool:
        """
        Perform pre-order traversal of the tree. Return False if there
        are any problems with attributes of any of the nodes in the tree.

        This is intended to be a troubleshooting 'helper' method to help
        find any inconsistencies in the tree after the add() or remove()
        operations. Review the code to understand what this method is
        checking and how it determines whether the AVL tree is correct.

        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        stack = Stack()
        stack.push(self._root)
        while not stack.is_empty():
            node = stack.pop()
            if node:
                # check for correct height (relative to children)
                left = node.left.height if node.left else -1
                right = node.right.height if node.right else -1
                if node.height != 1 + max(left, right):
                    return False

                if node.parent:
                    # parent and child pointers are in sync
                    if node.value < node.parent.value:
                        check_node = node.parent.left
                    else:
                        check_node = node.parent.right
                    if check_node != node:
                        return False
                else:
                    # NULL parent is only allowed on the root of the tree
                    if node != self._root:
                        return False
                stack.push(node.right)
                stack.push(node.left)
        return True

    # ------------------------------------------------------------------ #

    def add(self, value: object) -> None:
        """
        Add a new value to the AVL tree while maintaining balance.
        Duplicate values are not allowed. Iterative implementation using Stack.
        """
        if not self._root:
            # If the tree is empty, create the root node
            self._root = AVLNode(value)
            return

        current = self._root
        stack = Stack()  # Use Stack to track the path to the insertion point

        # Find the correct position for the new value
        while current:
            stack.push(current)
            if value < current.value:
                if not current.left:
                    # Insert as left child
                    current.left = AVLNode(value)
                    current.left.parent = current
                    stack.push(current.left)
                    break
                current = current.left
            elif value > current.value:
                if not current.right:
                    # Insert as right child
                    current.right = AVLNode(value)
                    current.right.parent = current
                    stack.push(current.right)
                    break
                current = current.right
            else:
                # Value already exists, do nothing
                return

        # Update height and rebalance the tree from the inserted node back to the root
        while not stack.is_empty():
            node = stack.pop()
            self._update_height(node)
            balanced_node = self._rebalance(node)

            if not stack.is_empty():
                # Update the parent pointers
                parent = stack.top()
                if parent.left == node:
                    parent.left = balanced_node
                elif parent.right == node:
                    parent.right = balanced_node
            else:
                # If no parent, this is the root
                self._root = balanced_node

    def remove(self, value: object) -> bool:
        """
        Removes the value from the AVL tree while maintaining its AVL properties.
        Returns True if the value is removed, False if not found.
        """
        node = self._find(value)  # Find the node to be removed

        if node is None:
            return False  # Value not found in tree

        # Case 1: Node with only one child or no child
        if node.left is None or node.right is None:
            # Directly replace the node with its non-null child, if it has one
            self._replace_node(node)

        # Case 2: Node with two children
        else:
            # Find the in-order successor (the leftmost node of the right subtree)
            successor = self._find_min(node.right)
            node.value = successor.value  # Replace node value with successor value
            self._replace_node(successor)  # Remove the successor node

        # Rebalance the tree starting from the parent of the removed node
        current = node.parent
        while current:
            self._update_height(current)  # Update the height of the current node
            self._rebalance(current)  # Rebalance the tree if necessary
            current = current.parent  # Move up to the parent node

        return True

    def _replace_node(self, node: AVLNode) -> None:
        """Replace the given node with its child (if any)."""
        # If the node has a child, replace it with the non-null child
        if node.left:
            self._replace_parent_child(node, node.left)
        else:
            self._replace_parent_child(node, node.right)

    def _replace_parent_child(self, node: AVLNode, child: AVLNode) -> None:
        """Replace node with its child (either left or right)."""
        if node.parent:
            if node.parent.left == node:
                node.parent.left = child
            else:
                node.parent.right = child
        else:
            self._root = child  # If node is root, update root pointer

        if child:
            child.parent = node.parent  # Update the parent pointer of the child

    # Experiment and see if you can use the optional                         #
    # subtree removal methods defined in the BST here in the AVL.            #
    # Call normally using self -> self._remove_no_subtrees(parent, node)     #
    # You need to override the _remove_two_subtrees() method in any case.    #
    # Remove these comments.                                                 #
    # Remove these method stubs if you decide not to use them.               #
    # Change this method in any way you'd like.                              #

    def _remove_two_subtrees(self, remove_parent: AVLNode, remove_node: AVLNode) -> AVLNode:
        """
        TODO: Write your implementation
        """
        pass

    # It's highly recommended to implement                          #
    # the following methods for balancing the AVL Tree.             #
    # Remove these comments.                                        #
    # Remove these method stubs if you decide not to use them.      #
    # Change these methods in any way you'd like.                   #

    def _balance_factor(self, node: AVLNode) -> int:
        """
        Calculate the balance factor of the given node.
        """
        left_height = node.left.height if node.left else -1
        right_height = node.right.height if node.right else -1
        return left_height - right_height

    def _get_height(self, node: AVLNode) -> int:
        """
        TODO: Write your implementation
        """
        pass

    def _rotate_left(self, node: AVLNode) -> AVLNode:
        new_root = node.right
        node.right = new_root.left
        if new_root.left:
            new_root.left.parent = node
        new_root.left = node

        new_root.parent = node.parent
        if node.parent:
            if node.parent.left == node:
                node.parent.left = new_root
            else:
                node.parent.right = new_root
        else:
            self._root = new_root

        node.parent = new_root
        self._update_height(node)
        self._update_height(new_root)
        return new_root

    def _rotate_right(self, node: AVLNode) -> AVLNode:
        """
        Perform a right rotation on the subtree rooted at the given node.
        """
        new_root = node.left
        node.left = new_root.right
        if new_root.right:
            new_root.right.parent = node
        new_root.right = node

        # Update parent pointers
        new_root.parent = node.parent
        node.parent = new_root

        # Update heights
        self._update_height(node)
        self._update_height(new_root)

        return new_root

    def _update_height(self, node: AVLNode) -> None:
        left_height = node.left.height if node.left else -1
        right_height = node.right.height if node.right else -1
        node.height = 1 + max(left_height, right_height)

    def _rebalance(self, node: AVLNode) -> AVLNode:
        balance = self._balance_factor(node)

        # Left-heavy case
        if balance > 1:
            if self._balance_factor(node.left) < 0:  # Left-Right case
                node.left = self._rotate_left(node.left)  # Rotate left on the left child
            return self._rotate_right(node)  # Rotate right on the node

        # Right-heavy case
        if balance < -1:
            if self._balance_factor(node.right) > 0:  # Right-Left case
                node.right = self._rotate_right(node.right)  # Rotate right on the right child
            return self._rotate_left(node)  # Rotate left on the node

        return node  # Balanced, no rotation needed


# ------------------- BASIC TESTING -----------------------------------------


if __name__ == '__main__':

    print("\nPDF - method add() example 1")
    print("----------------------------")
    test_cases = (
        (1, 2, 3),  # RR
        (3, 2, 1),  # LL
        (1, 3, 2),  # RL
        (3, 1, 2),  # LR
    )
    for case in test_cases:
        tree = AVL(case)
        print(tree)
        tree.print_tree()

    print("\nPDF - method add() example 2")
    print("----------------------------")
    test_cases = (
        (10, 20, 30, 40, 50),   # RR, RR
        (10, 20, 30, 50, 40),   # RR, RL
        (30, 20, 10, 5, 1),     # LL, LL
        (30, 20, 10, 1, 5),     # LL, LR
        (5, 4, 6, 3, 7, 2, 8),  # LL, RR
        (range(0, 30, 3)),
        (range(0, 31, 3)),
        (range(0, 34, 3)),
        (range(10, -10, -2)),
        ('A', 'B', 'C', 'D', 'E'),
        (1, 1, 1, 1),
    )
    for case in test_cases:
        tree = AVL(case)
        print('INPUT  :', case)
        print('RESULT :', tree)

    print("\nPDF - method add() example 3")
    print("----------------------------")
    for _ in range(100):
        case = list(set(random.randrange(1, 20000) for _ in range(900)))
        tree = AVL()
        for value in case:
            tree.add(value)
        if not tree.is_valid_avl():
            raise Exception("PROBLEM WITH ADD OPERATION")
    print('add() stress test finished')

    print("\nPDF - method remove() example 1")
    print("-------------------------------")
    test_cases = (
        ((1, 2, 3), 1),  # no AVL rotation
        ((1, 2, 3), 2),  # no AVL rotation
        ((1, 2, 3), 3),  # no AVL rotation
        ((50, 40, 60, 30, 70, 20, 80, 45), 0),
        ((50, 40, 60, 30, 70, 20, 80, 45), 45),  # no AVL rotation
        ((50, 40, 60, 30, 70, 20, 80, 45), 40),  # no AVL rotation
        ((50, 40, 60, 30, 70, 20, 80, 45), 30),  # no AVL rotation
    )
    for case, del_value in test_cases:
        tree = AVL(case)
        print('INPUT  :', tree, "DEL:", del_value)
        tree.remove(del_value)
        print('RESULT :', tree)

    print("\nPDF - method remove() example 2")
    print("-------------------------------")
    test_cases = (
        ((50, 40, 60, 30, 70, 20, 80, 45), 20),  # RR
        ((50, 40, 60, 30, 70, 20, 80, 15), 40),  # LL
        ((50, 40, 60, 30, 70, 20, 80, 35), 20),  # RL
        ((50, 40, 60, 30, 70, 20, 80, 25), 40),  # LR
    )
    for case, del_value in test_cases:
        tree = AVL(case)
        print('INPUT  :', tree, "DEL:", del_value)
        tree.print_tree()
        tree.remove(del_value)
        print('RESULT :', tree)
        tree.print_tree()
        print('')

    print("\nPDF - method remove() example 3")
    print("-------------------------------")
    case = range(-9, 16, 2)
    tree = AVL(case)
    for del_value in case:
        print('INPUT  :', tree, del_value)
        tree.remove(del_value)
        print('RESULT :', tree)

    print("\nPDF - method remove() example 4")
    print("-------------------------------")
    case = range(0, 34, 3)
    tree = AVL(case)
    for _ in case[:-2]:
        root_value = tree.get_root().value
        print('INPUT  :', tree, root_value)
        tree.remove(root_value)
        print('RESULT :', tree)

    print("\nPDF - method remove() example 5")
    print("-------------------------------")
    for _ in range(100):
        case = list(set(random.randrange(1, 20000) for _ in range(900)))
        tree = AVL(case)
        for value in case[::2]:
            tree.remove(value)
        if not tree.is_valid_avl():
            raise Exception("PROBLEM WITH REMOVE OPERATION")
    print('remove() stress test finished')

    print("\nPDF - method contains() example 1")
    print("---------------------------------")
    tree = AVL([10, 5, 15])
    print(tree.contains(15))
    print(tree.contains(-10))
    print(tree.contains(15))

    print("\nPDF - method contains() example 2")
    print("---------------------------------")
    tree = AVL()
    print(tree.contains(0))

    print("\nPDF - method inorder_traversal() example 1")
    print("---------------------------------")
    tree = AVL([10, 20, 5, 15, 17, 7, 12])
    print(tree.inorder_traversal())

    print("\nPDF - method inorder_traversal() example 2")
    print("---------------------------------")
    tree = AVL([8, 10, -4, 5, -1])
    print(tree.inorder_traversal())

    print("\nPDF - method find_min() example 1")
    print("---------------------------------")
    tree = AVL([10, 20, 5, 15, 17, 7, 12])
    print(tree)
    print("Minimum value is:", tree.find_min())

    print("\nPDF - method find_min() example 2")
    print("---------------------------------")
    tree = AVL([8, 10, -4, 5, -1])
    print(tree)
    print("Minimum value is:", tree.find_min())

    print("\nPDF - method find_max() example 1")
    print("---------------------------------")
    tree = AVL([10, 20, 5, 15, 17, 7, 12])
    print(tree)
    print("Maximum value is:", tree.find_max())

    print("\nPDF - method find_max() example 2")
    print("---------------------------------")
    tree = AVL([8, 10, -4, 5, -1])
    print(tree)
    print("Maximum value is:", tree.find_max())

    print("\nPDF - method is_empty() example 1")
    print("---------------------------------")
    tree = AVL([10, 20, 5, 15, 17, 7, 12])
    print("Tree is empty:", tree.is_empty())

    print("\nPDF - method is_empty() example 2")
    print("---------------------------------")
    tree = AVL()
    print("Tree is empty:", tree.is_empty())

    print("\nPDF - method make_empty() example 1")
    print("---------------------------------")
    tree = AVL([10, 20, 5, 15, 17, 7, 12])
    print("Tree before make_empty():", tree)
    tree.make_empty()
    print("Tree after make_empty(): ", tree)

    print("\nPDF - method make_empty() example 2")
    print("---------------------------------")
    tree = AVL()
    print("Tree before make_empty():", tree)
    tree.make_empty()
    print("Tree after make_empty(): ", tree)
