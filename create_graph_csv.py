import signal
import time

import pandas as pd
import random

import checker
import program


def add_edges(first_comp, second_comp, graph_data, vertex_color):
    for v in first_comp:
        for u in second_comp:
            should_add = random.randint(0, 1)
            if should_add:
                graph_data.append([v, u, vertex_color[v], vertex_color[u]])


def create_graph(n):
    graph_data = []
    colors = ["red", "green", "blue"]
    vertex_color = [random.choice(colors) for _ in range(n + 1)]
    green = []
    red = []
    blue = []
    for i in range(1, n + 1):
        if vertex_color[i] == "green":
            a = random.choice([red, blue])
            a.append(i)
        elif vertex_color[i] == "blue":
            a = random.choice([red, green])
            a.append(i)
        else:
            a = random.choice([green, blue])
            a.append(i)

    add_edges(green, blue, graph_data, vertex_color)
    add_edges(green, red, graph_data, vertex_color)
    add_edges(red, blue, graph_data, vertex_color)

    df = pd.DataFrame(graph_data,
                      columns=['vertex1', 'vertex2', 'color1', 'color2'])
    df.to_csv("graph.csv", index=False)
    with open('reserve.txt', 'w') as out:
        array = []
        for a in red:
            array.append((a, f'{a} -> red\n'))
        for a in green:
            array.append((a, f'{a} -> green\n'))
        for a in blue:
            array.append((a, f'{a} -> blue\n'))
        out.write(''.join(map(lambda m: m[1],
                              sorted(array, key=lambda m: m[0]))))

    return len(graph_data)


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True


if __name__ == "__main__":
    # n = int(input("Enter the number of vertices in a graph: "))
    max_working_time = 0
    edge_amount = -1
    count = 0
    killer = GracefulKiller()
    try:
        while not killer.kill_now:
            count += 1
            n = random.randint(1, 1000)
            m = create_graph(n)
            a = time.perf_counter()
            output = program.main()
            b = time.perf_counter()
            if b - a > max_working_time:
                max_working_time = b - a
                edge_amount = m
            if output:
                print(output)
                break
            checker_output = checker.main()
            if checker_output is not None:
                print(checker_output)
                break
    finally:
        print(f'{edge_amount} -> {max_working_time}')
        print(count)
