# nlgserv

nlgserv is a simple server that accepts JSON representations of sentences and generates English sentences from those.

It uses SimpleNLG (under the [MPL 2.0 licence](https://www.mozilla.org/MPL/)) available [on github.com](https://github.com/simplenlg/simplenlg) for natural language generation.

In order to use SimpleNLG (which is implemented in Java), [Jython 2.7.0](http://www.jython.org) is also bundled, under the terms of the [PSF v.2](http://www.jython.org/license.html).

Additionally, it uses Bottle v0.12.9 (under the [MIT licence](https://github.com/defnull/bottle/blob/0.12.9/LICENSE) available [on github.com](https://github.com/defnull/bottle/tree/0.12.9) for handling HTTP requests.

> This was something I cobbled together to act as part of my PhD project.
> Consequently, I don't really have time to maintain it or fix bugs, as
> it suits the purposes I need it for.
>
> Feel free to take the code and try and fix it, but I'm afraid I can't
> really help you. If you are able to use the Java library directly,
> I'd really recommend you do that instead.
>
> Thanks,
> Darren

Build status
------------

[![Build Status](https://travis-ci.org/mnestis/nlgserv.svg?branch=master)](https://travis-ci.org/mnestis/nlgserv)
[![Latest Version](https://img.shields.io/pypi/v/nlgserv.svg)](https://pypi.python.org/pypi/nlgserv/)
