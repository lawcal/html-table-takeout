# pylint: disable=too-many-lines
from pathlib import Path
import re
import pytest

from html_table_takeout import Table, TRow, TCell, TLink, TRef, TBreak, TText, parse_html


#########################################################
# test helpers
#########################################################


def create_table_html_with_rowspan(num_rows: int) -> str:
    num_rows = max(1, num_rows)
    table_content = ''
    for r in range(num_rows):
        row_content = f"<td rowspan='{num_rows}'>0</td>" if r <= 0 else ''
        table_content += f"<tr>{row_content}</tr>"
    return f"<table>{table_content}</table>"


def create_table(num_rows: int, num_cols: int) -> Table:
    num_rows = max(1, num_rows)
    num_cols = max(1, num_cols)
    table = Table(id=0)
    for _ in range(num_rows):
        table.rows.append(TRow())
        for _ in range(num_cols):
            cell = TCell()
            cell.elements.append(TText(text='0'))
            table.rows[-1].cells.append(cell)
    return table


def append_blank_rows(table: Table, num_rows: int) -> Table:
    num_rows = max(1, num_rows)
    for _ in range(num_rows):
        table.rows.append(TRow())
    return table


#########################################################
# structure
#########################################################


@pytest.mark.parametrize(
    '_desc,html_text,expected',
    [
        ('it returns empty list when no table', '<tr></tr>',
        []),
        ('it parses table with one cell', '<table><tr><td>1</td></tr></table>',
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
        ]),
        ('it parses multiple tables if multiple found', """
<table><tr><td>1</td></tr></table><table><tr><td>2</td></tr></table>
         """,
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
            Table(id=1, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
            ]),
        ]),
        ('it parses line breaks', """
<table>
    <tr>
        <td>1<br/></td>
        <td>2</td>
    </tr>
    <tr>
        <td><br>3</td>
        <td>4</td>
    </tr>
</table>
         """,
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                        TBreak(),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TBreak(),
                        TText(text='3'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='4'),
                    ]),
                ]),
            ]),
        ]),
        ('it parses a table without explicit row groups', """
<table>
    <tr>
        <td>1</td>
        <td>2</td>
    </tr>
    <tr>
        <td>3</td>
        <td>4</td>
    </tr>
</table>
         """,
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='3'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='4'),
                    ]),
                ]),
            ]),
        ]),
        ('it sets thead, tbody, tfoot for rows and header for cells', """
<table>
<thead>
    <tr>
        <th>1</th>
        <td>2</td>
    </tr>
    <tr>
        <td>3</td>
        <th>4</th>
    </tr>
</thead>
<tbody>
    <tr>
        <td>5</td>
        <th>6</th>
    </tr>
    <tr>
        <th>7</th>
        <td>8</td>
    </tr>
</tbody>
<tfoot>
    <tr>
        <th>9</th>
        <th>10</th>
    </tr>
    <tr>
        <td>11</td>
        <td>12</td>
    </tr>
</tfoot>
</table>
         """,
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=True, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='3'),
                    ]),
                    TCell(header=True, elements=[
                        TText(text='4'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='5'),
                    ]),
                    TCell(header=True, elements=[
                        TText(text='6'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=True, elements=[
                        TText(text='7'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='8'),
                    ]),
                ]),
                TRow(group='tfoot', cells=[
                    TCell(header=True, elements=[
                        TText(text='9'),
                    ]),
                    TCell(header=True, elements=[
                        TText(text='10'),
                    ]),
                ]),
                TRow(group='tfoot', cells=[
                    TCell(header=False, elements=[
                        TText(text='11'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='12'),
                    ]),
                ]),
            ]),
        ]),
        # because of unclosed tags, indents or spaces will be part of the raw text so don't indent
        ('it handles unclosed tags', """
<table>
<tr>
<td>1
<td>2
<tr>
<td>3
<td>4
</table>
         """,
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2\n'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='3\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='4\n'),
                    ]),
                ]),
            ]),
        ]),
        # because of unclosed tags, indents or spaces will be part of the raw text so don't indent
        ('it handles unclosed tags for row groups', """
<table>
<thead>
<tr>
<td>1
<td>2
<tbody>
<tr>
<td>3
<td>4
<tfoot>
<tr>
<td>5
<td>6
</table>
         """,
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='1\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2\n'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='3\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='4\n'),
                    ]),
                ]),
                TRow(group='tfoot', cells=[
                    TCell(header=False, elements=[
                        TText(text='5\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='6\n'),
                    ]),
                ]),
            ]),
        ]),
    ]
)
def test_structure(_desc, html_text, expected):
    actual = parse_html(html_text)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


def test_structure_nested():
    html_text = """
<table>
    <tr>
        <td>1<table>
            <tr>
                <td>2<table>
                    <tr>
                        <td><br/>3<br/><br/>4</td>
                        <td>5<br/><br/>6<br/></td>
                    </tr>
                    <tr>
                        <td>7</td>
                        <td>8</td>
                    </tr>
                </table></td>
            </tr>
        </table></td>
        <td>9</td>
    </tr>
    <tr>
        <td>0</td>
    </tr>
</table>"""
    table_one = Table(id=0, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TBreak(),
                TText(text='3'),
                TBreak(),
                TBreak(),
                TText(text='4'),
            ]),
            TCell(header=False, elements=[
                TText(text='5'),
                TBreak(),
                TBreak(),
                TText(text='6'),
                TBreak(),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='7'),
            ]),
            TCell(header=False, elements=[
                TText(text='8'),
            ]),
        ]),
    ])
    table_two = Table(id=1, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='2'),
                TRef(table=table_one),
            ]),
        ]),
    ])
    table_three = Table(id=2, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='1'),
                TRef(table=table_two),
            ]),
            TCell(header=False, elements=[
                TText(text='9'),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='0'),
            ]),
        ]),
    ])
    expected = [table_three]

    actual = parse_html(html_text)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


#########################################################
# rowspan/colspan
#########################################################


@pytest.mark.parametrize(
    '_desc,html_text,expected',
    [
        ('it expands cells according to rowspan and colspan', """
<<table>
    <tr>
         <td rowspan='2' colspan='2'>1</td>
         <td>2</td>
    </tr>
    <tr>
         <td rowspan='2'>3</td>
    </tr>
    <tr>
         <td>4</td>
         <td>5</td>
    </tr>
</table>
        """,
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='3'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='4'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='5'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='3'),
                    ]),
                ]),
            ]),
        ]),
        ('it handles rowspan and colspan that covers the whole table', """
<<table>
    <tr>
         <td rowspan='2' colspan='2'>1</td>
    </tr>
    <tr></tr>
</table>
        """,
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
        ]),
        ('it creates only rows that are present when rowspan overflows', """
<<table>
    <tr>
         <td>1</td>
         <td rowspan='5' colspan='2'>2</td>
    </tr>
    <tr>
         <td>3</td>
    </tr>
</table>
        """,
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='3'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
            ]),
        ]),
        ('it does not overflow rowspan to next row group', """
<table>
<thead>
    <tr>
        <td rowspan='5'>1</td>
        <td>2</td>
    </tr>
    <tr>
        <td>3</td>
    </tr>
</thead>
<tbody>
    <tr>
        <td>4</td>
        <td>5</td>
    </tr>
    <tr>
        <td>6</td>
        <td rowspan='5'>7</td>
    </tr>
</tbody>
<tfoot>
    <tr>
        <td rowspan='5'>8</td>
        <td>9</td>
    </tr>
</tfoot>
</table>
        """,
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='3'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='4'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='5'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='6'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='7'),
                    ]),
                ]),
                TRow(group='tfoot', cells=[
                    TCell(header=False, elements=[
                        TText(text='8'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='9'),
                    ]),
                ]),
            ]),
        ]),
        ('it does not overflow rowspan to next row group when tbody is missing', """
<table>
<thead>
    <tr>
        <td rowspan='5'>1</td>
        <td>2</td>
    </tr>
    <tr>
        <td>3</td>
    </tr>
</thead>
<tr>
    <td>4</td>
    <td>5</td>
</tr>
</table>
         """,
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='3'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='4'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='5'),
                    ]),
                ]),
            ]),
        ]),
        ('it handles rowspan with value zero', """
<table>
<thead>
    <tr>
        <td rowspan='0'>1</td>
        <td>2</td>
    </tr>
    <tr>
        <td>3</td>
    </tr>
</thead>
<tr>
    <td>4</td>
    <td>5</td>
</tr>
</table>
         """,
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='3'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='4'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='5'),
                    ]),
                ]),
            ]),
        ]),
        # because of unclosed tags, indents or spaces will be part of the raw text so don't indent
        ('it handles unclosed tags with rowspan and colspan', """
<table>
<tr>
<td rowspan='2'>1
<td rowspan='2' colspan='2'>2
<tr>
</table>
         """,
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2\n'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2\n'),
                    ]),
                ]),
            ]),
        ]),
    ]
)
def test_rowspan_colspan(_desc, html_text, expected):
    actual = parse_html(html_text)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


@pytest.mark.parametrize(
    '_desc,html_text,expected',
    [
        ('it handles rowspan at spec limit', create_table_html_with_rowspan(65534),
        [
            create_table(65534, 1),
        ]),
        ('it respects rowspan maximum limit', create_table_html_with_rowspan(65535),
        [
            append_blank_rows(create_table(65534, 1), 1),
        ]),
        ('it handles colspan at spec limit', """
<table>
    <tr><td colspan='1000'>0</td></tr>
</table>
        """,
        [
            create_table(1, 1000),
        ]),
        ('it respects colspan maximum limit', """
<table>
    <tr><td colspan='1000'>0</td></tr>
</table>
        """,
        [
            create_table(1, 1000),
        ]),
    ]
)
def test_rowspan_colspan_limits(_desc, html_text, expected):
    actual = parse_html(html_text)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


def test_rowspan_colspan_nested():
    html_text = """
<table>
    <tr>
        <td>1<table>
            <tr>
                <td rowspan='2' colspan='2'>2<table>
                    <tr>
                        <td>3</td>
                    </tr>
                </table></td>
            </tr>
            <tr></tr>
        </table></td>
    </tr>
</table>"""
    table_one = Table(id=0, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='3'),
            ]),
        ]),
    ])
    table_two = Table(id=1, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='2'),
                TRef(table=table_one),
            ]),
            TCell(header=False, elements=[
                TText(text='2'),
                TRef(table=table_one),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='2'),
                TRef(table=table_one),
            ]),
            TCell(header=False, elements=[
                TText(text='2'),
                TRef(table=table_one),
            ]),
        ]),
    ])
    table_three = Table(id=2, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='1'),
                TRef(table=table_two),
            ]),
        ]),
    ])
    expected = [table_three]

    actual = parse_html(html_text)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


#########################################################
# filtering - match
#########################################################

@pytest.mark.parametrize(
    '_desc,html_text,match,expected',
    [
        ('it returns empty list when no table',
        '<tr></tr>',
        '',
        []),
        ('it returns empty list when table is empty',
        '<table><tr></tr></table>',
        '',
        []),
        ('it returns empty list when table has no content and matching empty string',
        '<table><tr><td>  \r\n\t  </td></tr><tr><td>  \r\n\t  </td></tr></table>',
        '',
        []),
        ('it matches table with one cell when string match found',
        '<table><tr><td>123</td></tr></table>',
        '1',
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='123'),
                    ]),
                ]),
            ]),
        ]),
        ('it does not match table with one cell when no string match found',
        '<table><tr><td>123</td></tr></table>',
        'A',
        []),
        ('it matches in case-sensitive way when string match',
        '<table><tr><td>abc</td></tr></table>',
        'A',
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='abc'),
                    ]),
                ]),
            ]),
        ]),
        ('it matches using regex match',
        '<table><tr><td>123</td></tr></table>',
        re.compile('[0-9]'),
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='123'),
                    ]),
                ]),
            ]),
        ]),
        ('it matches multiple tables',
        '<table><tr><td>123</td></tr></table><table><tr><td>abc</td></tr></table><table><tr><td>456</td></tr></table>',
        re.compile('[0-9]'),
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='123'),
                    ]),
                ]),
            ]),
            Table(id=2, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='456'),
                    ]),
                ]),
            ]),
        ]),
    ]
)
def test_match(_desc, html_text, match, expected):
    actual = parse_html(html_text, match=match)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


def test_match_descendant_includes_root_table():
    html_text = """
<table>
    <tr><td>Z</td></tr>
</table>
<table>
    <tr>
        <td>A</td>
        <td><table>
            <tr>
                <td><table> <!-- descendant table matches -->
                    <tr><td>1</td></tr>
                </table></td>
            </tr>
        </table></td>
    </tr>
</table>
<table> <!-- root table matches -->
    <tr><td>2</td></tr>
</table>"""
    table_one = Table(id=1, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='1'),
            ]),
        ]),
    ])
    table_two = Table(id=2, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TRef(table=table_one),
            ]),
        ]),
    ])
    table_three = Table(id=3, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='A'),
            ]),
            TCell(header=False, elements=[
                TRef(table=table_two),
            ]),
        ]),
    ])
    table_four = Table(id=4, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='2'),
            ]),
        ]),
    ])
    match = re.compile('[0-9]')
    expected = [table_three, table_four]

    actual = parse_html(html_text, match=match)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


def test_match_root_includes_descendant_table():
    html_text = """
<table>
    <tr><td>Z</td></tr>
</table>
<table> <!-- root table matches -->
    <tr>
        <td>1</td>
        <td><table>
            <tr>
                <td><table>
                    <tr><td>A</td></tr>
                </table></td>
            </tr>
        </table></td>
    </tr>
</table>
<table> <!-- root table matches -->
    <tr><td>2</td></tr>
</table>"""
    table_one = Table(id=1, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='A'),
            ]),
        ]),
    ])
    table_two = Table(id=2, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TRef(table=table_one),
            ]),
        ]),
    ])
    table_three = Table(id=3, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='1'),
            ]),
            TCell(header=False, elements=[
                TRef(table=table_two),
            ]),
        ]),
    ])
    table_four = Table(id=4, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='2'),
            ]),
        ]),
    ])
    match = re.compile('[0-9]')
    expected = [table_three, table_four]

    actual = parse_html(html_text, match=match)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


#########################################################
# filtering - attributes
#########################################################


@pytest.mark.parametrize(
    '_desc,html_text,attrs,expected',
    [
        ('it selects tables matching one attribute',"""
<table id='2' class='one'>
    <tr><td>0</td></tr>
</table>
<table id='1' class='one'>
    <tr><td>1</td></tr>
</table>
<table id='1'>
    <tr><td>2</td></tr>
</table>
        """,
        {'id': '1'},
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
            Table(id=1, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
            ]),
        ]),
        ('it selects tables matching all two attributes',"""
<table id='2' class='one'>
    <tr><td>0</td></tr>
</table>
<table id='1' class='one'>
    <tr><td>1</td></tr>
</table>
<table id='1'>
    <tr><td>2</td></tr>
</table>
        """,
        {'id': '1', 'class': 'one'},
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
        ]),
        ('it selects attributes with no values',"""
<table id='2' class='one'>
    <tr><td>0</td></tr>
</table>
<table id='1' class>
    <tr><td>1</td></tr>
</table>
<table id='1'>
    <tr><td>2</td></tr>
</table>
        """,
        {'id': '1', 'class': None},
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
        ]),
    ]
)
def test_match_attr(_desc, html_text, attrs, expected):
    actual = parse_html(html_text, attrs=attrs)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


def test_match_attr_includes_descendants():
    html_text = """
<table>
    <tr><td>Z</td></tr>
</table>
<table>
    <tr>
        <td>1</td>
        <td><table id='A'> <!-- table matches -->
            <tr>
                <td>2</td>
            </tr>
            <tr>
                <td><table>
                    <tr>
                        <td>3</td>
                    </tr>
                    <tr>
                        <td><table>
                            <tr>
                                <td>4</td>
                            </tr>
                        </table></td>
                    </tr>
                </table></td>
            </tr>
        </table></td>
    </tr>
</table>
<table>
    <tr><td>2</td></tr>
</table>"""
    table_one = Table(id=0, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='4'),
            ]),
        ]),
    ])
    table_two = Table(id=1, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='3'),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TRef(table=table_one),
            ]),
        ]),
    ])
    table_three = Table(id=2, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='2'),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TRef(table=table_two),
            ]),
        ]),
    ])
    attrs = {'id': 'A'}
    expected = [table_three]

    actual = parse_html(html_text, attrs=attrs)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


#########################################################
# filtering - displayed only
#########################################################


@pytest.mark.parametrize(
    '_desc,html_text,displayed_only,expected',
    [
        ('it selects tables and elements that are displayed when displayed only is True',"""
<table style='background: red; display: none;'>
    <tr><td>0</td></tr>
</table>
<table>
    <tr><td>1</td></tr>
</table>
<table>
    <tr><td rowspan='2'>2</td></tr>
    <tr><td style='display: none'>3</td></tr>
    <tr style='display: none'><td>4</td></tr>
</table>
        """,
        True,
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
            Table(id=1, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
            ]),
        ]),
        ('it selects tables and elements regardless of display property when displayed only is False',"""
<table style='background: red; display: none;'>
    <tr><td>0</td></tr>
</table>
<table>
    <tr><td>1</td></tr>
</table>
<table>
    <tr><td rowspan='2'>2</td></tr>
    <tr><td style='display: none'>3</td></tr>
    <tr style='display: none'><td>4</td></tr>
</table>
        """,
        False,
        [
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='0'),
                    ]),
                ]),
            ]),
            Table(id=1, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
            Table(id=2, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='3'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='4'),
                    ]),
                ]),
            ]),
        ]),
    ]
)
def test_displayed_only(_desc, html_text, displayed_only, expected):
    actual = parse_html(html_text, displayed_only=displayed_only)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


#########################################################
# filtering - extract links
#########################################################


@pytest.mark.parametrize(
    '_desc,html_text,extract_links,expected',
    [
        ('it returns links as regular text when extract links is none',"""
<table>
<thead>
    <tr><td>Link in <a href='#1'>header</a></td></tr>
</thead>
    <tr><td>Link in <a href='#2'>body</a></td></tr>
<tfoot>
    <tr><td>Link in <a href='#3'>footer</a></td></tr>
</tfoot>
</table>
        """,
        None,
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TText(text='header'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TText(text='body'),
                    ]),
                ]),
                TRow(group='tfoot', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TText(text='footer'),
                    ]),
                ]),
            ]),
        ]),
        ('it returns links in header only when extract links is thead',"""
<table>
<thead>
    <tr><td>Link in <a href='#1'>header</a></td></tr>
</thead>
    <tr><td>Link in <a href='#2'>body</a></td></tr>
<tfoot>
    <tr><td>Link in <a href='#3'>footer</a></td></tr>
</tfoot>
</table>
        """,
        'thead',
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TLink(href='#1', text='header'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TText(text='body'),
                    ]),
                ]),
                TRow(group='tfoot', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TText(text='footer'),
                    ]),
                ]),
            ]),
        ]),
        ('it returns links in body only when extract links is body',"""
<table>
<thead>
    <tr><td>Link in <a href='#1'>header</a></td></tr>
</thead>
    <tr><td>Link in <a href='#2'>body</a></td></tr>
<tfoot>
    <tr><td>Link in <a href='#3'>footer</a></td></tr>
</tfoot>
</table>
        """,
        'tbody',
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TText(text='header'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TLink(href='#2', text='body'),
                    ]),
                ]),
                TRow(group='tfoot', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TText(text='footer'),
                    ]),
                ]),
            ]),
        ]),
        ('it returns links in footer only when extract links is tfoot',"""
<table>
<thead>
    <tr><td>Link in <a href='#1'>header</a></td></tr>
</thead>
    <tr><td>Link in <a href='#2'>body</a></td></tr>
<tfoot>
    <tr><td>Link in <a href='#3'>footer</a></td></tr>
</tfoot>
</table>
        """,
        'tfoot',
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TText(text='header'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TText(text='body'),
                    ]),
                ]),
                TRow(group='tfoot', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TLink(href='#3', text='footer'),
                    ]),
                ]),
            ]),
        ]),
        ('it returns links for all row groups when extract links is all',"""
<table>
<thead>
    <tr><td>Link in <a href='#1'>header</a></td></tr>
</thead>
    <tr><td>Link in <a href='#2'>body</a></td></tr>
<tfoot>
    <tr><td>Link in <a href='#3'>footer</a></td></tr>
</tfoot>
</table>
        """,
        'all',
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TLink(href='#1', text='header'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TLink(href='#2', text='body'),
                    ]),
                ]),
                TRow(group='tfoot', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TLink(href='#3', text='footer'),
                    ]),
                ]),
            ]),
        ]),
        ('it returns all text within link tags even when there are other elements',"""
<table>
<thead>
    <tr><td>Link in <a href='#1'><span>header</span></a></td></tr>
</thead>
    <tr><td>Link in <a href='#2'>bo<span>dy</span></a></td></tr>
<tfoot>
    <tr><td>Link in <a href='#3'><span>foo</span>ter</a></td></tr>
</tfoot>
</table>
        """,
        'all',
        [
            Table(id=0, rows=[
                TRow(group='thead', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TLink(href='#1', text='header'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TLink(href='#2', text='body'),
                    ]),
                ]),
                TRow(group='tfoot', cells=[
                    TCell(header=False, elements=[
                        TText(text='Link in '),
                        TLink(href='#3', text='footer'),
                    ]),
                ]),
            ]),
        ]),
    ]
)
def test_extract_links(_desc, html_text, extract_links, expected):
    actual = parse_html(html_text, extract_links=extract_links)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


#########################################################
# filtering - combination
#########################################################


def test_filtering_combination():
    html_text = """
<table>
    <tr>
        <td>1</td>
        <td><table id='A'> <!-- table matches -->
            <tr>
                <td>2</td>
            </tr>
            <tr>
                <td><table>
                    <tr>
                        <td>3</td>
                    </tr>
                    <tr style='display: none'>
                        <td>30</td>
                    </tr>
                    <tr>
                        <td><table>
                            <tr>
                                <td>4</td>
                            </tr>
                        </table></td>
                    </tr>
                </table></td>
            </tr>
        </table></td>
    </tr>
</table>
<table>
    <tr>
        <td>5</td>
        <td><table id='B'>
            <tr>
                <td>6</td>
            </tr>
            <tr>
                <td><table>
                    <tr>
                        <td>7</td>
                    </tr>
                    <tr>
                        <td><table>
                            <tr>
                                <td>8</td>
                            </tr>
                        </table></td>
                    </tr>
                </table></td>
            </tr>
        </table></td>
    </tr>
</table>
<table>
    <tr>
        <td>5</td>
        <td><table id='A' style='display: none'>
            <tr>
                <td>6</td>
            </tr>
            <tr>
                <td><table>
                    <tr>
                        <td>7</td>
                    </tr>
                    <tr>
                        <td><table>
                            <tr>
                                <td>8</td>
                            </tr>
                        </table></td>
                    </tr>
                </table></td>
            </tr>
        </table></td>
    </tr>
</table>"""
    table_one = Table(id=0, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='4'),
            ]),
        ]),
    ])
    table_two = Table(id=1, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='3'),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TRef(table=table_one),
            ]),
        ]),
    ])
    table_three = Table(id=2, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='2'),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TRef(table=table_two),
            ]),
        ]),
    ])
    match = re.compile('[0-9]')
    attrs = {'id': 'A'}
    displayed_only = True
    expected = [table_three]

    actual = parse_html(html_text, match=match, attrs=attrs, displayed_only=displayed_only)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


#########################################################
# test file input
#########################################################


def test_file_input():
    file_path = Path(__file__).parent / 'test_file_input.html'
    expected = [
        Table(id=0, rows=[
            TRow(group='tbody', cells=[
                TCell(header=False, elements=[
                    TText(text='1'),
                ]),
                TCell(header=False, elements=[
                    TText(text='2'),
                ]),
            ]),
            TRow(group='tbody', cells=[
                TCell(header=False, elements=[
                    TText(text='3'),
                ]),
                TCell(header=False, elements=[
                    TText(text='4'),
                ]),
            ]),
        ]),
    ]

    actual = parse_html(file_path)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


def test_file_does_not_exist():
    file_path = Path(__file__).parent / 'no_such_file.html'

    with pytest.raises(IOError, match='Failed to read file'):
        parse_html(file_path)


#########################################################
# test url input
#########################################################


def test_url_input():
    url = 'https://raw.githubusercontent.com/lawcal/html-table-takeout/6ed8fde22d734ea0950cd155a218fb4582d1ad19/tests/test_file_input.html' # pylint: disable=line-too-long
    expected = [
        Table(id=0, rows=[
            TRow(group='tbody', cells=[
                TCell(header=False, elements=[
                    TText(text='1'),
                ]),
                TCell(header=False, elements=[
                    TText(text='2'),
                ]),
            ]),
            TRow(group='tbody', cells=[
                TCell(header=False, elements=[
                    TText(text='3'),
                ]),
                TCell(header=False, elements=[
                    TText(text='4'),
                ]),
            ]),
        ]),
    ]

    actual = parse_html(url)
    assert len(actual) == len(expected)
    for idx, table in enumerate(actual):
        assert table == expected[idx]


def test_url_resource_does_not_exist():

    url = 'https://raw.githubusercontent.com/lawcal/html-table-takeout/6ed8fde22d734ea0950cd155a218fb4582d1ad19/tests/test_file_input_does_not_exist.html' # pylint: disable=line-too-long

    with pytest.raises(IOError, match='Failed to make HTTP request'):
        parse_html(url)
