# HTML Table Takeout

[![Test](https://github.com/lawcal/html-table-takeout/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/lawcal/html-table-takeout/actions/workflows/test.yml)

<img src="images/html_table_takeout_logo.png" alt="HTML Table Takeout project logo" width="300">

A fast, lightweight HTML table parser that supports rowspan, colspan, links and nested tables. No external dependencies are needed.

The input may be text, a URL or local file `Path`.

<sup><sub>HTML5 logo by <a href='https://www.w3.org/'>W3C</a>.</sub></sup>

## Quick Start

Install the package:
```
pip install html-table-takeout
```

Pass in a URL and print out the parsed `Table` as CSV:
```
from html_table_takeout import parse_html

# start with http:// or https:// to source from a URL
tables = parse_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')

print(tables[0].to_csv())

# output:
# Symbol,Security,GICS Sector,GICS Sub-Industry,Headquarters Location,Date added,CIK,Founded
# MMM,3M,Industrials,Industrial Conglomerates,"Saint Paul, Minnesota",1957-03-04,0000066740,1902
# ...
```

Pass in HTML text and print out the parsed `Table` as valid HTML:
```
from html_table_takeout import parse_html

tables = parse_html("""
<table>
    <tr>
        <td rowspan='2'>1</td> <!-- rowspan will be expanded -->
        <td>2</td>
    </tr>
    <tr>
        <td>3</td>
    </tr>
</table>""")

print(tables[0].to_html(indent=4))

# output:
# <table data-table-id='0'>
# <tbody>
#     <tr>
#         <td>1</td>
#         <td>2</td>
#     </tr>
#     <tr>
#         <td>1</td>
#         <td>3</td>
#     </tr>
# </tbody>
# </table>
```

## Usage

The core `parse_html()` function returns a list of zero or more top-level `Table`. A `Table` is guaranteed to have this structure:
- **rows**: List of one or more `TRow`
  - **cells**: List of zero or more `TCell` resulting from rowspan and colspan expansion
    - **elements**: List of zero or more `TText`, `TLink`, `TBreak`, `TRef`

| Type     | Description                                      |
| -------- | ------------------------------------------------ |
| `Table`  | Each parsed table has an auto-assigned unique id |
| `TRow`   | Equal to each `<tr>` in the original table       |
| `TCell`  | Expanded `<td>` or `<th>` cells from row/colspan |
| `TText`  | HTML-decoded text inside `<td>` or `<th>`        |
| `TLink`  | Equal to each `<a>` inside `<td>` or `<th>`      |
| `TBreak` | Equal to `<br/>`                                 |
| `TRef`   | Reference to the child `Table`                   |

All tables are guaranteed to have at least one `TRow` containing one `TCell`.

The `parse_html()` function also provides filtering by text or attributes to target the tables you want. Check out its docstring for all options.

## Why did you make this

Most HTML table parsers require extra DOM and data processing libraries that aren't needed for my application. I need a parser that handles nesting and gives me the flexibility to process the parsed result however I want.

Now you too can take out tables to go.

## Developing

Install development dependencies:
```
pip install build mypy pytest
```

Run tests:
```
pytest
```

Build the package:
```
python -m build
```
