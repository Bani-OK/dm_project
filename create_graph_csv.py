import signal
import time

import pandas as pd
import random

import checker
import program


def create_graph(n, m):
    graph_data = []
    colors = ["red", "green", "blue"]
    vertex_color = [random.choice(colors) for _ in range(n + 1)]
    good = []
    for i in range(n + 1):
        a = ["red", "green", "blue"]
        a.remove(vertex_color[i])
        good.append(random.choice(a))
    green = good.count("green")
    red = good.count("red")
    blue = good.count("blue")
    m = min(m, red * green + red * blue + green * blue)
    number_of_edges = 0
    while number_of_edges < m:
        v1 = random.randint(1, n)
        v2 = random.randint(1, n)

        if v1 == v2:
            continue
        if [v1, v2, vertex_color[v1], vertex_color[v2]] in graph_data or \
                [v2, v1, vertex_color[v2], vertex_color[v1]] in graph_data:
            continue
        if good[v1] == good[v2]:
            continue
        number_of_edges += 1

        graph_data.append([v1, v2, vertex_color[v1], vertex_color[v2]])

    df = pd.DataFrame(graph_data,
                      columns=['vertex1', 'vertex2', 'color1', 'color2'])
    df.to_csv("graph.csv", index=False)
    with open('reserve.txt', 'w') as out:
        for idx, val in enumerate(good):
            out.write(f'{idx} -> {val}\n')


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True


if __name__ == "__main__":
    # n = int(input("Enter the number of vertices in a graph: "))
    start = time.perf_counter()
    count = 0
    killer = GracefulKiller()
    try:
        while not killer.kill_now:
            count += 1
            n = random.randint(1, 1000)
            m = random.randint(0, min(n * (n - 1) // 2, 20000))
            create_graph(n, m)
            output = program.main()
            if output:
                print(output)
                break
            checker_output = checker.main()
            if checker_output is not None:
                print(checker_output)
                break
    except:
        pass
    finally:
        print(count)
