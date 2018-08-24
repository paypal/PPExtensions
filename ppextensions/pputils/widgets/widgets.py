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

"""IPyWidgets for PPExtensions."""

import qgrid

from time import sleep

from ipywidgets import Box
from ipywidgets import widgets
from pyhive.exc import DatabaseError
from IPython.display import display


class MenuWidgets(Box):
    """
        Widget to drive user driven parameters.
    """

    def __init__(self):
        super(MenuWidgets, self).__init__()
        # Change layout settings.
        self.layout.flex_flow = 'row'
        self.layout.display = 'flex'
        self.layout.align_items = 'stretch'
        self.layout.overflow_x = 'scroll'
        self.style = {'description_width': 'initial'}
        self.children = []


class StatusBar(MenuWidgets):
    """
        Widget to drive user driven parameters.
    """

    def __init__(self):
        super(StatusBar, self).__init__()
        self.children = [
            widgets.FloatProgress(
                value=0,
                min=0,
                max=100.0,
                step=0.1,
                description='Status:',
                bar_style='info',
                orientation='horizontal',
                style=self.style,
            ),
            widgets.HTML(
                value='<font color="blue"></front>',
                description='',
                style=self.style,
            )]
        self.layout.visibility = 'visible'
        display(self)

    def update_max(self, splits):
        """
            Update Max.
        """
        self.children[0].max = splits

    def update_description(self, description):
        """
            Update Description.
        """
        self.children[0].description = description

    def update_status(self, splits):
        """
            Update Status.
        """
        self.children[0].value = splits

    def update_info_message(self, status):
        """
            Update Info Messages.
        """
        self.children[1].value = '<font color="blue">%s</front>' % str(status)

    def update_status_error(self, message):
        """
            Update Status.
        """
        self.children[0].bar_style = 'danger'
        self.children[1].value = '<font color="red">%s</front>' % str(message)

    def update_status_success(self, message):
        """
            Update Status.
        """
        self.children[0].value = self.children[0].max
        self.children[0].bar_style = 'success'
        self.children[1].value = '<font color="green">%s</front>' % str(message)


class ParameterBox(MenuWidgets):
    """
        Widget to drive user driven parameters.
    """

    def __init__(self):
        super(ParameterBox, self).__init__()

    def display(self):
        """
            Display Widget.
        """
        display(self)

    def add_child(self, child):
        """
            Add Child.
        """
        self.children = self.children + (child,)


class PrestoStatusBar(StatusBar):
    """
        Progress Bar for Presto.
    """

    def __init__(self, cursor):
        super(PrestoStatusBar, self).__init__()
        self.run(cursor)

    def run(self, cursor):
        """
            Update Status bar.
        """

        # Don't use recursion here. The query might run for hours and tail-rec optimization is not supported in Python.
        if cursor:
            status = 'RUNNING'
            total_tasks = 100
            completed_tasks = 0
            try:
                while status.upper() == 'RUNNING':
                    sleep(1)
                    data = cursor.poll()
                    if data and 'stats' in data and 'state' in data['stats']:
                        status = data['stats']['state']
                        if 'completedSplits' in data['stats'] and completed_tasks != data['stats']['completedSplits']:
                            completed_tasks = data['stats']['completedSplits']
                            self.update_status(completed_tasks)
                        if 'totalSplits' in data['stats'] and total_tasks != data['stats']['totalSplits']:
                            total_tasks = data['stats']['totalSplits']
                            self.update_max(total_tasks)
                        self.update_info_message("%s - %d/%d tasks completed" % (status, completed_tasks, total_tasks))
                    else:
                        # TODO:  Need to handle better way.
                        return
                if status.upper() == 'FINISHED':
                    self.update_status_success('Execution Completed.')
            except DatabaseError as error:
                self.update_status_error("Unable to execute query. Please check logs below.")
                raise error


class HorizontalBox(widgets.HBox):
    """
        Widgets layout in HorizontalBox.
    """

    def __init__(self, children, data=None):
        super().__init__(children)
        self.data = data

    def DataFrame(self):
        """
            Return widget data as DataFrame.
        """
        return self.data


class VerticalBox(widgets.VBox):
    """
        Widgets layout in VerticalBox.
    """

    def __init__(self, children, data=None):
        super().__init__(children)
        self.data = data

    def DataFrame(self):
        """
            Return widget data as DataFrame.
        """
        return self.data

    def csv(self, filename=None):
        """
            Return widget data as DataFrame.
        """
        if filename is not None:
            self.data.to_csv(filename)


class TabView(widgets.Tab):
    """
        Widget to Manage Tab Layout.
    """

    def __init__(self, children, data):
        super().__init__(children)
        self.data = data
        for i in range(len(data)):
            self.set_title(i, 'Result Set ' + str(i))

    def DataFrame(self, idx=-1):
        """
            Return widget data as DataFrame.
            idx : Int Tab Index
            :return DataFrame
        """
        return self.data[idx]

    def csv(self, filename=None, idx=-1):
        """
            Return widget data as CSV.
            idx : Int Tab Index
            :return CSV
        """
        if filename is not None:
            self.data[idx].to_csv(filename)


class QGridCustomWidget(qgrid.QGridWidget):
    """
        Widget to render as QGrid.
    """

    def __init__(self, dataframe, display_limit=1000, grid_options=None):
        self.full_df = dataframe

        if grid_options is None:
            grid_options = {
                'fullWidthRows': True,
                'syncColumnCellResize': True,
                'forceFitColumns': False,
                'defaultColumnWidth': 150,
                'rowHeight': 35,
                'enableColumnReorder': True,
                'enableTextSelectionOnCells': True,
                'editable': True,
                'autoEdit': False,
                'explicitInitialization': True,
                'maxVisibleRows': 10,
                'minVisibleRows': 0,
                'maxVisibleColumns': 10,
                'minVisibleColumns': 0,
                'sortable': True,
                'filterable': True,
                'highlightSelectedCell': True,
                'highlightSelectedRow': True
            }

        super().__init__(df=self.full_df[:display_limit], grid_options=grid_options)

    def DataFrame(self):
        """
            Return widget data as DataFrame.
        """
        return self.full_df

    def csv(self, filename=None):
        """
            Return widget data as CSV.
        """
        if filename is not None:
            self.full_df.to_csv(filename)
