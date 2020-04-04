def trait_find_child_by_name(self, name, widget=None):
    if self.get_name() == name:
        return self
    if hasattr(self, 'get_children') and self.get_children():
        for w in self.get_children():
            ret = w.find_child_by_name(name)
            if ret:
                return ret


def trait_remove_all(self):
    for c in self.get_children():
        self.remove(c)
