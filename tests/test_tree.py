from __future__ import unicode_literals

import unittest

from todoflow.todos import TreeNode


class TestTree(unittest.TestCase):
    def test_init(self):
        TreeNode()

    def test_get_values(self):
        tree = TreeNode('v')
        self.assertEqual('v', tree.get_value())

    def test_append_child(self):
        tree = TreeNode()
        tree.append('v1')
        tree.append('v2')
        values = tree.get_values()
        self.assertEqual(('v1', 'v2'), values)

    def test_prepend_child(self):
        tree = TreeNode()
        tree.append('v2')
        tree.prepend('v1')
        values = tree.get_values()
        self.assertEqual(('v1', 'v2'), values)

    def test_parent_values(self):
        node3 = TreeNode('v3')
        node2 = TreeNode('v2', [node3])
        node1 = TreeNode('v1', [node2])
        self.assertEqual(
            tuple(node3.iter_parents_values()),
            ('v2', 'v1')
        )
        self.assertEqual(
            node3.get_parents_values(),
            ('v2', 'v1')
        )

    def test_get_level(self):
        node3 = TreeNode('v3')
        node2 = TreeNode('v2', [node3])
        node1 = TreeNode('v1', [node2])
        self.assertEqual(2, node3.get_level())
        self.assertEqual(1, node2.get_level())
        self.assertEqual(0, node1.get_level())

    def build_tree(self, root_value=None, values=None):
        root = TreeNode(value=root_value)
        if not values:
            return root
        prev_nodes = [root]
        for level in values:
            levelnodes = [[TreeNode(v) for v in for_node] for for_node in level]
            new_prev_nodes = []
            for node, children in zip(prev_nodes, levelnodes):
                node.set_children(children)
                new_prev_nodes.extend(children)
            prev_nodes = new_prev_nodes
        return root

    def build_tree_1(self):
        return self.build_tree(
            'root',
            [
                [['v1-0',              'v1-1']],
                [['v2-0-0', 'v2-0-1'], ['v2-1-0', 'v2-1-1']]
            ]
        )

    def test_iter(self):
        tree = self.build_tree_1()
        self.assertEqual(
            tree.get_values(),
            ('root', 'v1-0', 'v2-0-0', 'v2-0-1', 'v1-1', 'v2-1-0', 'v2-1-1')
        )

    def test_search(self):
        tree = self.build_tree_1()
        self.assertEqual(
            set(tree.search(lambda n: '0' in n.get_value())),
            set(['v1-0', 'v2-1-0', 'v2-0-0', 'v2-0-1'])
        )

    def test_search_no_math(self):
        tree = self.build_tree_1()
        self.assertEqual(
            set(tree.search(lambda n: False)),
            set()
        )

    def test_filter(self):
        tree = self.build_tree_1()
        self.assertEqual(
            tree.filter(lambda n: '0' in n.get_value()).get_values(),
            ('root', 'v1-0', 'v2-0-0', 'v2-0-1', 'v1-1', 'v2-1-0')
        )

    def test_find(self):
        tree = self.build_tree_1()
        self.assertEqual(tree.find('v2-0-0').get_value(), 'v2-0-0')

if __name__ == '__main__':
    unittest.main()
