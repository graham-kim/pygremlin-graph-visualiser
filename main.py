from canvas import Canvas
from spec import ArrowDraw, NodeSpec, NullNode
from formation import FormationManager

if __name__ == '__main__':
    mgr = FormationManager()
    n1 = mgr.add_node("abc\nwiga", (400,300), "lime", multibox=True)
    n2 = mgr.add_node("def", (200,100), "green")
    mgr.add_dual_link(n1, n2, "blue", "red")

    children = mgr.add_depth_line_of_linked_nodes( \
        n2, dir=(0,1), link_length=200, node_specs=[
            NodeSpec("ghi", node_col="red", link_col="pink", link_draw=ArrowDraw.FWD_ARROW),
            NodeSpec("jkl", node_col="green", link_col="pink", link_draw=ArrowDraw.FWD_ARROW),
            NullNode(link_col="pink", link_draw=ArrowDraw.DOUBLE_ARROW)
        ])

    id = mgr.id_of
    mgr.add_label("waha", mgr.pos_perp_to(n2, id("ghi"), 200, to_left=False), "red")

    n3 = mgr.add_linked_node(children[0], (600,500), NodeSpec("xyz", node_col="green", link_col="purple", \
                             link_draw=ArrowDraw.DUAL_LINK, link_2_col="orange"))

    mgr.add_breadth_line_of_sibling_nodes( \
        n3, start_coord=(800,700), end_coord=(800,300), node_specs=[
            NodeSpec("aaa", node_col="red", link_col="teal", link_draw=ArrowDraw.DOUBLE_ARROW),
            NodeSpec("bbb", node_col="red", link_col="teal", link_draw=ArrowDraw.DOUBLE_ARROW),
            None,
            NodeSpec("ccc", node_col="purple", link_col="teal", link_draw=ArrowDraw.DOUBLE_ARROW, multibox=True)
        ])

    mgr.add_arc_of_sibling_nodes( \
        n1, radius=200, start_dir_coord=(700, 200), end_dir_coord=(300, 50), clockwise=False, node_specs=[
            NodeSpec("dd", node_col="blue", link_col="lime", link_draw=ArrowDraw.FWD_ARROW),
            NodeSpec("ee", node_col="pink", link_col="lime", link_draw=ArrowDraw.FWD_ARROW),
            NodeSpec("ff", node_col="magenta", link_col="lime", link_draw=ArrowDraw.NO_ARROW),
            NodeSpec("gg", node_col="navy", link_col="lime", link_draw=ArrowDraw.BACK_ARROW),
            NodeSpec("ii", node_col="teal", link_col="lime", link_draw=ArrowDraw.NO_LINK),
            NodeSpec("jj", node_col="purple", link_col="lime", link_draw=ArrowDraw.FWD_ARROW)
        ])

    mgr.add_rail_of_nodes(start_coord=(70,100), dir=(0,1), link_length=100, node_specs=[ \
            NodeSpec("ab"),
            NodeSpec("bc"),
            NodeSpec("cd")
        ])

    c = Canvas(mgr.nodes, mgr.links, mgr.labels)
    c.main_loop()