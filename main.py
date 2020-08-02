from canvas import Canvas
from spec import ArrowDraw, NodeSpec, NullNode
import model

if __name__ == '__main__':
    mgr = model.FormationManager()
    n1 = mgr.add_node("abc\nwiga", (400,300), "red", multibox=True)
    n2 = mgr.add_node("def", (200,100), "green")
    mgr.add_dual_link(n1, n2, "blue", "red")

    children = mgr.add_depth_line_of_linked_nodes( \
        n2, dir_coord=mgr.pos_of(n2)+(0,1), link_length=200, node_specs=[
            NodeSpec("ghi", node_col="red", link_col="pink", link_draw=ArrowDraw.FWD_ARROW),
            NodeSpec("jkl", node_col="green", link_col="pink", link_draw=ArrowDraw.FWD_ARROW),
            NullNode(link_col="pink", link_draw=ArrowDraw.DOUBLE_ARROW)
        ])

    n3 = mgr.add_linked_node(children[0], (600,500), NodeSpec("xyz", node_col="green", link_col="purple", \
                             link_draw=ArrowDraw.FWD_ARROW))

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

    c = Canvas(mgr.nodes, mgr.links)
    c.main_loop()