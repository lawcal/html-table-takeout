from dataclasses import dataclass, field
from html.parser import HTMLParser
import re
from typing import Literal
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .types import Table, TRow, TCell, TLink, TRef, TBreak, TText


def _found_match(s: str, match: str | re.Pattern | None) -> bool:
    if not match:
        return True
    if isinstance(match, re.Pattern):
        return match.search(s) is not None
    return match.lower() in s.lower()


def _whitespace_stripped(s: str) -> str:
    return ''.join(s.split())


def _has_style_display_none(attrs: dict[str, str | None]) -> bool:
    styles = attrs.get('style') or ''
    return 'display:none' in _whitespace_stripped(styles)


def _found_match_attributes(attrs: dict[str, str | None], match: dict[str, str | None] | None) -> bool:
    if match is None:
        return True
    return match.items() <= attrs.items()


def _extract_links_allowed(
    ctx: '_Context',
    extract_links: Literal[None, 'thead', 'tbody', 'tfoot', 'all']
) -> bool:
    return extract_links is not None and (
        extract_links == 'all'
        or (ctx.in_thead and extract_links == 'thead')
        or (ctx.in_tfoot and extract_links == 'tfoot')
        or (not (ctx.in_thead or ctx.in_tfoot) and extract_links == 'tbody')
    )


def _is_http_url(url: str) -> bool:
    try:
        url_parts = urlparse(url)
    except Exception as _e: # pylint: disable=broad-except
        return False
    return url_parts.scheme in ('http', 'https')


def _request_http(url: str, encoding: str, request_headers: dict[str, str] | None = None) -> str:
    try:
        with urlopen(Request(url=url, headers=request_headers or {})) as resp:
            return resp.read().decode(encoding)
    except Exception as e:
        raise IOError(f"Failed to make HTTP request. Error:{repr(e)}") from None


def _read_file(file_path: Path, encoding: str) -> str:
    try:
        with file_path.open(mode='r', encoding=encoding) as file:
            return file.read()
    except Exception as e:
        raise IOError(f"Failed to read file. Error:{repr(e)}") from None


@dataclass
class _Context:
    table: Table = field(default_factory=Table)
    in_thead: bool = False
    in_tbody: bool = False
    in_tfoot: bool = False
    in_tr: bool = False
    in_td: bool = False
    in_a: bool = False
    index: int = 0
    remainder: list[tuple[int, TCell, int]] = field(default_factory=list)
    next_remainder: list[tuple[int, TCell, int]] = field(default_factory=list)


class _HtmlTableParser(HTMLParser):
    def __init__(
        self,
        match: str | re.Pattern | None = None,
        attrs: dict[str, str | None] | None = None,
        displayed_only: bool = True,
        extract_links: Literal[None, 'thead', 'tbody', 'tfoot', 'all'] = 'all',
    ) -> None:
        HTMLParser.__init__(self, convert_charrefs=True)
        self.id = 0
        self.match = match
        self.attrs = attrs
        self.displayed_only = displayed_only
        self.extract_links = extract_links
        self.tables: list[Table] = []
        self.contexts: list[_Context] = []


    def handle_starttag(self, tag: str, attrs):
        attrs = dict(attrs)
        if self.displayed_only and _has_style_display_none(attrs):
            return

        ctx = self.contexts[-1] if self.contexts else None
        if tag == 'table' and (
            ctx # always pass child tables
            or _found_match_attributes(attrs, self.attrs)
        ):
            self.contexts.append(_Context())
        if ctx is None:
            return

        if tag in ('thead', 'tbody', 'tfoot'):
            # Handle implicit end of previous row
            if ctx.in_tr:
                self.handle_endtag('tr')

            # rowspan must not cross row groups
            ctx.remainder = []

            ctx.in_thead = tag == 'thead'
            ctx.in_tbody = tag == 'tbody'
            ctx.in_tfoot = tag == 'tfoot'
            ctx.in_tr = False
            ctx.in_td = False
            ctx.in_a = False

        elif tag == 'tr':
            # Handle implicit end of previous row
            if ctx.in_tr:
                self.handle_endtag('tr')

            ctx.table.rows.append(TRow(group='thead' if ctx.in_thead else 'tfoot' if ctx.in_tfoot else 'tbody'))
            ctx.index = 0
            ctx.next_remainder = []

            ctx.in_tr = True
            ctx.in_td = False
            ctx.in_a = False

        elif tag in ('td', 'th') and ctx.in_tr:
            row = ctx.table.rows[-1]

            # Append cells from previous rows with rowspan > 1 that come before this <td>
            while ctx.remainder and ctx.remainder[0][0] <= ctx.index:
                prev_i, prev_cell, prev_rowspan = ctx.remainder.pop(0)
                row.cells.append(prev_cell)
                if prev_rowspan > 1:
                    ctx.next_remainder.append((prev_i, prev_cell, prev_rowspan - 1))
                ctx.index += 1

            # Append the cell from this <td>, colspan times
            cell = TCell(header=tag == 'th')
            # According to spec, rowspan may be zero meaning the cell spans remaining rows in row group:
            # https://html.spec.whatwg.org/multipage/tables.html#attr-tdth-rowspan
            rowspan = min(max(0, int(attrs.get('rowspan', 1))), 65534) or 65534 # limits according to spec
            colspan = min(max(1, int(attrs.get('colspan', 1))), 1000) # limits according to spec

            for _ in range(colspan):
                row.cells.append(cell)
                if rowspan > 1:
                    ctx.next_remainder.append((ctx.index, cell, rowspan - 1))
                ctx.index += 1

            ctx.in_td = True
            ctx.in_a = False

        elif tag == 'a' and ctx.in_td:
            cell = ctx.table.rows[-1].cells[-1]
            if _extract_links_allowed(ctx, self.extract_links):
                cell.elements.append(TLink(href=attrs.get('href', '').strip()))
            else:
                cell.elements.append(TText())

            ctx.in_a = True

        elif tag == 'br' and ctx.in_td:
            cell = ctx.table.rows[-1].cells[-1]
            cell.elements.append(TBreak(text='\n'))


    def handle_endtag(self, tag: str):
        ctx = self.contexts[-1] if self.contexts else None
        if ctx is None:
            return

        if tag == 'table':
            # Handle implicit end of previous row
            if ctx.in_tr:
                self.handle_endtag('tr')
            ctx = self.contexts.pop()
            parent_ctx = self.contexts[-1] if self.contexts else None
            if ctx.table.max_width() > 0:
                # Assign table id
                ctx.table.id = self.id
                self.id += 1
                if parent_ctx:
                    # Descendant table
                    parent_ctx.table.rows[-1].cells[-1].elements.append(TRef(table=ctx.table))
                else:
                    # Root table
                    inner_text = ctx.table.inner_text()
                    if _whitespace_stripped(inner_text) and _found_match(inner_text, self.match):
                        self.tables.append(ctx.table)

        elif ((tag == 'thead' and ctx.in_thead)
            or (tag == 'tbody' and ctx.in_tbody)
            or (tag == 'tfoot' and ctx.in_tfoot)):
            # rowspan must not cross row groups
            ctx.remainder = []

            ctx.in_thead = False
            ctx.in_tbody = False
            ctx.in_tfoot = False
            ctx.in_tr = False
            ctx.in_td = False
            ctx.in_a = False

        elif tag == 'tr' and ctx.in_tr:
            row = ctx.table.rows[-1]

            # Append cells from previous rows at the final position
            for prev_i, prev_cell, prev_rowspan in ctx.remainder:
                row.cells.append(prev_cell)
                if prev_rowspan > 1:
                    ctx.next_remainder.append((prev_i, prev_cell, prev_rowspan - 1))
            ctx.remainder = ctx.next_remainder

            ctx.in_tr = False
            ctx.in_td = False
            ctx.in_a = False

        elif tag in ('td', 'th') and ctx.in_td:
            # The following comments are CRITICAL for understanding the code. Do not omit them:
            # It is critical that we set `ctx.in_tr = True` or the code won't work at all.
            # This is because <td> or <th> must always be contained inside a <tr>.
            # Ignore suggestions that the line can be optimized away. It cannot be omitted.
            ctx.in_tr = True # important - do not omit this
            ctx.in_td = False
            ctx.in_a = False

        elif tag == 'a' and ctx.in_a:
            ctx.in_a = False


    def handle_data(self, data: str):
        ctx = self.contexts[-1] if self.contexts else None
        if ctx is None:
            return

        if ctx.in_a: # most specific condition so must be checked first
            cell = ctx.table.rows[-1].cells[-1]
            element = cell.elements[-1]
            element.text += data

        elif ctx.in_td:
            cell = ctx.table.rows[-1].cells[-1]
            cell.elements.append(TText(text=data))


def _parse_html_text(
    html_text: str,
    match: str | re.Pattern | None = None,
    attrs: dict[str, str | None] | None = None,
    displayed_only: bool = True,
    extract_links: Literal[None, 'thead', 'tbody', 'tfoot', 'all'] = None
) -> list[Table]:
    p = _HtmlTableParser(
        match,
        attrs,
        displayed_only,
        extract_links
    )
    p.feed(html_text)
    return p.tables


def parse_html(
    html_source: str | Path,
    *,
    match: str | re.Pattern | None = None,
    attrs: dict[str, str | None] | None = None,
    encoding: str = 'utf-8',
    displayed_only: bool = True,
    extract_links: Literal[None, 'thead', 'tbody', 'tfoot', 'all'] = 'all',
    request_headers: dict[str, str] | None = None
) -> list[Table]:
    r"""
    Parse HTML tables into a ``list`` of ``Table`` objects.

    Parameters
    ----------
    html_source : str or Path
        Source for the HTML tables. Can be text, a URL or local file Path.
        For URL, the string must start with "http://" or "https://".
        For local file source, pass in a Path object.

    match : str or compiled regular expression, optional
        Tables with inner text matching this string or regex will be returned.
        If a string is given, simple case-insensitive match will be performed.
        Defaults to ``None`` where all tables found will be returned.

        The highest level table is returned if any of its descendant tables
        match. Unless attributes filtering is also used, the highest level
        table will always be the root-level table.

    attrs : dict, optional
        Tables with attributes that match all of the `attrs` will be returned.
        Descendant tables will be included if an ancestor table is a match.
        Defaults to ``None`` where all tables found will be returned.

        Attributes are not checked for validity. To match an HTML attribute
        that has no value, set the attribute key's value to ``None``.

    encoding : str, optional
        Applicable for URL and Path sources where the resource will be
        interpreted according to this encoding. Defaults to ``'utf-8'``.

    displayed_only : bool, default True
        Whether elements with "display: none" should be parsed.

    extract_links : {{None, "thead", "tbody", "tfoot", "all"}}, optional
        Table elements with <a> tags in the specified row groups will be
        extracted. If a link is found in a row group where this is active,
        then a `TLink` will be created instead of a `TText`.
        
        Defaults to ``'all'`` where links are always extracted.

    request_headers: dict, optional
        Applicable for URL source only. The specified request headers will be
        passed in while making the request.

    Returns
    -------
    tables
        A list of ``Table`` objects.

    Raises
    ------
    IOError
        When failing to retrieve a URL or Path resource.
    """
    if isinstance(html_source, Path):
        html_text = _read_file(html_source, encoding)
    elif _is_http_url(html_source):
        html_text = _request_http(html_source, encoding, request_headers)
    else:
        html_text = html_source
    return _parse_html_text(html_text, match, attrs, displayed_only, extract_links)
