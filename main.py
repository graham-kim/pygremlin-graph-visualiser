from canvas import Canvas
import model

if __name__ == '__main__':
    mgr = model.FormationManager()
    n1 = mgr.add_node("abc", (400,300), "red", multibox=True)
    n2 = mgr.add_node("def", (300,200), "green")
    mgr.add_link(n1, n2, "blue")

    children = mgr.add_depth_line_of_linked_nodes( \
        n2, (300,500), 200, "pink", False, [
        ("ghi", "red"),
        ("jkl", "green"),
        ("mno", "red")
    ])

    n3 = mgr.add_linked_node(children[0], "xyz", (600,500), "green", "purple")

    mgr.add_breadth_line_of_sibling_nodes( \
        n3, (800,700), (800,300), "teal", False, [
        ("aaa", "red"),
        ("bbb", "red"),
        None,
        ("ccc", "green")
    ])

    mgr.add_arc_of_sibling_nodes( \
        n1, 200, (700, 200), (300, 50), False, "lime", True, [
        ("dd", "blue"),
        ("ee", "pink"),
        ("ff", "magenta"),
        ("gg", "navy"),
        ("ii", "teal"),
        ("jj", "purple")
    ])

    c = Canvas(mgr.nodes, mgr.links)
    c.main_loop()