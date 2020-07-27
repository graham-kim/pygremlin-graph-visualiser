from canvas import Canvas
import model

if __name__ == '__main__':
    mgr = model.FormationManager()
    n1 = mgr.add_node("abc", (400,300), "red")
    n2 = mgr.add_node("def", (300,200), "green")
    mgr.add_link(n1, n2)

    children = mgr.add_depth_line_of_linked_nodes( \
        n2, (300,500), 200, True, [
        ("ghi", "red"),
        ("jkl", "green"),
        ("mno", "red")
    ])

    mgr.add_linked_node(children[0], "xyz", (600,500), "green")

    c = Canvas(mgr.nodes, mgr.links)
    c.main_loop()