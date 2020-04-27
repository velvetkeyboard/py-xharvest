def find_child_by_name(widget, name):
    if widget.get_name() == name:
        return widget
    if hasattr(widget, "get_children"):
        for w in widget.get_children():
            ret = find_child_by_name(w, name)
            if ret:
                return ret


def remove_all_children(widget):
    for c in widget.get_children():
        widget.remove(c)
