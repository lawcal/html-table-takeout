# pylint: disable=line-too-long,too-many-lines
import pytest

from html_table_takeout import Table, TRow, TCell, TLink, TRef, TText


#########################################################
# Table to_html
#########################################################


@pytest.mark.parametrize(
    '_desc,table,expected',
    [
        ('it converts table with no rows to html',
            Table(id=0),
"""
<table data-table-id='0'>
</table>"""
        ),
        ('it converts table with no cells to html',
            Table(id=0, rows=[
                TRow(group='tbody'),
            ]),
"""
<table data-table-id='0'>
<tbody>
    <tr>
    </tr>
</tbody>
</table>"""
        ),
        ('it converts table with one cell to html',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
"""
<table data-table-id='0'>
<tbody>
    <tr>
        <td>1</td>
    </tr>
</tbody>
</table>"""
        ),
        ('it converts basic table to html',
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
"""
<table data-table-id='0'>
<tbody>
    <tr>
        <td>1</td>
        <td>2</td>
    </tr>
    <tr>
        <td>3</td>
        <td>4</td>
    </tr>
</tbody>
</table>"""
        ),
        ('it converts table with line breaks to html',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='\n3'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='4'),
                    ]),
                ]),
            ]),
"""
<table data-table-id='0'>
<tbody>
    <tr>
        <td>1<br/></td>
        <td>2</td>
    </tr>
    <tr>
        <td><br/>3</td>
        <td>4</td>
    </tr>
</tbody>
</table>"""
        ),
        ('it converts table with thead, tbody, tfoot to html',
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
"""
<table data-table-id='0'>
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
</table>"""
        ),
        ('it converts table with links to html',
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
"""
<table data-table-id='0'>
<thead>
    <tr>
        <td>Link in <a href='#1'>header</a></td>
    </tr>
</thead>
<tbody>
    <tr>
        <td>Link in <a href='#2'>body</a></td>
    </tr>
</tbody>
<tfoot>
    <tr>
        <td>Link in <a href='#3'>footer</a></td>
    </tr>
</tfoot>
</table>"""
        ),
        ('it converts table with html escaped text to html',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='& I "'),
                        TLink(href='&', text='>'),
                    ]),
                ]),
            ]),
"""
<table data-table-id='0'>
<tbody>
    <tr>
        <td>&amp; I &quot;<a href='&amp;'>&gt;</a></td>
    </tr>
</tbody>
</table>"""
        ),
    ]
)
def test_table_to_html(_desc, table: Table, expected):
    assert table.to_html(indent=4) == expected.lstrip()


def test_table_nested_to_html():
    table_one = Table(id=0, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='3\n4\n5'),
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
        ]),
    ])
    expected = """
<table data-table-id='2'>
<tbody>
    <tr>
        <td>1<table data-table-id='1'><tbody><tr><td>2<table data-table-id='0'><tbody><tr><td>3<br/>4<br/>5</td></tr></tbody></table></td></tr></tbody></table></td>
    </tr>
</tbody>
</table>"""
    assert table_three.to_html(indent=4) == expected.lstrip()


#########################################################
# Table to_csv
#########################################################


@pytest.mark.parametrize(
    '_desc,table,expected',
    [
        ('it returns empty string when table has no rows',
            Table(id=0),
            ''
        ),
        ('it returns single newline when table has no cells',
            Table(id=0, rows=[
                TRow(group='tbody'),
            ]),
            '\n'
        ),
        ('it converts table with one cell to csv',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
            '1\n'
        ),
        ('it converts basic table to csv',
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
            '1,2\n3,4\n'
        ),
        ('it converts table with line breaks to csv',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='\n3'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='4'),
                    ]),
                ]),
            ]),
            '1,2\n3,4\n'
        ),
        ('it converts table with thead, tbody, tfoot to csv',
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
            '1,2\n3,4\n5,6\n7,8\n9,10\n11,12\n'
        ),
        ('it converts table with links to csv',
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
            'Link in header\nLink in body\nLink in footer\n'
        ),
        ('it converts table with csv special characters to csv',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='"One day, lad, all this will be yours."'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='"What, the curtains?"'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='"We want...a SHRUBBERY!\n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='One that\'s nice. And not too expensive."'),
                    ]),
                ]),
            ]),
            '"""One day, lad, all this will be yours.""","""What, the curtains?"""\n"""We want...a SHRUBBERY!","One that\'s nice. And not too expensive."""\n'
        ),
    ]
)
def test_table_to_csv(_desc, table: Table, expected):
    assert table.to_csv() == expected


def test_table_nested_to_csv():
    table_one = Table(id=0, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='\n3\n\n'),
                TText(text='4'),
            ]),
            TCell(header=False, elements=[
                TText(text='5\n\n'),
                TText(text='6\n'),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='7'),
            ]),
            TCell(header=False, elements=[
                TText(text='8\n\n'),
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
                TText(text='1\n'),
                TRef(table=table_two),
            ]),
            TCell(header=False, elements=[
                TText(text='9\n'),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='0'),
            ]),
        ]),
    ])
    expected = '"1\n23\n\n4 5\n\n6\n7 8",9\n0\n'
    assert table_three.to_csv() == expected


#########################################################
# Table inner_text
#########################################################


@pytest.mark.parametrize(
    '_desc,table,expected',
    [
        ('it returns empty string for table with no rows',
            Table(id=0),
            ''
        ),
        ('it returns empty string for table with no cells',
            Table(id=0, rows=[
                TRow(group='tbody'),
            ]),
            ''
        ),
        ('it returns text with multiple spaces and line breaks',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='   1   \n'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2   '),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='\n3\n\n'),
                        TText(text='4'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='   5   '),
                    ]),
                ]),
            ]),
            '1 2\n3\n\n4 5'
        ),
        ('it returns text portion of links',
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
            'Link in header\nLink in body\nLink in footer'
        ),
        ('it returns text with html special characters',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='& I "'),
                        TLink(href='&', text='>'),
                    ]),
                ]),
            ]),
            '& I ">'
        ),
    ]
)
def test_table_inner_text(_desc, table: Table, expected):
    assert table.inner_text() == expected


def test_table_nested_inner_text():
    table_one = Table(id=0, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='\n3\n\n'),
                TText(text='4'),
            ]),
            TCell(header=False, elements=[
                TText(text='5\n\n'),
                TText(text='6\n'),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='7'),
            ]),
            TCell(header=False, elements=[
                TText(text='8\n\n'),
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
                TText(text='1\n'),
                TRef(table=table_two),
            ]),
            TCell(header=False, elements=[
                TText(text='9\n'),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='0'),
            ]),
        ]),
    ])
    expected = '1\n23\n\n4 5\n\n6\n7 8 9\n0'
    assert table_three.inner_text() == expected


#########################################################
# Table max_width
#########################################################

@pytest.mark.parametrize(
    '_desc,table,expected',
    [
        ('it returns zero for table with no rows',
            Table(id=0),
            0
        ),
        ('it returns zero for table with no cells',
            Table(id=0, rows=[
                TRow(group='tbody'),
            ]),
            0
        ),
        ('it returns one for table with one cell',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
            1
        ),
        ('it returns two for table with 2x2 cells',
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
            2
        ),
        ('it returns maximum number of cells for ragged table',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
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
            2
        ),
    ]
)
def test_table_max_width(_desc, table: Table, expected):
    assert table.max_width() == expected


def test_table_nested_max_width():
    table_one = Table(id=0, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='3'),
            ]),
            TCell(header=False, elements=[
                TText(text='4'),
            ]),
            TCell(header=False, elements=[
                TText(text='5'),
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
        ]),
    ])
    expected = 1 # only counts root table
    assert table_three.max_width() == expected


#########################################################
# Table is_rectangular
#########################################################


@pytest.mark.parametrize(
    '_desc,table,expected',
    [
        ('it returns false for table with no rows',
            Table(id=0),
            False
        ),
        ('it returns false for table with no cells',
            Table(id=0, rows=[
                TRow(group='tbody'),
            ]),
            False
        ),
        ('it returns false for table with multiple rows with no cells',
            Table(id=0, rows=[
                TRow(group='tbody'),
                TRow(group='tbody'),
                TRow(group='tbody'),
            ]),
            False
        ),
        ('it returns true for table with one cell',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
            ]),
            True
        ),
        ('it returns false for table with uneven number of cells',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False),
                ]),
            ]),
            False
        ),
    ]
)
def test_table_is_rectangular(_desc, table: Table, expected):
    assert table.is_rectangular() == expected


def test_table_nested_is_rectangular():
    table_one = Table(id=0, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='3'),
            ]),
            TCell(header=False, elements=[
                TText(text='4'),
            ]),
            TCell(header=False, elements=[
                TText(text='5'),
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
        ]),
    ])
    expected = True # only considers root table
    assert table_three.is_rectangular() == expected


#########################################################
# Table rectangify
#########################################################


@pytest.mark.parametrize(
    '_desc,table,expected',
    [
        ('it does not modify table when table has no rows',
            Table(id=0),
            Table(id=0),
        ),
        ('it does not modify table when table has no cells',
            Table(id=0, rows=[
                TRow(group='tbody'),
            ]),
            Table(id=0, rows=[
                TRow(group='tbody'),
            ]),
        ),
        ('it does not modify table when table has multiple rows with no cells',
            Table(id=0, rows=[
                TRow(group='tbody'),
                TRow(group='tbody'),
                TRow(group='tbody'),
            ]),
            Table(id=0, rows=[
                TRow(group='tbody'),
                TRow(group='tbody'),
                TRow(group='tbody'),
            ]),
        ),
        ('it pads rows with short cells to match to row with most cells',
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='tbody'),
            ]),
            Table(id=0, rows=[
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(),
                ]),
                TRow(group='tbody', cells=[
                    TCell(header=False, elements=[
                        TText(text='1'),
                    ]),
                    TCell(header=False, elements=[
                        TText(text='2'),
                    ]),
                ]),
                TRow(group='tbody', cells=[
                    TCell(),
                    TCell(),
                ]),
            ]),
        ),
    ]
)
def test_table_rectangify(_desc, table: Table, expected):
    table.rectangify()
    assert table == expected
    if table.max_width() > 0:
        assert table.is_rectangular()


def test_table_nested_rectangify():
    table_child = Table(id=0, rows=[
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
    ])
    table = Table(id=1, rows=[
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='1'),
                TRef(table=table_child),
            ]),
        ]),
        TRow(group='tbody'),
    ])
    table_child_expected = Table(id=0, rows=[
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
    ])
    table_expected = Table(id=1, rows=[ # only pads root table
        TRow(group='tbody', cells=[
            TCell(header=False, elements=[
                TText(text='1'),
                TRef(table=table_child_expected),
            ]),
        ]),
        TRow(group='tbody', cells=[
            TCell(),
        ]),
    ])
    table.rectangify()
    assert table == table_expected
    if table.max_width() > 0:
        assert table.is_rectangular()


#########################################################
# TRow
#########################################################


@pytest.mark.parametrize(
    '_desc,row,expected',
    [
        ('it returns false when row is empty',
            TRow(),
            False
        ),
        ('it returns false when row contains one non-header cell',
            TRow(cells=[TCell()]),
            False
        ),
        ('it returns true when row contains one header cell',
            TRow(cells=[TCell(header=True)]),
            True
        ),
        ('it returns false when row contains one non-header cell and one header cell',
            TRow(cells=[TCell(), TCell(header=True)]),
            False
        ),
    ]
)
def test_trow_contains_all_th(_desc, row: TRow, expected):
    assert row.contains_all_th() == expected


def test_trow_nested_contains_all_th():
    row = TRow(cells=[
        TCell(elements=[
            TRef(table=Table(
                rows=[
                    TRow(cells=[TCell(header=True)])
                ]
            ))
        ])
    ])
    expected = False # only considers root table
    assert row.contains_all_th() == expected


@pytest.mark.parametrize(
    '_desc,row,expected',
    [
        ('it returns false when row is empty',
            TRow(),
            False
        ),
        ('it returns false when row contains one non-header cell and one header cell',
            TRow(cells=[TCell(), TCell(header=True)]),
            False
        ),
        ('it returns true when group is thead and row contains one header cell',
            TRow(group='thead', cells=[TCell(header=True)]),
            True
        ),
        ('it returns true when group is tbody and row contains one header cell',
            TRow(group='tbody', cells=[TCell(header=True)]),
            True
        ),
        ('it returns true when group is tfoot and row contains one header cell',
            TRow(group='tfoot', cells=[TCell(header=True)]),
            True
        ),
        ('it returns true when group is thead and row contains one non-header cell',
            TRow(group='thead', cells=[TCell()]),
            True
        ),
        ('it returns false when group is tbody and row contains one non-header cell',
            TRow(group='tbody', cells=[TCell()]),
            False
        ),
        ('it returns false when group is tfoot and row contains one non-header cell',
            TRow(group='tfoot', cells=[TCell()]),
            False
        ),
    ]
)
def test_trow_is_header_like(_desc, row: TRow, expected):
    assert row.is_header_like() == expected
