import pandas as pd


class Statement:
    node_name: str
    node_color: str
    target_color: str

    opposite = None

    out_edges: list
    in_edges: list

    tout: int = None
    component: int = None

    def __init__(self, node_name: str, target_color: str, node_color: str):
        self.target_color = target_color
        self.node_name = node_name
        self.node_color = node_color
        self.out_edges = []
        self.in_edges = []


def main():
    statements = []
    node_names = {}

    for name1, name2, color1, color2 in read_file("graph.csv"):
        add_node_if_new(name1, color1, node_names, statements)
        add_node_if_new(name2, color2, node_names, statements)
        set_statements_links(name1, name2, node_names)

    fill_out_times(statements)
    statements.sort(key=lambda x: x.tout, reverse=True)
    setup_components(statements)
    select_colors(statements)

    write_to_file(node_names)


def read_file(path: str):
    df: pd.DataFrame = pd.read_csv(path, header=0)
    for idx, row in df.iterrows():
        yield row['vertex1'], row['vertex2'], row['color1'], row['color2']


def add_node_if_new(name: str, color: str, node_names: dict, statements: list):
    if name not in node_names:
        possible_colors: list = ["red", "green", "blue"]
        possible_colors.remove(color)

        positive = Statement(name, possible_colors[0], color)
        negative = Statement(name, possible_colors[1], color)

        negative.opposite = positive
        positive.opposite = negative

        statements.append(positive)
        statements.append(negative)

        node_names[name] = positive


def set_statements_links(name1: str, name2: str, node_names: dict):
    first_p: Statement = node_names[name1]
    first_n: Statement = node_names[name1].opposite
    second_p: Statement = node_names[name2]
    second_n: Statement = node_names[name2].opposite
    current_statements = [first_p, first_n, second_p, second_n]

    if first_p.node_color == second_p.node_color:
        set_equal_colors(current_statements)
    else:
        set_different_colors(current_statements)


def set_equal_colors(current_statements: list):
    first_color = current_statements[0].target_color
    first_color_statements = []
    second_color_statements = []
    for statement in current_statements:
        if statement.target_color == first_color:
            first_color_statements.append(statement)
        else:
            second_color_statements.append(statement)

    add_link(first_color_statements[0], first_color_statements[1])
    add_link(second_color_statements[0], second_color_statements[1])


def set_different_colors(current_statements: list):
    current_statements.sort(key=lambda x: x.target_color)

    for idx in range(1, 4):
        if current_statements[idx].target_color == \
                current_statements[idx - 1].target_color:
            del current_statements[idx - 1:idx + 1]
            break

    add_link(current_statements[0], current_statements[1])


def add_link(st_a: Statement, st_b: Statement):
    add_edge(st_a.opposite, st_b)
    add_edge(st_b.opposite, st_a)


def add_edge(st_a: Statement, st_b: Statement):
    st_a.out_edges.append(st_b)
    st_b.in_edges.append(st_a)


def fill_out_times(statements: list):
    cur_time = 0
    for val in statements:
        if val.tout is None:
            cur_time = fill_out_times_from_node(val, cur_time)


def fill_out_times_from_node(node: Statement, time: int) -> int:
    node.tout = -1
    stack: list = [node]
    while stack:
        cur_node = stack[-1]

        for next_cur_node in cur_node.out_edges:
            if next_cur_node.tout is None:
                next_cur_node.tout = -1
                stack.append(next_cur_node)
                break

        if stack[-1] == cur_node:
            cur_node.tout = time
            time += 1
            del stack[-1]
    return time


def setup_components(statements: list):
    cur_component = 0
    for val in statements:
        if val.component is None:
            paint_graph(val, cur_component)
            cur_component += 1


def paint_graph(node: Statement, component_number: int):
    stack: list = [node]

    while stack:
        cur_node: Statement = stack.pop()
        cur_node.component = component_number

        for next_node in cur_node.in_edges:
            if next_node.component is None:
                stack.append(next_node)


def select_colors(statements: list):
    for val in statements:
        if val.component == val.opposite.component:
            print("It is impossible to color this graph")
            return
        if val.component > val.opposite.component:
            val.mode_color = val.target_color
            val.opposite.mode_color = val.target_color


def write_to_file(node_names: dict):
    with open("output_file.txt", 'w', encoding='utf-8') as output:
        for name, node in node_names.items():
            output.write(f'{name} -> {node.node_color}\n')
