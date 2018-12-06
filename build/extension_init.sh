#!/bin/sh
jupyter nbextension install scheduler --user --py 
jupyter nbextension enable scheduler --user --py
jupyter serverextension enable scheduler --py --user 

jupyter nbextension install github --user --py
jupyter nbextension enable github --user --py
jupyter serverextension enable github --py --user
