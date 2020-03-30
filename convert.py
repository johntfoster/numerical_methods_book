#!/usr/bin/env python
"""convert.py
Usage:
  convert.py <files_to_convert.txt> 
  convert.py --daytum <files_to_convert.txt> 
  convert.py --dir=<output_file_path> <files_to_convert.txt> 

Options:
  -h --help                Show this screen.
  -v --version             Show version.
  --daytum                 Set options to convert into Daytum format.
  -d <path>, --dir=<path>  Output directory [default: ./]
"""
import nbformat
import nbconvert
import sys
import os
import shutil
import json

from docopt import docopt

from traitlets.config import Config


def add_rise_options(body, daytum=False):

    notebook_json = json.loads(body)
    notebook_metadata = notebook_json.get("metadata", {})

    if "livereveal" in notebook_metadata:
        rise_options = notebook_metadata["livereveal"]
        del notebook_metadata["livereveal"]
    else:
        defaults = {
            "footer": "",
            "progress": True,
            "scroll": True,
            "theme": "simple",
            "slideNumber": False,
            "auto_select": None,
            "enable_chalkboard": False,
            "controls": True,
        }
        rise_options = notebook_metadata.get("rise", defaults)

    if daytum:
        rise_options[
            "footer"
        ] = "<img src='https://github.com/daytum/logos/blob/master/daytum_logo_2019.png?raw=true' width='220'>"

    notebook_metadata["rise"] = rise_options

    return json.dumps(notebook_json)


def export_with_options(notebook_template, config, output_path=".", daytum=False):

    with open(notebook_template) as nb_file:
        nb_contents = nb_file.read()

    # Convert using the ordinary exporter
    notebook = nbformat.reads(nb_contents, as_version=4)
    exporter = nbconvert.NotebookExporter(config=config)

    body, res = exporter.from_notebook_node(notebook)

    body = add_rise_options(body, daytum)

    output_file_name = "{}.ipynb".format(notebook_template.split(".tpl.ipynb")[0])
    with open(os.path.join(output_path, output_file_name), "w") as output_file:
        output_file.write(body)


if __name__ == "__main__":

    args = docopt(__doc__, version="0.1")

    c = Config()
    c.TemplateExporter.exclude_input_prompt = True
    c.TemplateExporter.exclude_output_prompt = True
    c.TagRemovePreprocessor.enabled = True
    if args["--daytum"]:
        c.TagRemovePreprocessor.remove_cell_tags = set(["no_daytum"])
    else:
        c.TagRemovePreprocessor.remove_cell_tags = set(["daytum"])

    file_list = [line.rstrip("\n") for line in open(args["<files_to_convert.txt>"])]

    for filename in file_list:
        if filename.split(".")[-2] == "tpl":
            export_with_options(
                filename, config=c, output_path=args["--dir"], daytum=args["--daytum"]
            )
        elif not (args["--daytum"] and "datasets" in filename):
            shutil.copyfile(filename, os.path.join(args["--dir"], filename))
