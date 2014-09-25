

class TreeElement(object):
    parent_id = None

    def __init__(self, id, children={}, **kwargs):
        self.id = str(id)
        self.children = children
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def has_child(self, child):
        return child.id in self.children

    def add_child(self, child):
        self.children[child.id] = child

    def remove_child(self, child):
        self.children.pop(child)

    def to_dict(self):
        data = {self.id: self.__dict__.copy()}
        data[self.id]['children'] = []
        for child in self.children:
            data[self.id]['children'].append(self.children[child].to_dict())
        return data


class Tree(object):
    root = None

    def __init__(self, id, children={}, **kwargs):
        self.root = TreeElement(id, children, **kwargs)

    def add_element(self, element, parent_id):
        parent_id = str(parent_id)
        parent = self.find_element(parent_id)
        if parent is not None:
            parent.add_child(element)
            return True
        return False

    def remove_element(self, element):
        tree_element = self.find_element(element.id)
        if tree_element is not None:
            parent = self.find_element(tree_element.parent_id)
            parent.remove_child(element)
            return True
        return False

    def _find_element(self, element, element_id):
        if element_id in element.children:
            return element.children[element_id]
        else:
            for child in element.children:
                self._find_element(child, element_id)
        return None

    def find_element(self, element_id):
        element_id = str(element_id)
        if self.root.id == element_id:
            return self.root
        else:
            return self._find_element(self.root, element_id)

    def to_dict(self):
        return self.root.to_dict()
