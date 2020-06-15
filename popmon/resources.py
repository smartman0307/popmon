# Copyright (c) 2020 ING Wholesale Banking Advanced Analytics
# This file is part of the Population Shift Monitoring package (popmon)
# Licensed under the MIT License

# Resources lookup file for popmon

import pathlib

from jinja2 import Environment, FileSystemLoader
from pkg_resources import resource_filename

import popmon

# data files that are shipped with popmon.
_DATA = dict(
    (_.name, _)
    for _ in pathlib.Path(resource_filename(popmon.__name__, "test_data")).glob("*")
)

# Tutorial notebooks
_NOTEBOOK = {
    _.name: _
    for _ in pathlib.Path(resource_filename(popmon.__name__, "notebooks")).glob(
        "*.ipynb"
    )
}

# Resource types
_RESOURCES = dict(data=_DATA, notebook=_NOTEBOOK)

# Environment for visualization templates' directory
_TEMPLATES_ENV = Environment(
    loader=FileSystemLoader(
        resource_filename(popmon.__name__, "visualization/templates")
    )
)


def _resource(resource_type, name: str) -> str:
    """Return the full path filename of a resource.

    :param str resource_type: The type of the resource.
    :param str  name: The name of the resource.
    :returns: The full path filename of the fixture data set.
    :rtype: str
    :raises FileNotFoundError: If the resource cannot be found.
    """
    full_path = _RESOURCES[resource_type].get(name, None)

    if full_path and full_path.exists():
        return str(full_path)

    raise FileNotFoundError(
        'Could not find {resource_type} "{name!s}"! Does it exist?'.format(
            resource_type=resource_type, name=name
        )
    )


def data(name: str) -> str:
    """Return the full path filename of a shipped data file.

    :param str name: The name of the data.
    :returns: The full path filename of the data.
    :rtype: str
    :raises FileNotFoundError: If the data cannot be found.
    """
    return _resource("data", name)


def notebook(name: str) -> str:
    """Return the full path filename of a tutorial notebook.

    :param str name: The name of the notebook.
    :returns: The full path filename of the notebook.
    :rtype: str
    :raises FileNotFoundError: If the notebook cannot be found.
    """
    return _resource("notebook", name)


def templates_env(filename=None, **kwargs):
    """Return visualization templates directory environment. If filename provided, the exact
    template is being retrieved and provided keyword arguments - rendered accordingly.

    :param str filename: the name of the template to get retrieved.
    :param kwargs: residual keyword arguments which would be used for rendering
    :returns: template if a filename is provided (rendered given that keyword arguemnts are provided)
              otherwise: environment of the templates directory
    """
    if filename:
        if kwargs:
            return _TEMPLATES_ENV.get_template(filename).render(**kwargs)
        else:
            return _TEMPLATES_ENV.get_template(filename)
    else:
        return _TEMPLATES_ENV
