"""hug/directives.py

Defines the directives built into hug. Directives allow attaching behaviour to an API handler based simply
on an argument it takes and that arguments default value. The directive gets called with the default supplied,
ther request data, and api_version. The result of running the directive method is then set as the argument value.
Directive attributes are always prefixed with 'hug_'

Copyright (C) 2015  Timothy Edmund Crosley

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

"""
from functools import partial
from timeit import default_timer as python_timer


class Timer(object):
    '''Keeps track of time surpased since instanciation, outputed by doing float(instance)'''
    __slots__ = ('start', 'round_to')

    def __init__(self, round_to=None, **kwargs):
        self.start = python_timer()
        self.round_to = round_to

    def __float__(self):
        return round(self.start, self.round_to) if self.round_to else self.start

    def __int__(self):
        return int(round(float(self)))

    def __json__(self):
        return self.__float__()


def module(default=None, module=None, **kwargs):
    '''Returns the module that is running this hug API function'''
    return module if module else default


def api(default=None, module=None, **kwargs):
    '''Returns the api instance in which this API function is being ran'''
    return getattr(module, '__hug__', default)


def api_version(default=None, api_version=None, **kwargs):
    '''Returns the current api_version as a directive for use in both request and not request handling code'''
    return api_version


class CurrentAPI(object):
    '''Returns quick access to all api functions on the current version of the api'''
    __slots__ = ('api_version', 'api')

    def __init__(self, default=None, api_version=None, **kwargs):
        self.api_version = api_version
        self.api = api(**kwargs)

    def __getattr__(self, name):
        function = self.api.versioned.get(self.api_version, {}).get(name, None)
        if not function:
            function = self.api.versioned.get(None, {}).get(name, None)
        if not function:
            raise AttributeError('API Function {0} not found'.format(name))

        accepts = function.interface.api_function.__code__.co_varnames
        if 'hug_api_version' in accepts:
            function = partial(function, hug_api_version=self.api_version)
        if 'hug_current_api' in accepts:
            function = partial(function, hug_current_api=self)

        return function
