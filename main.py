from canvas import Canvas
import model

if __name__ == '__main__':
    mgr = model.FormationManager()
    n1 = mgr.add_node("abc", (400,300), "red")
    n2 = mgr.add_node("def", (300,200), "green")
    mgr.add_link(n1, n2)

    mgr.add_depth_line_of_linked_nodes(n2, (700,100), 200, [
        ("ghi", "red"),
        ("jkl", "green"),
        ("mno", "red")
    ])

    c = Canvas(mgr.nodes, mgr.links)
    c.main_loop()