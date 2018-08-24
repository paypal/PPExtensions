"""Copyright (c) 2018, PayPal Inc.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

"""Wrapper for all results from queries."""

import operator
import prettytable
import re
import six

from sql.column_guesser import ColumnGuesserMixin
from sql.run import CsvResultDescriptor, UnicodeWriter
from functools import reduce


class ResultSet(list, ColumnGuesserMixin):
    """
    Results of SQL outputs.

    Credits: Thanks to 'Ipython-sql' for ResultSet.
    """

    def __init__(self, columns, data, displaylimit=100):
        self.keys = columns
        self.displaylimit = displaylimit
        self.field_names = unduplicate_field_names(self.keys)
        self.pretty = prettytable.PrettyTable(self.field_names)
        self.style = prettytable.__dict__["DEFAULT"]
        list.__init__(self, data)
        self.data = data
        for row in self[:self.displaylimit or None]:
            self.pretty.add_row(row)

    def __getitem__(self, key):
        """
        Access by integer (row position within result set)
        or by string (value of leftmost column)
        """
        try:
            return list.__getitem__(self, key)
        except TypeError:
            result = [row for row in self if row[0] == key]
            if not result:
                raise KeyError(key)
            if len(result) > 1:
                raise KeyError('%d results for "%s"' % (len(result), key))
            return result[0]

    def _repr_html_(self):
        _cell_with_spaces_pattern = re.compile(r'(<td>)( {2,})')
        if self.pretty:
            result = self.pretty.get_html_string()
            result = _cell_with_spaces_pattern.sub(_nonbreaking_spaces, result)
            if self.displaylimit and len(self) > self.displaylimit:
                result = '%s\n<span style="font-style:italic;text-align:center;">%d rows, truncated to displaylimit of %d</span>' % (
                    result, len(self), self.displaylimit)
            return result
        else:
            return None

    def __str__(self, *arg, **kwarg):
        return str(self.pretty or '')

    def dict(self):
        """Returns a dict built from the result set, with column names as keys"""
        return dict(zip(self.keys, zip(*self)))

    def DataFrame(self):
        """Returns a Pandas DataFrame instance built from the result set."""
        import pandas as pd
        frame = pd.DataFrame(self.data, columns=(self and self.keys) or [])
        return frame

    def pie(self, key_word_sep=" ", title=None, **kwargs):
        """Generates a pylab pie chart from the result set.
        ``matplotlib`` must be installed, and in an
        IPython Notebook, inlining must be on::
            %%matplotlib inline
        Values (pie slice sizes) are taken from the
        rightmost column (numerical values required).
        All other columns are used to label the pie slices.
        Parameters
        ----------
        key_word_sep: string used to separate column values
                      from each other in pie labels
        title: Plot title, defaults to name of value column
        Any additional keyword arguments will be passsed
        through to ``matplotlib.pylab.pie``.
        """
        self.guess_pie_columns(xlabel_sep=key_word_sep)
        import matplotlib.pylab as plt
        pie = plt.pie(self.ys[0], labels=self.xlabels, **kwargs)
        plt.title(title or self.ys[0].name)
        return pie

    def plot(self, title=None, **kwargs):
        """Generates a pylab plot from the result set.
        ``matplotlib`` must be installed, and in an
        IPython Notebook, inlining must be on::
            %%matplotlib inline
        The first and last columns are taken as the X and Y
        values.  Any columns between are ignored.
        Parameters
        ----------
        title: Plot title, defaults to names of Y value columns
        Any additional keyword arguments will be passsed
        through to ``matplotlib.pylab.plot``.
        """
        import matplotlib.pylab as plt
        self.guess_plot_columns()
        self.x = self.x_value or range(len(self.ys[0]))
        coords = reduce(operator.add, [(self.x, y) for y in self.ys])
        plot = plt.plot(*coords, **kwargs)
        if hasattr(self.x, 'name'):
            plt.xlabel(self.x.name)
        ylabel = ", ".join(y.name for y in self.ys)
        plt.title(title or ylabel)
        plt.ylabel(ylabel)
        return plot

    def bar(self, key_word_sep=" ", title=None, **kwargs):
        """Generates a pylab bar plot from the result set.
        ``matplotlib`` must be installed, and in an
        IPython Notebook, inlining must be on::
            %%matplotlib inline
        The last quantitative column is taken as the Y values;
        all other columns are combined to label the X axis.
        Parameters
        ----------
        title: Plot title, defaults to names of Y value columns
        key_word_sep: string used to separate column values
                      from each other in labels
        Any additional keyword arguments will be passsed
        through to ``matplotlib.pylab.bar``.
        """
        import matplotlib.pylab as plt
        self.guess_pie_columns(xlabel_sep=key_word_sep)
        plot = plt.bar(range(len(self.ys[0])), self.ys[0], **kwargs)
        if self.xlabels:
            plt.xticks(range(len(self.xlabels)), self.xlabels,
                       rotation=45)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ys[0].name)
        return plot

    def csv(self, filename=None, **format_params):
        """Generate results in comma-separated form.  Write to ``filename`` if given.
           Any other parameters will be passed on to csv.writer."""
        if not self.pretty:
            return None  # no results
        if filename:
            encoding = format_params.get('encoding', 'utf-8')
            if six.PY2:
                outfile = open(filename, 'wb')
            else:
                outfile = open(filename, 'w', newline='', encoding=encoding)
        else:
            outfile = six.StringIO()
        writer = UnicodeWriter(outfile, **format_params)
        writer.writerow(self.field_names)
        for row in self:
            writer.writerow(row)
        if filename:
            outfile.close()
            return CsvResultDescriptor(filename)
        else:
            return outfile.getvalue()


def _nonbreaking_spaces(match_obj):
    """
    Make spaces visible in HTML by replacing all `` `` with ``&nbsp;``
    Call with a ``re`` match object.  Retain group 1, replace group 2
    with nonbreaking speaces.
    """
    spaces = '&nbsp;' * len(match_obj.group(2))
    return '%s%s' % (match_obj.group(1), spaces)


def unduplicate_field_names(field_names):
    """Append a number to duplicate field names to make them unique. """
    res = []
    for k in field_names:
        if k in res:
            i = 1
            while k + '_' + str(i) in res:
                i += 1
            k += '_' + str(i)
        res.append(k)
    return res
