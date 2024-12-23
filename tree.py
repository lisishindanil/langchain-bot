import os


def generate_tree(directory, prefix=""):
    tree_structure = []
    items = sorted(os.listdir(directory))
    ignore = {"__pycache__", ".git"}

    for index, item in enumerate(items):
        if item in ignore:
            continue
        path = os.path.join(directory, item)
        connector = "├── " if index < len(items) - 1 else "└── "

        tree_structure.append(f"{prefix}{connector}{item}")

        if os.path.isdir(path):
            extension = "│   " if index < len(items) - 1 else "    "
            tree_structure.extend(generate_tree(path, prefix + extension))

    return tree_structure


def save_tree_to_markdown(directory, output_file="project_tree.md"):
    tree_structure = generate_tree(directory)
    with open(output_file, "w") as f:
        f.write("# Project Structure\n\n")
        f.write("```\n")
        f.write("\n".join(tree_structure))
        f.write("\n```\n")
    print(f"Project tree saved to {output_file}")


project_directory = "./"
save_tree_to_markdown(project_directory)
