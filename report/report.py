from manimlib import *


class Node:
    circle: Circle
    name: Text
    color: str
    stroke_color: str
    text_name: str

    def __init__(self, circle, color=None, stroke_color=None, name=None):
        self.circle = circle
        self.color = color
        self.stroke_color = stroke_color
        self.name = name
        if color is None:
            self.color = circle.get_color()
        if stroke_color is None:
            self.stroke_color = circle.get_stroke_color()

    def objects(self):
        return VGroup(self.circle, self.name)

    def set_updater(self, scene):
        self.name.add_updater(lambda m:
                              m.move_to(self.circle.get_center())
                              .set_height(self.circle.get_radius() / 1.25))
        scene.add(self.name)

    def set_color_animation(self):
        return self.circle.animate.set_color(self.color) \
            .set_stroke(self.stroke_color)


class Edge:
    line: Line
    start: Node
    end: Node

    def __init__(self, start, end, object_type=Line):
        self.line = object_type(start.circle.get_center(),
                                end.circle.get_center())
        self.line.set_length(
            self.line.get_length() - (0.7 if object_type is Line else 0.2))

        self.start = start
        self.end = end

    def add_gradient(self):
        return self.line.animate.set_color(
            color=[self.start.color, WHITE, self.end.color])

    def add_updater(self, scene):
        self.line.add_updater(
            lambda m: m.put_start_and_end_on(
                self.start.circle.get_center(),
                self.end.circle.get_center()
            ).set_length(m.get_length() - 0.7))
        scene.add(self.line)

    def revert_arrow(self):
        return self.line.animate.put_start_and_end_on(
            self.end.circle.get_center(),
            self.start.circle.get_center()
        ).set_length(self.line.get_length())

    def normalize_arrow(self):
        return self.line.animate.put_start_and_end_on(
            self.start.circle.get_center(),
            self.end.circle.get_center()
        ).set_length(self.line.get_length())


class Graph:
    nodes: list
    edges: list

    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    def get_objects(self):
        return VGroup(*[node.circle for node in self.nodes],
                      *[edge.line for edge in self.edges])

    def add_edges_gradients(self, scene):
        ans = []
        for edge in self.edges:
            ans += [edge.add_gradient()]
        scene.play(*ans)

    def get_animations_colors_check(self, *colors):
        ans = []
        for idx, node in enumerate(self.nodes):
            node.color = colors[idx][0]
            node.stroke_color = colors[idx][1]
            ans += [node.circle.animate.set_color(node.color)
                        .set_stroke(node.stroke_color)]
        return ans


class Video(Scene):
    a = 0
    b = None

    # def play(self, *args, **kwargs):
    #     if self.b is not None:
    #         self.remove(self.b)
    #     self.b = Text(str(self.a)).to_edge(UR)
    #     self.add(self.b)
    #     self.a += 1

        # super(Video, self).play(*args, **kwargs)

    def construct(self):
        nodes, node_counter = self.make_nodes()
        edges, edge_counter = self.make_edges(nodes)
        graph = Graph(nodes, edges)
        hide_stuff = self.show_answer(graph)
        self.play(graph.get_objects().animate.shift(UP * 1.7 + RIGHT * 4.5),
                  FadeOut(hide_stuff), FadeOut(node_counter),
                  FadeOut(edge_counter))
        statements, impl_edges, statements_group = \
            self.start_solution(nodes, edges)
        components_show = self.show_strong_components()
        self.play(VGroup(components_show, statements_group)
                  .animate.shift(DOWN * 8))
        self.remove(components_show)
        del components_show
        self.statements_components(statements, statements_group)
        self.wait()
        self.thanks()

    def make_nodes(self):
        circles = [Node(Circle(stroke_color=GREY, stroke_width=4,
                               fill_color=WHITE, fill_opacity=0.5),
                        RED, RED_E)]
        self.play(DrawBorderThenFill(circles[0].circle))
        self.play(
            circles[0].circle.animate.shift(UP * 2).set_width(0.5))
        circles += [Node(circles[0].circle.copy(), RED, RED_E),
                    Node(circles[0].circle.copy(), BLUE, BLUE_E),
                    Node(circles[0].circle.copy(), GREEN, GREEN_E),
                    Node(circles[0].circle.copy(), BLUE, BLUE_E)]
        self.play(*[Rotate(circles[i].circle, 2 * i * PI / 5,
                           about_point=ORIGIN) for i in range(5)])

        node_counter_circle = circles[0].circle.copy()
        self.play(node_counter_circle.animate.to_edge(UL, buff=0.2))
        node_counter_text = Tex(r"\leq 1000").set_height(0.3) \
            .move_to(node_counter_circle.get_right(),
                     aligned_edge=LEFT).shift(
            RIGHT * 0.2)
        self.play(Write(node_counter_text))
        node_counter = VGroup(node_counter_circle, node_counter_text)
        self.play(FlashAround(node_counter, color=WHITE))
        self.wait(2)

        objects = VGroup(*[it.circle for it in circles])
        self.play(objects.animate.shift(DOWN * 1.25)
                  .scale(4, about_edge=UP))
        self.animate_first_colors(circles[0].circle)
        self.play(objects.animate.shift(UP * 1.25)
                  .scale(0.25, about_edge=UP))
        self.play(*[circles[i].set_color_animation() for i in range(1, 5)])
        return circles, node_counter

    def animate_first_colors(self, first_circle):
        colors_rect = RoundedRectangle(height=6, width=2,
                                       corner_radius=0.2,
                                       fill_opacity=0.5, fill_color=GREY,
                                       stroke_color=GREY_D)
        color_circles = [
            Circle(radius=0.7, fill_color=RED, fill_opacity=0.5,
                   stroke_color=RED_E).shift(UP * 1.8),
            Circle(radius=0.7, fill_color=GREEN, fill_opacity=0.5,
                   stroke_color=GREEN_E),
            Circle(radius=0.7, fill_color=BLUE, fill_opacity=0.5,
                   stroke_color=BLUE_E).shift(DOWN * 1.8)]
        group = VGroup(colors_rect, *color_circles)
        group.shift(RIGHT * 4)
        self.play(DrawBorderThenFill(group))
        arrows = [Arrow(color_circles[0].get_center(),
                        first_circle.get_center(),
                        stroke_color=RED_C),
                  Arrow(color_circles[1].get_center(),
                        first_circle.get_center(),
                        stroke_color=GREEN_C),
                  Arrow(color_circles[2].get_center(),
                        first_circle.get_center(),
                        stroke_color=BLUE_C)]
        self.play(*[ShowCreation(arrow.set_length(arrow.get_length() - 2))
                    for arrow in arrows])
        self.wait(2)

        def highlight_arrow(chosen, *args):
            anims = []
            for arrow in args:
                if arrow == chosen:
                    anims += [arrow.animate.set_opacity(1)]
                else:
                    anims += [arrow.animate.set_opacity(0.2)]
            self.play(*anims)

        highlight_arrow(arrows[1], *arrows)
        highlight_arrow(arrows[2], *arrows)
        highlight_arrow(arrows[0], *arrows)
        transform_circle = color_circles[0].copy()
        self.play(transform_circle.animate.move_to(ORIGIN)
                  .rescale_to_fit(length=2, dim=1),
                  *[FadeOut(arrow) for arrow in arrows],
                  FadeOut(group),
                  FadeOut(first_circle))
        first_circle.set_color(RED)
        first_circle.set_stroke(RED_E)
        self.play(FadeIn(first_circle), FadeOut(transform_circle),
                  run_time=0.01)

    def make_edges(self, nodes):
        edges = [Edge(nodes[0], nodes[1]), Edge(nodes[1], nodes[2]),
                 Edge(nodes[2], nodes[3]), Edge(nodes[3], nodes[4]),
                 Edge(nodes[0], nodes[4]), Edge(nodes[0], nodes[2]),
                 Edge(nodes[1], nodes[3]), Edge(nodes[1], nodes[4])]
        self.play(*[ShowCreation(edge.line) for edge in edges])

        edge_counter_line = edges[0].line.copy()
        self.play(edge_counter_line.animate
                  .to_edge(UL, buff=0.65).shift(LEFT * 0.9)
                  .set_length(0.6).set_angle(-3 * PI / 4))
        edge_counter_text = Tex(r'\leq 20000').set_height(0.3) \
            .move_to(edge_counter_line.get_right(),
                     aligned_edge=LEFT).shift(
            RIGHT * 0.25)
        self.play(Write(edge_counter_text))
        edge_counter = VGroup(edge_counter_line, edge_counter_text)
        self.play(FlashAround(edge_counter, color=WHITE))
        self.wait(2)

        return edges, edge_counter

    def show_answer(self, graph):
        answer_nodes = deepcopy(graph.nodes)
        answer_edges = [Edge(answer_nodes[0], answer_nodes[1]),
                        Edge(answer_nodes[1], answer_nodes[2]),
                        Edge(answer_nodes[2], answer_nodes[3]),
                        Edge(answer_nodes[3], answer_nodes[4]),
                        Edge(answer_nodes[0], answer_nodes[4]),
                        Edge(answer_nodes[0], answer_nodes[2]),
                        Edge(answer_nodes[1], answer_nodes[3]),
                        Edge(answer_nodes[1], answer_nodes[4])]
        answer_graph = Graph(answer_nodes, answer_edges)
        original = graph.get_objects()
        answer = answer_graph.get_objects()
        arrow = Arrow(original.get_right() + LEFT * 3.5,
                      answer.get_left() + RIGHT * 3.5)
        self.play(original.animate.shift(LEFT * 3.5),
                  answer.animate.shift(RIGHT * 3.5),
                  FadeInFromPoint(arrow, ORIGIN))

        self.play(*answer_graph.get_animations_colors_check((BLUE, BLUE_E),
                                                            (GREEN,
                                                             GREEN_E),
                                                            (RED, RED_E),
                                                            (BLUE, BLUE_E),
                                                            (RED, RED_E)))

        answer_graph.add_edges_gradients(self)

        q = Text('?', height=1.5).to_edge(UP)

        self.play(Write(q),
                  graph.get_objects().animate.shift(DOWN * 1.7 + LEFT * 1),
                  answer_graph.get_objects().animate.shift(
                      DOWN * 1.7 + RIGHT * 1),
                  arrow.animate.shift(DOWN * 1.7))
        second_arrow = arrow.copy()

        self.play(arrow.animate.put_start_and_end_on(
            graph.get_objects().get_edge_center(UR),
            q.get_center() + LEFT * 1 + DOWN * 0.7),
            second_arrow.animate.put_start_and_end_on(
                q.get_center() + RIGHT * 1 + DOWN * 0.7,
                answer_graph.get_objects().get_edge_center(UL)))
        self.wait(2)

        return VGroup(answer_graph.get_objects(), arrow, second_arrow, q)

    def start_solution(self, nodes, edges):
        nodes_circles = VGroup(*[it.circle for it in nodes],
                               *[it.line for it in edges])

        nodes_circles.add(*self.name_nodes(nodes))
        self.play(nodes_circles.animate.shift(DOWN * 1.25)
                  .scale(4, about_edge=UP))
        arr1, arr2, a_st1, a_st2 = self.animate_possible_colors(
            nodes[0].circle,
            nodes[0].name)
        self.play(nodes_circles.animate.shift(UP * 1.25)
                  .scale(0.25, about_edge=UP),
                  VGroup(arr1, arr2, a_st1.objects(), a_st2.objects())
                  .animate.shift(UP * 1.2).scale(0.25, about_edge=DOWN))
        statements, arrows = self.animate_st_create(nodes[1:])
        statements = [(a_st1, a_st2)] + statements
        arrows += [arr1, arr2]
        self.separate_statements(statements, nodes_circles, arrows)
        impl_edges = self.show_implications(nodes, edges, statements,
                                            nodes_circles)
        statements_group = VGroup(*[st[0].objects() for st in statements],
                                  *[st[1].objects() for st in statements])
        self.play(nodes_circles.animate.shift(LEFT * 5),
                  statements_group.animate.move_to(ORIGIN))
        self.remove(nodes_circles)
        self.wait()
        self.play(statements_group.animate.shift(UP * 8))
        return statements, impl_edges, statements_group

    def name_nodes(self, nodes):
        texts = []
        animations = []
        for idx, node in enumerate(nodes):
            node.name = Text('ABCDE'[idx], height=0.2) \
                .move_to(node.circle.get_center())
            texts += [node.name]
            animations += [Write(node.name)]
        self.play(*animations)
        return texts

    def animate_possible_colors(self, circle, name):
        green = circle.copy()
        blue = circle.copy().shift(UP * 3).scale(0.5)
        green_arr = Arrow(green.get_top(), blue.get_bottom())
        blue_arr = green_arr.copy()
        self.play(green.animate.shift(UP * 3).scale(0.5),
                  FadeInFromPoint(green_arr, ORIGIN))

        self.play(Rotate(green_arr, PI / 6, about_point=circle.get_center()),
                  Rotate(blue_arr, -PI / 6, about_point=circle.get_center()),
                  green.animate.rotate_about_origin(PI / 6)
                  .set_color(GREEN).set_stroke(GREEN_E),
                  blue.animate.rotate_about_origin(-PI / 6)
                  .set_color(BLUE).set_stroke(BLUE_E))

        green.rotate_about_origin(0)
        blue.rotate_about_origin(0)

        blue_name = name.copy()
        green_name = name.copy()

        green_st = Node(green, name=green_name)
        blue_st = Node(blue, name=blue_name)

        self.play(green_name.animate.scale(0.5).move_to(green.get_center()),
                  blue_name.animate.scale(0.5).move_to(blue.get_center()))

        self.wait(2)

        green_st.set_updater(self)
        blue_st.set_updater(self)
        return blue_arr, green_arr, green_st, blue_st

    def animate_st_create(self, nodes):
        statements = []
        animations = []
        arrows = []
        for node in nodes:
            colors = [(RED, RED_E), (GREEN, GREEN_E), (BLUE, BLUE_E)]
            colors.remove((node.color, node.stroke_color))
            direction = node.circle.get_center() / \
                        np.sum(np.square(node.circle.get_center()))
            start_point = node.circle.get_center() + direction * -0.1
            end_point = start_point.copy() + (direction * 2)
            arrow_a = Arrow(start_point, end_point).scale(0.5) \
                .rotate(PI / 6, about_point=node.circle.get_center())
            arrow_b = Arrow(start_point, end_point).scale(0.5) \
                .rotate(-PI / 6, about_point=node.circle.get_center())
            a = node.circle.copy().scale(0.5).shift(direction * 1.52) \
                .rotate(PI / 6, about_point=node.circle.get_center()) \
                .set_color(colors[0][0]).set_stroke(colors[0][1])
            b = node.circle.copy().scale(0.5).shift(direction * 1.52) \
                .rotate(-PI / 6, about_point=node.circle.get_center()) \
                .set_color(colors[1][0]).set_stroke(colors[1][1])
            text_a = node.name.copy().scale(0.5).move_to(a.get_center())
            text_b = node.name.copy().scale(0.5).move_to(b.get_center())
            statements += [(Node(a, name=text_a), Node(b, name=text_b))]
            animations += [FadeInFromPoint(arrow_a, node.circle.get_center()),
                           FadeInFromPoint(arrow_b, node.circle.get_center()),
                           FadeInFromPoint(a, node.circle.get_center()),
                           FadeInFromPoint(b, node.circle.get_center()),
                           FadeInFromPoint(text_a, node.circle.get_center()),
                           FadeInFromPoint(text_b, node.circle.get_center())]
            arrows += [arrow_a, arrow_b]
        self.play(*animations)
        for st in statements:
            st[0].set_updater(self)
            st[1].set_updater(self)
        return statements, arrows

    def separate_statements(self, statements, graph, arrows):
        anims = [graph.animate.shift(LEFT * 3)]
        anims += [FadeOut(arrow) for arrow in arrows]
        for idx, sts in enumerate(statements):
            x_coord = 3 + 4 * (idx - 2) * sts[0].circle.get_radius() + 0.6 * (
                    idx - 2)
            anims += [sts[0].circle.animate.move_to(
                RIGHT * x_coord + UP * 0.7).scale(2),
                      sts[1].circle.animate.move_to(
                          RIGHT * x_coord + DOWN * 0.7).scale(2)]
        self.bring_to_front(statements[0][0].name)
        self.bring_to_front(statements[0][1].name)
        self.play(*anims)

    def show_implications(self, nodes, edges, statements, graph):
        st_group = VGroup(*[it[0].objects() for it in statements],
                          *[it[1].objects() for it in statements])
        self.play(graph.animate.scale(0.75).to_edge(DL),
                  st_group.animate.to_edge(DR))
        first_edges = self.first_variant(graph, nodes, statements)
        second_edges = self.second_variant(nodes, statements)
        self.play(graph.animate.scale(4 / 3).move_to(LEFT * 4.5))
        anims = []
        for idx in range(10):
            target = Point(RIGHT * 2.5 + UP * 3.5) \
                .rotate(-idx * PI / 5, about_point=RIGHT * 2.5)
            idx += 2
            b = idx // 5 % 2
            a = idx % 5
            if b == 1:
                a = 4 - a
            anims += [statements[a][b].objects().animate.move_to(target)]
        self.play(*anims)
        edges_copy = copy.copy(edges)
        edges_copy.pop(0)
        edges_copy.pop(2)
        new_edges = self.transform_edges(edges_copy, statements)
        old_edges_group = VGroup(*[edge.line for edge in edges_copy]).copy()
        new_edges_group = VGroup(*[edge.line for edge in new_edges])
        self.play(Transform(old_edges_group, new_edges_group))
        self.play(FadeOut(new_edges_group), run_time=0)
        self.play(FadeOut(old_edges_group), run_time=0)
        [edge.add_updater(self) for edge in new_edges]
        return list(first_edges) + list(second_edges) + new_edges

    def first_variant(self, graph, nodes, statements):
        a, b = deepcopy(nodes[:2])
        ab = Edge(a, b)
        self.wait(2)
        ab.add_updater(self)
        self.play(
            a.objects().animate.move_to(LEFT * 1.5 + UP * 3).scale(4 / 3),
            b.objects().animate.move_to(RIGHT * 1.5 + UP * 3).scale(4 / 3))

        arr = Arrow(UP * 2.7, UP * 1.7)
        a_p, a_n = deepcopy(statements[0])
        b_p, b_n = deepcopy(statements[1])
        a_p.name.clear_updaters()
        a_n.name.clear_updaters()
        b_p.name.clear_updaters()
        b_n.name.clear_updaters()
        self.play(FadeIn(arr),
                  a_p.objects().animate.move_to(UP * 1.4 + LEFT * 1.5),
                  a_n.objects().animate.move_to(LEFT * 1.5),
                  b_p.objects().animate.move_to(UP * 1.4 + RIGHT * 1.5),
                  b_n.objects().animate.move_to(RIGHT * 1.5))
        edges = [Edge(a_p, b_p), Edge(a_p, b_n),
                 Edge(a_n, b_p), Edge(a_n, b_n)]
        [edge.add_updater(self) for edge in edges]
        self.play(*[FadeIn(it.line) for it in edges])
        self.play(*[it.add_gradient() for it in edges])
        self.play(WiggleOutThenIn(edges[0].line),
                  WiggleOutThenIn(edges[3].line))
        self.play(FadeOut(edges[0].line),
                  FadeOut(edges[3].line))
        del edges[0]
        del edges[2]
        group = VGroup(a_p.objects(), a_n.objects(),
                       b_p.objects(), b_n.objects(),
                       a.objects(), b.objects(), arr)
        self.wait(2)
        self.play(group.animate.shift(RIGHT * graph.get_x()))
        separators = [Line(UP * 3.5 + RIGHT * 2.3, UP * 2 + RIGHT * 2.3),
                      Line(UP * 1 + RIGHT * 2.3, DOWN * 0.5 + RIGHT * 2.3),
                      Line(UP * 3.5 + LEFT * 2.7, DOWN * 0.5 + LEFT * 2.7),
                      Text('and', fill_color=ORANGE)
                          .move_to(RIGHT * 2.3 + UP * 1.5)]
        self.play(*[FadeIn(separator) for separator in separators])
        first_x, second_x = RIGHT * (-2.7 + 2.5), RIGHT * (2.3 + 2.5)
        first_a, first_b = deepcopy((a_p, b_p))
        second_a, second_b = deepcopy((a_n, b_n))
        first_edge = Text('or', fill_color=ORANGE).move_to(first_x + UP * 3)
        second_edge = Text('or', fill_color=ORANGE).move_to(second_x + UP * 3)
        self.play(
            FadeIn(first_edge),
            FadeIn(second_edge),
            first_a.objects().animate.move_to(first_x + LEFT + UP * 3),
            first_b.objects().animate.move_to(first_x + RIGHT + UP * 3),
            second_a.objects().animate.move_to(second_x + LEFT + UP * 3),
            second_b.objects().animate.move_to(second_x + RIGHT + UP * 3)
        )
        a_arrow = Arrow(UP * 2.7 + first_x, UP * 1.7 + first_x)
        b_arrow = Arrow(UP * 2.7 + second_x, UP * 1.7 + second_x)
        self.play(FadeIn(a_arrow), FadeIn(b_arrow))
        first_a1 = deepcopy(first_a)
        first_b1 = deepcopy(first_b)
        first_a1b1 = Edge(first_a1, first_b1, Arrow)
        first_a1b1.add_updater(self)
        second_a1 = deepcopy(second_a)
        second_b1 = deepcopy(second_b)
        second_a1b1 = Edge(second_a1, second_b1, Arrow)
        second_a1b1.add_updater(self)
        self.play(
            first_a1.circle.animate.move_to(
                UP * 1.4 + first_x + LEFT * 0.7)
                .set_color(BLUE).set_stroke(BLUE_E),
            first_a1.name.animate.move_to(
                UP * 1.4 + first_x + LEFT * 0.7),
            first_b1.objects().animate.move_to(
                UP * 1.4 + first_x + RIGHT * 0.7),
            second_a1.circle.animate.move_to(
                UP * 1.4 + second_x + LEFT * 0.7)
                .set_color(GREEN).set_stroke(GREEN_E),
            second_a1.name.animate.move_to(
                UP * 1.4 + second_x + LEFT * 0.7),
            second_b1.objects().animate.move_to(
                UP * 1.4 + second_x + RIGHT * 0.7),
            FadeIn(first_a1b1.line), FadeIn(second_a1b1.line)
        )
        first_and = Text('and', fill_color=ORANGE).move_to(first_x + UP * 0.7)
        first_a2 = deepcopy(first_a)
        first_b2 = deepcopy(first_b)
        first_a2b2 = Edge(first_b2, first_a2, Arrow)
        first_a2b2.add_updater(self)
        second_and = Text('and', fill_color=ORANGE).move_to(
            second_x + UP * 0.7)
        second_a2 = deepcopy(second_a)
        second_b2 = deepcopy(second_b)
        second_a2b2 = Edge(second_b2, second_a2, Arrow)
        second_a2b2.add_updater(self)
        self.play(
            first_a2.objects().animate.move_to(first_x + LEFT * 0.7),
            first_b2.circle.animate.move_to(
                first_x + RIGHT * 0.7).set_color(BLUE).set_stroke(BLUE_E),
            first_b2.name.animate.move_to(first_x + RIGHT * 0.7),
            second_a2.objects().animate.move_to(second_x + LEFT * 0.7),
            second_b2.circle.animate.move_to(
                second_x + RIGHT * 0.7).set_color(GREEN).set_stroke(GREEN_E),
            second_b2.name.animate.move_to(second_x + RIGHT * 0.7),
            FadeIn(first_a2b2.line), FadeIn(second_a2b2.line),
            FadeInFromPoint(first_and, first_and.get_center()),
            FadeInFromPoint(second_and, second_and.get_center())
        )
        self.play(
            first_a1.objects().animate.move_to(statements[0][1].circle),
            first_a2.objects().animate.move_to(statements[0][0].circle),
            first_b1.objects().animate.move_to(statements[1][0].circle),
            first_b2.objects().animate.move_to(statements[1][1].circle),
            second_a1.objects().animate.move_to(statements[0][0].circle),
            second_a2.objects().animate.move_to(statements[0][1].circle),
            second_b1.objects().animate.move_to(statements[1][1].circle),
            second_b2.objects().animate.move_to(statements[1][0].circle),
        )
        self.play(
            FadeOut(first_a1.objects()),
            FadeOut(first_a2.objects()),
            FadeOut(first_b1.objects()),
            FadeOut(first_b2.objects()),
            FadeOut(second_a1.objects()),
            FadeOut(second_a2.objects()),
            FadeOut(second_b1.objects()),
            FadeOut(second_b2.objects())
        )
        self.play(
            FadeOut(group),
            *[FadeOut(edge.line) for edge in edges],
            FadeOut(ab.line),
            *[FadeOut(it) for it in separators],
            FadeOut(first_a.objects()),
            FadeOut(first_b.objects()),
            FadeOut(second_a.objects()),
            FadeOut(second_b.objects()),
            FadeOut(first_edge),
            FadeOut(first_and),
            FadeOut(second_edge),
            FadeOut(second_and),
            FadeOut(a_arrow),
            FadeOut(b_arrow)
        )
        first_a1b1.start = statements[0][0]
        first_a1b1.end = statements[1][1]
        first_a2b2.start = statements[1][1]
        first_a2b2.end = statements[0][0]
        second_a1b1.start = statements[0][1]
        second_a1b1.end = statements[1][0]
        second_a2b2.start = statements[1][0]
        second_a2b2.end = statements[0][1]
        first_a1b1.add_updater(self)
        first_a2b2.add_updater(self)
        second_a1b1.add_updater(self)
        second_a2b2.add_updater(self)
        return first_a1b1, first_a2b2, second_a1b1, second_a2b2

    def second_variant(self, nodes, statements):
        a, b = deepcopy(nodes[-2:])
        ab = Edge(a, b)
        ab.add_updater(self)
        self.play(
            a.objects().animate.move_to(LEFT * 1.5 + UP * 3).scale(4 / 3),
            b.objects().animate.move_to(RIGHT * 1.5 + UP * 3).scale(4 / 3))
        arr = Arrow(UP * 2.7, UP * 1.7)
        a_p, a_n = deepcopy(statements[3])
        b_p, b_n = deepcopy(statements[4])
        a_p.name.clear_updaters()
        a_n.name.clear_updaters()
        b_p.name.clear_updaters()
        b_n.name.clear_updaters()
        self.play(FadeIn(arr),
                  a_p.objects().animate.move_to(UP * 1.4 + LEFT * 1.5),
                  a_n.objects().animate.move_to(LEFT * 1.5),
                  b_p.objects().animate.move_to(UP * 1.4 + RIGHT * 1.5),
                  b_n.objects().animate.move_to(RIGHT * 1.5))
        edges = [Edge(a_p, b_p), Edge(a_p, b_n),
                 Edge(a_n, b_p), Edge(a_n, b_n)]
        [edge.add_updater(self) for edge in edges]
        self.play(*[FadeIn(it.line) for it in edges])
        self.play(*[it.add_gradient() for it in edges])
        self.play(WiggleOutThenIn(edges[0].line))
        self.play(FadeOut(edges[0].line))
        del edges[0]
        group = VGroup(a_p.objects(), a_n.objects(),
                       b_p.objects(), b_n.objects(),
                       a.objects(), b.objects(), arr)
        self.wait(2)
        self.play(group.animate.shift(LEFT * 3.5))
        separator = Line(UP * 3.5, DOWN * 0.5)
        self.play(FadeIn(separator))
        x = RIGHT * 3.5
        a = deepcopy(a_n)
        b = deepcopy(b_n)
        ab_or = Text('or', fill_color=ORANGE).move_to(UP * 3 + x)
        self.play(
            a.objects().animate.move_to(UP * 3 + x + LEFT * 1),
            b.objects().animate.move_to(UP * 3 + x + RIGHT * 1),
            FadeIn(ab_or)
        )
        arrow = Arrow(UP * 2.7 + x, UP * 1.7 + x)
        self.play(FadeIn(arrow))
        a1 = deepcopy(a)
        b1 = deepcopy(b)
        a1b1 = Edge(a1, b1, Arrow)
        a1b1.add_updater(self)
        self.play(a1.name.animate.move_to(UP * 1.4 + x + LEFT * 0.7),
                  a1.circle.animate.move_to(UP * 1.4 + x + LEFT * 0.7)
                  .set_color(RED).set_stroke(RED_E),
                  b1.objects().animate.move_to(UP * 1.4 + x + RIGHT * 0.7),
                  FadeIn(a1b1.line)
                  )
        self.bring_to_front(a1.name)
        a2 = deepcopy(a)
        b2 = deepcopy(b)
        a2b2 = Edge(b2, a2, Arrow)
        a2b2_and = Text("and", fill_color=ORANGE).move_to(UP * 0.7 + x)
        a2b2.add_updater(self)
        self.play(b2.name.animate.move_to(x + RIGHT * 0.7),
                  b2.circle.animate.move_to(x + RIGHT * 0.7)
                  .set_color(RED).set_stroke(RED_E),
                  a2.objects().animate.move_to(x + LEFT * 0.7),
                  FadeIn(a2b2.line),
                  FadeInFromPoint(a2b2_and, a2b2_and.get_center())
                  )
        self.bring_to_front(b2.name)
        self.play(
            a1.objects().animate.move_to(statements[3][0].circle),
            a2.objects().animate.move_to(statements[3][1].circle),
            b1.objects().animate.move_to(statements[4][1].circle),
            b2.objects().animate.move_to(statements[4][0].circle),
        )
        self.play(FadeOut(a1.objects()),
                  FadeOut(a2.objects()),
                  FadeOut(b1.objects()),
                  FadeOut(b2.objects()))
        self.play(FadeOut(a.objects()),
                  FadeOut(b.objects()),
                  FadeOut(ab.line),
                  FadeOut(ab_or),
                  FadeOut(arrow),
                  FadeOut(group),
                  *[FadeOut(edge.line) for edge in edges],
                  FadeOut(separator),
                  FadeOut(a2b2_and))
        a1b1.start = statements[3][0]
        a1b1.end = statements[4][1]
        a2b2.start = statements[4][0]
        a2b2.end = statements[3][1]
        a1b1.add_updater(self)
        a2b2.add_updater(self)
        return a1b1, a2b2

    def transform_edges(self, edges, statements):
        result = []
        for edge in edges:
            a = self.get_index_of_statement(statements, edge.start)
            b = self.get_index_of_statement(statements, edge.end)
            if edge.start.color == edge.end.color:
                result += [Edge(statements[a][0], statements[b][1], Arrow),
                           Edge(statements[a][1], statements[b][0], Arrow),
                           Edge(statements[b][0], statements[a][1], Arrow),
                           Edge(statements[b][1], statements[a][0], Arrow)]
            else:
                a_eq, b_eq = 0, 0
                a_neq, b_neq = 1, 1
                if statements[a][1].color == statements[b][0].color:
                    a_eq, a_neq = a_neq, a_eq
                elif statements[a][0].color == statements[b][1].color:
                    b_eq, b_neq = b_neq, b_eq
                elif statements[a][1].color == statements[b][1].color:
                    a_eq, a_neq = a_neq, a_eq
                    b_eq, b_neq = b_neq, b_eq
                result += [
                    Edge(statements[a][a_eq], statements[b][b_neq], Arrow),
                    Edge(statements[b][b_eq], statements[a][a_neq], Arrow)
                ]
        return result

    def get_index_of_statement(self, statements, node):
        for idx, sts in enumerate(statements):
            if sts[0].name.text == node.name.text:
                return idx

    def show_strong_components(self):
        nodes: list[Node] = []
        anims = []
        for idx in range(10):
            target = Point(UP * 3.5).rotate_about_origin(idx * PI / 5)
            circle = Circle(fill_color=WHITE, stroke_color=GREY,
                            fill_opacity=0.5, radius=0.25).move_to(target)
            anims += [FadeInFromPoint(circle, circle.get_center() / 2)]
            nodes += [Node(circle)]
            nodes[-1].text_name = "ABCDEFGHIJ"[idx]
        self.play(*anims)
        edges_names = ['AC', 'AH', 'BA', 'BG', 'CD', 'DF', 'EA',
                       'EI', 'FJ', 'GI', 'HF', 'HG', 'IH', 'JC']
        edges = []
        anims = []
        for edge in edges_names:
            names = "ABCDEFGHIJ"
            start_idx = names.index(edge[0])
            end_idx = names.index(edge[1])
            edges += [Edge(nodes[start_idx], nodes[end_idx], Arrow)]
            anims += [FadeIn(edges[-1].line)]

        self.play(*anims)

        def dfs(index, tout):
            node = nodes[index]
            self.play(node.circle.animate.set_color(YELLOW)
                      .set_stroke(YELLOW_E), run_time=0.5)
            node.color = YELLOW
            node.stroke_color = YELLOW_E
            name = "ABCDEFGHIJ"[index]
            cur_edges = list(filter(lambda e: e[0] == name, edges_names))
            for cur_edge in cur_edges:
                end_index = "ABCDEFGHIJ".index(cur_edge[1])
                if nodes[end_index].color != YELLOW and \
                        nodes[end_index].name is None:
                    cur_edge_idx = 0
                    for idx, search_edge in enumerate(edges):
                        if search_edge.start == node and \
                                search_edge.end == nodes[end_index]:
                            self.play(search_edge.line.animate
                                      .set_stroke(YELLOW), run_time=0.5)
                            cur_edge_idx = idx
                            break
                    tout = dfs(end_index, tout)
                    self.play(edges[cur_edge_idx].line.animate
                              .set_stroke(WHITE), run_time=0.5)
            node.color = WHITE
            node.stroke_color = GREY
            text = Text(str(tout), height=0.3,
                        fill_color=BLACK).move_to(node.circle)
            node.name = text
            self.play(node.circle.animate.set_color(WHITE).set_stroke(GREY),
                      FadeIn(text), run_time=0.5)
            return tout + 1

        t = 0
        for cur_node in range(10):
            if nodes[cur_node].name is None:
                t = dfs(cur_node, t)
        anims = []
        for edge in edges:
            anims += [edge.revert_arrow()]
        self.play(*anims)

        nodes.sort(key=lambda n: n.name.text, reverse=True)

        def dfs2(index, color):
            node = nodes[index]
            self.play(node.circle.animate.set_color(color[0])
                      .set_stroke(color[1]), run_time=0.5)
            node.color = color[0]
            node.stroke_color = color[1]
            name = node.text_name
            cur_edges = list(filter(lambda e: e[1] == name, edges_names))
            for cur_edge in cur_edges:
                end_index = list(map(lambda n: n.text_name, nodes)) \
                    .index(cur_edge[0])
                if nodes[end_index].color == WHITE:
                    for search_edge in edges:
                        if search_edge.end == node and \
                                search_edge.start == nodes[end_index]:
                            self.play(search_edge.line.animate
                                      .set_stroke(color[0]), run_time=0.5)
                            break
                    dfs2(end_index, color)

        colors = [(TEAL, TEAL_E), (GOLD, GOLD_E),
                  (MAROON, MAROON_E), (PURPLE, PURPLE_E),
                  (YELLOW, YELLOW_E)]
        cur_col = 0
        for cur_node in range(10):
            if nodes[cur_node].color is WHITE:
                dfs2(cur_node, colors[cur_col])
                cur_col += 1

        anims = []
        for edge in edges:
            if edge.start.name.text == '3' and edge.end.name.text == '2':
                anims += [edge.line.animate.set_stroke(YELLOW)]
            elif edge.start.name.text == '6' and edge.end.name.text == '5':
                anims += [edge.line.animate.set_stroke(PURPLE)]
        self.play(*anims)

        self.play(*[edge.normalize_arrow() for edge in edges])
        [edge.add_updater(self) for edge in edges]
        nodes.sort(key=lambda n: n.text_name)

        anims = []
        target = Point(UP * 1.2)
        anims += [nodes[7].objects().animate.move_to(target)]
        target.rotate(2 * PI / 3, about_point=ORIGIN)
        anims += [nodes[8].objects().animate.move_to(target)]
        target.rotate(2 * PI / 3, about_point=ORIGIN)
        anims += [nodes[6].objects().animate.move_to(target)]

        self.play(
            nodes[1].objects().animate.move_to(UP * 3.5 + RIGHT * 1.7),
            nodes[4].objects().animate.move_to(UP * 3.5 + LEFT * 1.7),
            nodes[0].objects().animate.move_to(UP * 2.5),
            *anims,
            nodes[2].objects().animate.move_to(DOWN * 1.5 + LEFT),
            nodes[3].objects().animate.move_to(DOWN * 3.5 + LEFT),
            nodes[5].objects().animate.move_to(DOWN * 3.5 + RIGHT),
            nodes[9].objects().animate.move_to(DOWN * 1.5 + RIGHT),
        )
        group = VGroup(*[node.objects() for node in nodes])

        self.play(group.animate.shift(LEFT * 4))

        comp0 = nodes[4].circle.copy()
        comp1 = nodes[1].circle.copy()
        comp2 = nodes[0].circle.copy()
        comp3 = nodes[8].circle.copy()
        comp4 = nodes[9].circle.copy()
        comp0_arrow = Arrow(LEFT + UP * 1.4, UP * 1.4)
        comp1_arrow = Arrow(LEFT + UP * 0.7, UP * 0.7)
        comp2_arrow = Arrow(LEFT, ORIGIN)
        comp3_arrow = Arrow(LEFT + DOWN * 0.7, DOWN * 0.7)
        comp4_arrow = Arrow(LEFT + DOWN * 1.4, DOWN * 1.4)
        comp0_text = Text("0").move_to(RIGHT * 0.2 + UP * 1.4)
        comp1_text = Text("1").move_to(RIGHT * 0.2 + UP * 0.7)
        comp2_text = Text("2").move_to(RIGHT * 0.2)
        comp3_text = Text("3").move_to(RIGHT * 0.2 + DOWN * 0.7)
        comp4_text = Text("4").move_to(RIGHT * 0.2 + DOWN * 1.4)
        self.play(
            FadeIn(comp0_arrow), FadeIn(comp0_text),
            comp0.animate.move_to(LEFT * 1.3 + UP * 1.4),
            FadeIn(comp1_arrow), FadeIn(comp1_text),
            comp1.animate.move_to(LEFT * 1.3 + UP * 0.7),
            FadeIn(comp2_arrow), FadeIn(comp2_text),
            comp2.animate.move_to(LEFT * 1.3),
            FadeIn(comp3_arrow), FadeIn(comp3_text),
            comp3.animate.move_to(LEFT * 1.3 + DOWN * 0.7),
            FadeIn(comp4_arrow), FadeIn(comp4_text),
            comp4.animate.move_to(LEFT * 1.3 + DOWN * 1.4),
        )
        self.wait(2)
        first = nodes[1].objects().copy()
        second = nodes[9].objects().copy()
        f_s = Arrow(UP + RIGHT * 2.5, UP + RIGHT * 4.5)
        f_s.set_length(f_s.get_length() - 0.5)
        self.play(first.animate.move_to(UP + RIGHT * 2.5),
                  second.animate.move_to(UP + RIGHT * 4.5),
                  FadeIn(f_s))
        then = Arrow(UP * 0.5 + RIGHT * 3.5, DOWN * 0.5 + RIGHT * 3.5)
        comp_t = Tex(r'comp [\ \ \ \ ] \leq comp [\ \ \ \ ]') \
            .move_to(DOWN + RIGHT * 3.5)
        first_copy = first.copy()
        second_copy = second.copy()

        self.play(FadeInFromPoint(then, f_s.get_center()),
                  FadeIn(comp_t),
                  first_copy.animate.move_to(DOWN + RIGHT * 2.75),
                  second_copy.animate.move_to(DOWN + RIGHT * 5.39))
        group.add(comp0, comp0_text, comp0_arrow,
                  comp1, comp1_text, comp1_arrow,
                  comp2, comp2_text, comp2_arrow,
                  comp3, comp3_text, comp3_arrow,
                  comp4, comp4_text, comp4_arrow,
                  first, second, f_s, then,
                  first_copy, second_copy, comp_t)
        self.wait(2)
        return group

    def statements_components(self, statements, statements_group):
        self.on_components(statements, UP * 2.5)
        self.on_components(statements, 0)
        self.on_components(statements, UP * 2.5)
        self.play(statements_group.animate.shift(LEFT * 3 + DOWN).scale(0.65))
        nodes, text = self.component_to_graph(statements)
        edges = [Edge(nodes[0], nodes[1]), Edge(nodes[1], nodes[2]),
                 Edge(nodes[2], nodes[3]), Edge(nodes[3], nodes[4]),
                 Edge(nodes[0], nodes[4]), Edge(nodes[0], nodes[2]),
                 Edge(nodes[1], nodes[3]), Edge(nodes[1], nodes[4])]
        self.play(*[FadeInFromPoint(edge.line, edge.line.get_center())
                    for edge in edges])
        [edge.add_updater(self) for edge in edges]
        self.play(statements_group.animate.shift(LEFT * 8))
        self.paradox(text)
        group = VGroup(*[node.objects() for node in nodes])
        self.play(group.animate.shift(LEFT * 3.5).scale(1.25))
        self.play(*[edge.add_gradient() for edge in edges])
        self.wait(2)
        self.play(FadeOut(group),
                  *[FadeOut(edge.line) for edge in edges])

    def on_components(self, statements, radius):
        anims = []
        first_center = LEFT * 3
        second_center = RIGHT * 3
        target = Point(radius + first_center)
        anims += [statements[0][0].objects().animate.move_to(target)]
        target.rotate(2 * PI / 5, about_point=first_center)
        anims += [statements[1][1].objects().animate.move_to(target)]
        target.rotate(2 * PI / 5, about_point=first_center)
        anims += [statements[3][0].objects().animate.move_to(target)]
        target.rotate(2 * PI / 5, about_point=first_center)
        anims += [statements[4][1].objects().animate.move_to(target)]
        target.rotate(2 * PI / 5, about_point=first_center)
        anims += [statements[2][1].objects().animate.move_to(target)]
        target = Point(radius + second_center)
        anims += [statements[0][1].objects().animate.move_to(target)]
        target.rotate(2 * PI / 5, about_point=second_center)
        anims += [statements[2][0].objects().animate.move_to(target)]
        target.rotate(2 * PI / 5, about_point=second_center)
        anims += [statements[4][0].objects().animate.move_to(target)]
        target.rotate(2 * PI / 5, about_point=second_center)
        anims += [statements[3][1].objects().animate.move_to(target)]
        target.rotate(2 * PI / 5, about_point=second_center)
        anims += [statements[1][0].objects().animate.move_to(target)]
        self.play(*anims)

    def component_to_graph(self, statements):
        nodes = []
        comps = [r'<',
                 r'>',
                 r'>',
                 r'<',
                 r'>']
        comp_text = Tex(r'comp [\ \ \ \ ] \ \ \ \  comp [\ \ \ \ ]') \
            .move_to(LEFT * 3 + UP * 2.5)
        self.play(FadeIn(comp_text))
        center = RIGHT * 3.5
        target = Point(UP * 2.25 + center)
        for idx in range(5):
            first = statements[idx][0].circle.copy()
            second = statements[idx][1].circle.copy()
            comp_idx = Tex(comps[idx]).move_to(LEFT * 3 + UP * 2.5)
            first_name = Text('ABCDE'[idx], height=0.2).scale(0.65) \
                .move_to(first)
            second_name = first_name.copy().move_to(second)
            first_node = Node(first, name=first_name)
            second_node = Node(second, name=second_name)
            self.play(first_node.objects().animate.scale(20 / 13).move_to(
                LEFT * 3.75 + UP * 2.5),
                second_node.objects().animate.scale(20 / 13).move_to(
                    LEFT * 1.11 + UP * 2.5))
            self.play(FadeIn(comp_idx))
            if comps[idx] == r'<':
                self.play(second_node.objects().animate.move_to(target),
                          FadeOut(first_node.objects()))
                nodes += [second_node]
            else:
                self.play(first_node.objects().animate.move_to(target),
                          FadeOut(second_node.objects()))
                nodes += [first_node]
            self.play(FadeOut(comp_idx))
            target.rotate(2 * PI / 5, about_point=center)
        return nodes, comp_text

    def paradox(self, text):
        self.play(text.animate.shift(LEFT * 1.3))
        text2 = text.copy().shift(DOWN)
        a_c = Circle(radius=0.25, fill_color=RED,
                     stroke_color=RED_E, stroke_width=4,
                     fill_opacity=0.5) \
            .move_to(text.get_center() + LEFT * 0.75)
        a_t = Text('X', height=0.2).move_to(a_c.get_center())
        b_c = Circle(radius=0.25, fill_color=GREEN,
                     stroke_color=GREEN_E, stroke_width=4,
                     fill_opacity=0.5) \
            .move_to(text.get_center() + RIGHT * 1.89)
        b_t = Text('X', height=0.2).move_to(b_c.get_center())
        c_c = Circle(radius=0.25, fill_color=GREEN,
                     stroke_color=GREEN_E, stroke_width=4,
                     fill_opacity=0.5) \
            .move_to(text2.get_center() + LEFT * 0.75)
        c_t = Text('Y', height=0.2).move_to(c_c.get_center())
        d_c = Circle(radius=0.25, fill_color=BLUE,
                     stroke_color=BLUE_E, stroke_width=4,
                     fill_opacity=0.5) \
            .move_to(text2.get_center() + RIGHT * 1.89)
        d_t = Text('Y', height=0.2).move_to(d_c.get_center())
        a = Node(a_c, name=a_t)
        b = Node(b_c, name=b_t)
        c = Node(c_c, name=c_t)
        d = Node(d_c, name=d_t)
        self.play(*[FadeInFromPoint(it.objects(),
                                    it.objects().get_center() + DOWN * 0.5)
                    for it in (a, b)])
        ab_t = Tex(r'<').move_to(text)
        self.play(FadeIn(ab_t))

        a_arrow = Arrow(text.get_right(),
                        text.get_right() + RIGHT * 1.25)
        a_res = deepcopy(b)
        self.play(FadeInFromPoint(a_arrow, text.get_right()),
                  a_res.objects().animate
                  .move_to(text.get_right() + RIGHT * 1.5))

        self.play(FadeInFromPoint(text2, text.get_center()))
        self.play(*[FadeInFromPoint(it.objects(),
                                    it.objects().get_center() + DOWN * 0.5)
                    for it in (c, d)])
        cd_t = Tex(r'>').move_to(text2)
        self.play(FadeIn(cd_t))

        b_arrow = Arrow(text2.get_right(),
                        text2.get_right() + RIGHT * 1.25)
        b_res = deepcopy(c)
        self.play(FadeInFromPoint(b_arrow, text2.get_right()),
                  b_res.objects().animate
                  .move_to(text2.get_right() + RIGHT * 1.5))

        but_a = deepcopy(a_res)
        but_b = deepcopy(d)
        but_ab = Arrow(text2.get_center() + DOWN + LEFT*0.8,
                       text2.get_center() + DOWN + RIGHT*0.8)
        self.play(but_a.objects().animate.move_to(
            text2.get_center() + DOWN + LEFT),
            but_b.objects().animate.move_to(
                text2.get_center() + DOWN + RIGHT),
            FadeIn(but_ab)
        )
        self.wait(2)
        text3 = text2.copy().shift(DOWN * 2)
        but_a1 = deepcopy(but_a)
        but_b1 = deepcopy(but_b)
        but_ab1 = Tex(r'\leq').move_to(text3)
        self.play(FadeIn(text3), FadeIn(but_ab1),
                  but_a1.objects().animate.move_to(
                      text3.get_center() + LEFT * 0.75
                  ),
                  but_b1.objects().animate.move_to(
                      text3.get_center() + RIGHT * 1.89
                  ))
        self.wait(2)

        but_c = deepcopy(b_res)
        but_d = deepcopy(a)
        but_cd = Arrow(text3.get_center() + DOWN + LEFT*0.8,
                       text3.get_center() + DOWN + RIGHT*0.8)
        self.play(but_c.objects().animate.move_to(
            text3.get_center() + DOWN + LEFT),
            but_d.objects().animate.move_to(
                text3.get_center() + DOWN + RIGHT),
            FadeIn(but_cd)
        )
        text4 = text3.copy().shift(DOWN * 2)
        but_c1 = deepcopy(but_c)
        but_d1 = deepcopy(but_d)
        but_cd1 = Tex(r'\leq').move_to(text4)
        self.play(FadeIn(text4), FadeIn(but_cd1),
                  but_c1.objects().animate.move_to(
                      text4.get_center() + LEFT * 0.75
                  ),
                  but_d1.objects().animate.move_to(
                      text4.get_center() + RIGHT * 1.89
                  ))

        self.wait(2)

        self.play(
            FadeOut(a_res.objects()),
            FadeOut(a_arrow),
            FadeOut(b_res.objects()),
            FadeOut(b_arrow),
            FadeOut(but_a.objects()),
            FadeOut(but_b.objects()),
            FadeOut(but_ab),
            FadeOut(text3),
            FadeOut(but_a1.objects()),
            FadeOut(but_b1.objects()),
            FadeOut(but_c.objects()),
            FadeOut(but_d.objects()),
            FadeOut(but_cd),
            FadeOut(text4),
            FadeOut(but_c1.objects()),
            FadeOut(but_d1.objects()),
            text.animate.move_to(LEFT*3.5 + UP*0.5),
            text2.animate.move_to(LEFT*3.5 + DOWN*0.5),
            ab_t.animate.move_to(LEFT*3.5 + UP*0.5),
            cd_t.animate.move_to(LEFT*3.5 + DOWN*0.5),
            a.objects().animate.move_to(LEFT*(3.5 + 0.75) + UP*0.5),
            c.objects().animate.move_to(LEFT*(3.5 + 0.75) + DOWN*0.5),
            b.objects().animate.move_to(LEFT*(3.5 - 1.89) + UP*0.5),
            d.objects().animate.move_to(LEFT*(3.5 - 1.89) + DOWN*0.5),
            but_ab1.animate.rotate(-PI / 2).move_to(LEFT*(3.5 + 1.5)),
            but_cd1.animate.rotate(PI / 2).move_to(LEFT*(3.5 - 1))
        )
        self.wait(2)
        self.play(FadeOut(text),
                  FadeOut(text2),
                  FadeOut(ab_t),
                  FadeOut(cd_t),
                  FadeOut(a.objects()),
                  FadeOut(b.objects()),
                  FadeOut(c.objects()),
                  FadeOut(d.objects()),
                  FadeOut(but_ab1),
                  FadeOut(but_cd1))

    def thanks(self):
        corona = ImageMobject("media/images/3B1B_Logo.svg.png")
        corona.scale(1.2)

        self.play(FadeIn(corona))
