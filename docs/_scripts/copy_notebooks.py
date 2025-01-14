import os
import shutil
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]

examples_dir = root_dir / "examples"
docs_dir = root_dir / "docs/docs"
how_tos_dir = docs_dir / "how-tos"
tutorials_dir = docs_dir / "tutorials"

_MANUAL = {
    "how-tos": [
        "async.ipynb",
        "streaming-tokens.ipynb",
        "human-in-the-loop.ipynb",
        "persistence.ipynb",
        "time-travel.ipynb",
        "visualization.ipynb",
        "state-model.ipynb",
        "subgraph.ipynb",
        "persistence_postgres.ipynb",
        "branching.ipynb",
    ],
    "tutorials": [
        "chat_agent_executor_with_function_calling/base.ipynb",
        "chat_agent_executor_with_function_calling/high-level.ipynb",
        "chat_agent_executor_with_function_calling/high-level-tools.ipynb",
        "chat_agent_executor_with_function_calling/prebuilt-tool-node.ipynb",
        "agent_executor/base.ipynb",
        "agent_executor/high-level.ipynb",
    ],
}
_MANUAL_INVERSE = {v: docs_dir / k for k, vs in _MANUAL.items() for v in vs}
_HOW_TOS = {"agent_executor", "chat_agent_executor_with_function_calling", "docs"}
_MAP = {
    "persistence_postgres.ipynb": "tutorial",
}
_IGNORE = (".ipynb_checkpoints", ".venv", ".cache")


def clean_notebooks():
    roots = (how_tos_dir, tutorials_dir)
    for dir_ in roots:
        traversed = []
        for root, dirs, files in os.walk(dir_):
            for file in files:
                if file.endswith(".ipynb"):
                    os.remove(os.path.join(root, file))
            # Now delete the dir if it is empty now
            if root not in roots:
                traversed.append(root)

        for root in reversed(traversed):
            if not os.listdir(root):
                os.rmdir(root)


def copy_notebooks():
    # Nested ones are mostly tutorials rn
    for root, dirs, files in os.walk(examples_dir):
        if any(
            path.startswith(".") or path.startswith("__") for path in root.split(os.sep)
        ):
            continue
        if any(path in _HOW_TOS for path in root.split(os.sep)):
            dst_dir = how_tos_dir
        else:
            dst_dir = tutorials_dir
        for file in files:
            dst_dir_ = dst_dir
            if file.endswith((".ipynb", ".png")):
                if file in _MAP:
                    dst_dir = os.path.join(dst_dir, _MAP[file])
                src_path = os.path.join(root, file)
                dst_path = os.path.join(
                    dst_dir, os.path.relpath(src_path, examples_dir)
                )
                for k in _MANUAL_INVERSE:
                    if src_path.endswith(k):
                        overridden_dir = _MANUAL_INVERSE[k]
                        dst_path = os.path.join(overridden_dir, os.path.relpath(src_path, examples_dir))
                        print(f"Overriding {src_path} to {dst_path}")
                        break

                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy(src_path, dst_path)
                # Convert all ./img/* to ../img/*
                if file.endswith(".ipynb"):
                    with open(dst_path, "r") as f:
                        content = f.read()
                    content = content.replace("(./img/", "(../img/")
                    with open(dst_path, "w") as f:
                        f.write(content)
                dst_dir = dst_dir_
    # Top level notebooks are "how-to's"
    # for file in examples_dir.iterdir():
    #     if file.suffix.endswith(".ipynb") and not os.path.isdir(
    #         os.path.join(examples_dir, file)
    #     ):
    #         src_path = os.path.join(examples_dir, file)
    #         dst_path = os.path.join(docs_dir, "how-tos", file.name)
    #         shutil.copy(src_path, dst_path)


if __name__ == "__main__":
    clean_notebooks()
    copy_notebooks()
