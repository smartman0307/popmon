# Copyright (c) 2023 ING Analytics Wholesale Banking
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
from typing import Optional


class Pipeline:
    """Base class used for to run modules in a pipeline."""

    def __init__(self, modules, logger: Optional[logging.Logger] = None):
        """Initialization of the pipeline

        :param list modules: modules of the pipeline.
        :param logger: logger to be used by each module.
        """
        self.modules = modules
        self.set_logger(logger)

    def set_logger(self, logger: Optional[logging.Logger]):
        """Set the logger to be used by each module

        :param logger: input logger
        """
        self.logger = logger or logging.getLogger()
        for module in self.modules:
            module.set_logger(self.logger)

    def add_modules(self, modules):
        """Add more modules to existing list of modules.

        :param list modules: list of more modules
        """
        if len(modules):
            self.modules.extend(modules)

    def transform(self, datastore):
        """Central function of the pipeline.

        Calls transform() of each module in the pipeline.
        Typically, transform() of a module takes something from the datastore, does something to it,
        and puts the results back into the datastore again, to be passed on to the next module in the pipeline.

        :param dict datastore: input datastore
        :return: updated output datastore
        :rtype: dict
        """

        for module in self.modules:
            self.logger.debug(f"transform {module.__class__.__name__}")
            datastore = module.transform(datastore)
        return datastore

    def __repr__(self):
        """String representation for pipeline"""
        name = self.__class__.__name__
        ret = f"{name}: [\n"
        for m in self.modules:
            ret += "\t" + str(m).replace("\n", "\n\t") + "\n"
        ret += "]"
        return ret
