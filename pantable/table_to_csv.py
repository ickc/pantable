import csv
import io

import panflute
import yaml

from .const import ALIGN_TO_LETTER
from .util import ast_to_markdown


def table_to_csv(elem, doc):
    """convert Table element and to csv table in code-block with class "table" in panflute AST"""
    if isinstance(elem, panflute.Table):
        # get options as a dictionary
        options = {}
        # options: caption: panflute ast to markdown
        if elem.caption:
            options['caption'] = ast_to_markdown(panflute.Para(*elem.caption))
        # options: alignment
        parsed_alignment = [ALIGN_TO_LETTER[i] for i in elem.alignment]
        options['alignment'] = "".join(parsed_alignment)
        # options: width
        options['width'] = elem.width
        # options: table-width from width
        options['table-width'] = sum(options['width'])
        # options: header: False if empty header row, else True
        options['header'] = bool(panflute.stringify(elem.header)) if elem.header else False
        # options: markdown
        options['markdown'] = True

        # option in YAML
        yaml_metadata = yaml.safe_dump(options)

        # table in panflute AST
        table_body = elem.content
        if options['header']:
            table_body.insert(0, elem.header)
        # table in list
        table_list = [[ast_to_markdown(cell.content)
                       for cell in row.content]
                      for row in table_body]
        # table in CSV
        with io.StringIO() as file:
            writer = csv.writer(file)
            writer.writerows(table_list)
            csv_table = file.getvalue()
        code_block = f"""---
{yaml_metadata}---
{csv_table}"""
        return panflute.CodeBlock(code_block, classes=["table"])
    return None
