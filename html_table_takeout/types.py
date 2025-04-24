import csv
from dataclasses import dataclass, field
import html
import io
import re
from typing import Literal


_RE_WHITESPACE_NEWLINE = re.compile(r'[\r\n]+|\s{2,}')
_RE_WHITESPACE = re.compile(r'[^\S\r\n]') # whitespace but not newline


def _collapse_whitespace(s: str, include_newline: bool = True) -> str:
    regex = _RE_WHITESPACE_NEWLINE if include_newline else _RE_WHITESPACE
    return regex.sub(' ', s.strip())


def _calc_space_newline(indent: int) -> tuple[str, str]:
    if indent < 0:
        return '', ''
    return ' ' * min(indent, 24), '\n'


@dataclass
class TText:
    text: str = ''

    def to_html(self) -> str:
        return html.escape(self.text).replace('\n', '<br/>')

    def inner_text(self) -> str:
        return self.text


@dataclass
class TLink(TText):
    href: str = ''

    def to_html(self) -> str:
        href = html.escape(self.href)
        href_attr = f" href='{href}'" if href else ''
        return f"<a{href_attr}>{super().to_html()}</a>"


@dataclass
class TCell:
    header: bool = False
    elements: list[TText] = field(default_factory=list)

    def __iter__(self):
        for element in self.elements:
            yield element

    def to_html(self, indent=0) -> str:
        space, _ = _calc_space_newline(indent)
        tag = 'th' if self.header else 'td'
        html_content = _collapse_whitespace(''.join(e.to_html() for e in self.elements))
        return f"{space}<{tag}>{html_content}</{tag}>"

    def inner_text(self) -> str:
        return _collapse_whitespace(''.join(e.inner_text() for e in self.elements), False)


@dataclass
class TRow:
    group: Literal['thead', 'tbody', 'tfoot'] = 'tbody'
    cells: list[TCell] = field(default_factory=list)

    def __iter__(self):
        for cell in self.cells:
            yield cell

    def to_html(self, indent=0) -> str:
        space, newline = _calc_space_newline(indent)
        html_content = (
            newline + newline.join(c.to_html(indent * 2) for c in self.cells)
            if self.cells else ''
        )
        return f"{space}<tr>{html_content}{newline}{space}</tr>"

    def inner_text(self) -> str:
        return ' '.join(c.inner_text() for c in self.cells)


    def contains_all_th(self) -> bool:
        """
        Whether the cells in the row contain all header cells. Descendant
        Tables are not considered.
        """
        for c in self.cells:
            if not c.header:
                return False
        return bool(self.cells)


    def is_header_like(self) -> bool:
        """
        Whether the row functions like a header. A row is considered like
        a header if was originally enclosed in a `<thead>` or if it contains
        all header cells. Descendant Tables are not considered.
        """
        return self.group == 'thead' or self.contains_all_th()


@dataclass
class Table:
    id: int = -1
    rows: list[TRow] = field(default_factory=list)

    def __iter__(self):
        for row in self.rows:
            yield row

    def to_html(self, indent=2) -> str:
        """
        Returns the Table as HTML.
        """
        _, newline = _calc_space_newline(indent)
        # Insert <thead>, <tbody> or <tfoot> when row group differs from previous
        html_content = ''
        prev_row_group = ''
        for r in self.rows:
            if r.group != prev_row_group:
                if prev_row_group:
                    # Add end tag for previous group
                    html_content += f"{newline}</{prev_row_group}>"
                # Add start tag for current group
                html_content += f"{newline}<{r.group}>"
            html_content += f"{newline}{r.to_html(indent)}"
            prev_row_group = r.group
        # Add end tag for last group
        if prev_row_group:
            html_content += f"{newline}</{prev_row_group}>"
        return f"<table data-table-id='{self.id}'>{html_content}{newline}</table>"


    def to_csv(self) -> str:
        """
        Returns the Table as CSV.
        """
        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=',',
            quotechar='"',
            escapechar=None,
            doublequote=True,
            skipinitialspace=False,
            lineterminator='\n',
            quoting=csv.QUOTE_MINIMAL,
        )
        for r in self.rows:
            writer.writerow(c.inner_text() for c in r.cells)
        return output.getvalue()


    def inner_text(self) -> str:
        """
        Returns the Table as text with whitespaces collapsed.
        """
        return '\n'.join(r.inner_text() for r in self.rows)


    def max_width(self) -> int:
        """
        Returns the greatest number of cells found in all the rows. Descendant
        Tables are not considered.
        """
        if not self.rows:
            return 0
        return max(len(r.cells) for r in self.rows)


    def is_rectangular(self) -> bool:
        """
        Whether the Table contains the same number of cells on each row. A
        Table must contain at least one cell to be rectangular. Descendant
        Tables are not considered.
        """
        if len(self.rows) <= 0:
            # Reject zero dimensions
            return False
        prev_width = len(self.rows[0].cells)
        for r in self.rows:
            if len(r.cells) != prev_width:
                return False
            prev_width = len(r.cells)
        return prev_width > 0


    def rectangify(self) -> None:
        """
        Modifies the Table by appending empty cells to rows up to the maximum
        width. This does not modify descendant Tables.
        """
        max_width = self.max_width()
        for r in self.rows:
            cells_to_pad = max_width - len(r.cells)
            for _ in range(cells_to_pad):
                r.cells.append(TCell())


@dataclass
class TRef(TText):
    table: Table = field(default_factory=Table)
    text: Literal[''] = ''

    def to_html(self) -> str:
        return self.table.to_html(indent=-1)

    def inner_text(self) -> str:
        return self.table.inner_text()
