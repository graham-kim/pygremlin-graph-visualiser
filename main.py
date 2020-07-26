from canvas import Canvas
import model

if __name__ == '__main__':
    nodes = [
        model.Node("abc", (400,300), "red"),
        model.Node("def", (300,200), "blue")
    ]

    links = [
        model.Link(nodes[0], nodes[1])
    ]

    c = Canvas(nodes, links)
    c.main_loop()