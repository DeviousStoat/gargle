"""Sets the same docstrings on several classes with the same methods."""

import ast
import typing as t

# File name to the list of classes' names that need to have the same doctrings
# in their methods.
# The first class in the list should be the one with the written docstrings.
TO_UNIFORMIZE = {
    "gargle/maybe.py": ("Some", "Nothing"),
    "gargle/result.py": ("Ok", "Err"),
}


class ClassModifier(ast.NodeTransformer):
    def __init__(
        self, class_with_docstrings: ast.ClassDef, *args: t.Any, **kwargs: t.Any
    ) -> None:
        self._class_with_docstrings = class_with_docstrings
        super().__init__(*args, **kwargs)

    def function_with_docstring(self, function_name: str) -> ast.FunctionDef:
        for child_node in ast.walk(self._class_with_docstrings):
            if (
                isinstance(child_node, ast.FunctionDef)
                and child_node.name == function_name
            ):
                return child_node

        raise RuntimeError(
            f"Could not find function {function_name}"
            f" in class {self._class_with_docstrings.name}"
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        with_docstring = self.function_with_docstring(node.name)
        if not (docstring_content := ast.get_docstring(with_docstring, clean=False)):
            return node

        docstring = ast.Expr(value=ast.Str(s=docstring_content))

        current_docstring = ast.get_docstring(node, clean=False)
        if current_docstring:
            node.body[0] = docstring
        else:
            node.body.insert(0, docstring)

        return node


class DocstringAdder(ast.NodeTransformer):
    def __init__(
        self,
        class_name: str,
        class_modifier: ClassModifier,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        self._class_name = class_name
        self._class_modifier = class_modifier
        super().__init__(*args, **kwargs)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if not node.name == self._class_name:
            return node
        return self._class_modifier.visit(node)


def find_class_def_by_name(
    node: ast.Module, class_name: str, file: str
) -> ast.ClassDef:
    for child_node in ast.walk(node):
        if isinstance(child_node, ast.ClassDef) and child_node.name == class_name:
            return child_node

    raise RuntimeError(f"Could not find class {class_name} in file {file}")


def main() -> None:
    for file, classes in TO_UNIFORMIZE.items():
        with open(file) as f:
            tree = ast.parse(f.read())

        class_with_docstrings = find_class_def_by_name(tree, classes[0], file)

        class_modifier = ClassModifier(class_with_docstrings)
        for class_name in classes[1:]:
            tree = ast.fix_missing_locations(
                DocstringAdder(class_name, class_modifier).visit(tree)
            )

        with open(file, "w") as f:
            f.write(ast.unparse(tree))


if __name__ == "__main__":
    main()
