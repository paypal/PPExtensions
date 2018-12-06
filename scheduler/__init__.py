"""Package sparkmonitor

This package contains two modules:
    kernelextension.py is the Jupyter kernel extension.
    serverextension.py is the Jupyter web server extension.
"""

def _jupyter_nbextension_paths():
    """Used by 'jupyter nbextension' command to install frontend extension"""
    return [dict(
        section="tree",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="scheduler",
        # _also_ in the `nbextension/` namespace
        require="scheduler/scheduler"),
           dict(
        section="tree",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="scheduler",
        # _also_ in the `nbextension/` namespace
        require="scheduler/schedulermain")  
        ]


def _jupyter_server_extension_paths():
    """Used by "jupyter serverextension" command to install web server extension'"""
    return [{
        "module": "scheduler.scheduler"
    }]
