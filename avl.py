# Name:John Fletcher
# OSU Email: fletjohn@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: Assignment 4
# Due Date: 11/12/2024
# Description: Implementation of binary search tree class


import random

from numpy.ma.core import left_shift

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
        Removes a node with the given value from the AVL tree.
        Returns True if the node is removed, False otherwise.
        """
        parent = None
        current = self._root

        # Step 1: Find the node to be removed and its parent
        while current and current.value != value:
            parent = current
            if value < current.value:
                current = current.left
            else:
                current = current.right

        # If the node was not found, return False
        if current is None:
            return False

        # Step 2: Remove the node (same as in the BST deletion)
        # Case 1: Node to be removed has no children (leaf node)
        if current.left is None and current.right is None:
            print("Entered Case 1")
            if parent is None:  # The tree only has one node
                self._root = None
            elif parent.left == current:
                parent.left = None
            else:
                parent.right = None

        # Case 2: Node to be removed has one child
        elif current.left is None or current.right is None:
            print("Entered Case 2")
            child = current.left if current.left else current.right
            if parent is None:  # The root is being removed
                self._root = child
            elif parent.left == current:
                parent.left = child
            else:
                parent.right = child

        # Case 3: Node to be removed has two children
        else:
            print("Entered Case 3")
            # Find the in-order successor (smallest node in the right subtree)
            successor_parent = current
            successor = current.right
            while successor.left:
                successor_parent = successor
                successor = successor.left

            # Replace current's value with the successor's value
            current.value = successor.value

            # Remove the successor
            if successor_parent.left == successor:
                successor_parent.left = successor.right
            else:
                successor_parent.right = successor.right

        # Step 3: Rebalance the tree starting from the parent of the deleted node
        # We will start from the parent and propagate upwards to the root
        node = parent if parent else current  # Start rebalancing from the parent or current node
        while node:
            # Update the height of the current node
            node.height = max(self._get_height(node.left), self._get_height(node.right)) + 1

            # Get the balance factor of the current node
            balance = self._balance_factor(node)

            # If the node becomes unbalanced, apply rotations
            # Left Left Case
            if balance > 1 and self._balance_factor(node.left) >= 0:
                node = self._rotate_right(node)

            # Left Right Case
            elif balance > 1 and self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
                node = self._rotate_right(node)

            # Right Right Case
            elif balance < -1 and self._balance_factor(node.right) <= 0:
                node = self._rotate_left(node)

            # Right Left Case
            elif balance < -1 and self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
                node = self._rotate_left(node)

            # Move up to the parent node for the next iteration
            # If the current node is the root, we stop
            if node == self._root:
                break
            else:
                # The parent is tracked by our loop through the binary tree
                parent = node.parent  # You'll need a method to track the parent
                node = parent

        self._rebalance(node)

        print(self.is_valid_avl())

        return True

    def _update_height(self, node):
        while node:
            left_height = node.left.height if node.left else -1
            right_height = node.right.height if node.right else -1
            node.height = 1 + max(left_height, right_height)
            node = node.parent

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

    def _find(self, value: object) -> AVLNode:
        """
        Find and return the node with the given value in the AVL tree.
        """
        current = self._root
        while current:
            if value < current.value:
                current = current.left
            elif value > current.value:
                current = current.right
            else:
                return current  # Found the node
        return None  # Node not found

    # It's highly recommended to implement                          #
    # the following methods for balancing the AVL Tree.             #
    # Remove these comments.                                        #
    # Remove these method stubs if you decide not to use them.      #
    # Change these methods in any way you'd like.                   #

    def _balance_factor(self, node: AVLNode) -> int:
        # Safely get the height of the left child
        if node is None:
            return 0  # A None node is considered balanced with no height.
        left_height = 0
        right_height = 0

        if node.left is None:
            left_height = -1

        if node.right is None:
            right_height = -1

        left_height = node.left.height if node.left else -1

        # Safely get the height of the right child
        right_height = node.right.height if node.right else -1

        # Return the balance factor (difference between left and right subtree heights)
        return left_height - right_height

    def _get_height(self, node: AVLNode) -> int:
        """
        Returns the height of the given node.
        If the node is None, returns -1, as an empty subtree has a height of -1.
        """
        if node is None:
            return -1  # An empty subtree has a height of -1.
        return node.height  # Return the stored height of the node.

    def _rotate_left(self, node: AVLNode) -> AVLNode:
        print("Rotate Left Called")
        new_root = node.right  # Step 1: Set the new root to the right child of the node
        node.right = new_root.left  # Step 2: Set the right child of node to be the left child of new_root
        if new_root.left:
            new_root.left.parent = node  # Step 3: Update parent of the left child of new_root (if any)
        new_root.left = node  # Step 4: Set node as the left child of new_root

        new_root.parent = node.parent  # Step 5: Set the parent of new_root to the parent's of node
        if node.parent:
            if node.parent.left == node:  # Step 6: Update parent's left or right child pointer
                node.parent.left = new_root
            else:
                node.parent.right = new_root
        else:
            self._root = new_root  # Step 7: If node was the root, update the tree's root to new_root

        node.parent = new_root  # Step 8: Set node's parent to be new_root
        self._update_height(node)  # Step 9: Update the height of the rotated node
        self._update_height(new_root)  # Step 10: Update the height of the new root

        return new_root  # Step 11: Return the new root of the rotated subtree

    def _rotate_right(self, node: AVLNode) -> AVLNode:
        print("Rotate Right Called")
        new_root = node.left
        node.left = new_root.right
        if new_root.right:
            new_root.right.parent = node
        new_root.right = node

        # Update parent pointers
        new_root.parent = node.parent
        if node.parent:
            if node.parent.left == node:
                node.parent.left = new_root
            else:
                node.parent.right = new_root
        else:
            self._root = new_root

        node.parent = new_root

        # Update heights
        self._update_height(node)
        self._update_height(new_root)

        return new_root

    def _rebalance(self, node: AVLNode) -> AVLNode:
        balance = self._balance_factor(node)

        # Left-heavy case
        if balance > 1:
            # Left-Right case (double rotation)
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)  # Rotate left on the left child
            # Left-Left case (single rotation)
            return self._rotate_right(node)  # Rotate right on the node

        # Right-heavy case
        if balance < -1:
            # Right-Left case (double rotation)
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)  # Rotate right on the right child
            # Right-Right case (single rotation)
            return self._rotate_left(node)  # Rotate left on the node

        return node  # Balanced, no rotation needed

    def _find_min(self, node: AVLNode) -> AVLNode:
        """
        Returns the node with the minimum value in the given subtree.
        """
        current = node
        while current.left:
            current = current.left  # Move to the leftmost node
        return current




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
