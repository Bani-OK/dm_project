import re


def main():
    colors = {}
    with open("output_file.txt", 'r') as file:
        for line in file:
            node, color = re.findall(r'^(\d+) -> (\w+)', line)[0]
            colors[node] = color
    with open("graph.csv", 'r') as file:
        for line in file:
            if line == 'vertex1,vertex2,color1,color2\n' or line == '':continue
            node1, node2, color1, color2 = \
                re.findall(r'^([^,]+?),([^,]+?),([^,]+?),([^,]+?)', line)[0]
            if colors[node1] == color1 or \
                colors[node2] == color2 or \
                colors[node1] == colors[node2]:
                return f'NOOOO: {line}'
