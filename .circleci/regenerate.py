#!/usr/bin/env python3

from copy import deepcopy
import os.path

import jinja2
import yaml
from jinja2 import select_autoescape


PYTHON_VERSIONS = ["3.7", "3.8", "3.9", "3.10"]

RC_PATTERN = r"/v[0-9]+(\.[0-9]+)*-rc[0-9]+/"


def indent(indentation, data_list):
    return ("\n" + " " * indentation).join(
        yaml.dump(data_list, default_flow_style=False).splitlines()
    )


def jobs(pr_or_master, num_workers=20, indentation=2):
    w = {}
    needs_gpu_nvidia_small_multi = [3, 9, 12, 13]
    needs_gpu_nvidia_medium = [14, 15]
    w[f"pytorch_tutorial_{pr_or_master}_build_manager"] = {
        "<<": "*pytorch_tutorial_build_manager_defaults"
    }
    for i in range(num_workers):
        d = {"<<": "*pytorch_tutorial_build_worker_defaults"}
        if i in needs_gpu_nvidia_small_multi:
            d["resource_class"] = "gpu.nvidia.small.multi"
        if i in needs_gpu_nvidia_medium:
            d["resource_class"] = "gpu.nvidia.medium"
        w[f"pytorch_tutorial_{pr_or_master}_build_worker_{i:02d}"] = d

    return indent(indentation, w).replace("'", "")


def workflows_jobs(pr_or_master, indentation=6):
    w = []
    d = {"filters": {"branches": {"ignore" if pr_or_master == "pr" else "only": ["master"]}}}
    if pr_or_master == "master":
        d["context"] = "org-member"

    for i in range(20):
        w.append({f"pytorch_tutorial_{pr_or_master}_build_worker_{i:02d}": deepcopy(d)})
    w.append({f"pytorch_tutorial_{pr_or_master}_build_manager": deepcopy(d)})
    return indent(indentation, w)


if __name__ == "__main__":

    d = os.path.dirname(__file__)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(d),
        lstrip_blocks=True,
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        keep_trailing_newline=True,
    )
    with open(os.path.join(d, "config.yml"), "w") as f:
        f.write(
            env.get_template("config.yml.in").render(
                jobs=jobs, workflows_jobs=workflows_jobs
            )
        )
