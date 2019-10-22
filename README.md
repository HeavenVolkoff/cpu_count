# cpu_count

[![project_badge](https://img.shields.io/badge/HeavenVolkoff/cpu__count-black.svg?style=for-the-badge&logo=github "Project Badge")](https://github.com/HeavenVolkoff/cpu_count)
[![version_badge](https://img.shields.io/pypi/v/cpu_count?label=version&style=for-the-badge "Version Badge")](https://pypi.org/project/cpu-count/)
[![python_version](https://img.shields.io/pypi/pyversions/cpu_count?style=for-the-badge "Python Version")](https://pypi.org/project/cpu-count/)
[![license_badge](https://img.shields.io/github/license/HeavenVolkoff/cpu_count.svg?style=for-the-badge "License Badge")](https://opensource.org/licenses/BSD-3-Clause)

Modified version of python's `cpu_count` that takes into account system
constraints to calculate the number of available CPUs

## Motivation

The Python standard library offers an implementation of cpu_count that returns
the real number of CPUs even when they are not actually available to be used by
the python process (due to constraints such as CPU affinity or CPU scheduler
configurations). This is the preferred behaviour for most applications. However,
when the interest is the amount of CPUs available for data processing, that
approach could be misleading. Especially when it is used behind the scenes such
as by the `concurrent.futures.Executor` when defining its defaults.

The purpose of this module is to provide this functionality in an API equal to
the standard implementation. By taking into account the described constraints,
this implementation attempts to return the amount of usable CPUs that are
available. If no constraint is identified the result will be the same as the
standard implementation.

## How to install

```
pip install cpu_count
```

## How to use
### As an external module
This is the standard way. Just import and call `cpu_count`

```python
from cpu_count import cpu_count

print(cpu_count())
# $> 8
```

### Monkey-patch standard lib
This an alternative way that replaces python's standard `cpu_count` with the
one from this module (Affected internal modules are `posix`, `os` and
`multiprocessing`). The advantage of this approach is not needing to port any
code, just import and call `setup_monkey_patch` ate the begin of your
application and everything will just work™.

_Note: This will also have implications in the behaviour of standard libraries
that use this function_

```python
import os
from cpu_count.monkey_patch import setup_monkey_patch

print(os.cpu_count())
# $> 12

setup_monkey_patch()

print(os.cpu_count())
# $> 8
```

#### Limitation
This approach has one limitation: it can't replace previous code that
imported the standard implementation using `from os import cpu_count`.

```python
from os import cpu_count
from cpu_count.monkey_patch import setup_monkey_patch

print(cpu_count())
# $> 12

setup_monkey_patch()

print(cpu_count())
# $> 12
```

### System wide monkey-patch
This approach also replaces python's standard `cpu_count`. However instead of
calling this module's `setup_monkey_patch` in your application code, it will be
called at python startup. For this to work you need to create a file called
`cpu_count_monkey_patch.pth` at your python's global or local site-package's
folder with the following content:

```python
import cpu_count; cpu_count.monkey_patch.setup_monkey_patch()
```

_NOTE: This approach is specially useful when creating container images of
python applications. An example of using this on a Dockerfile can be found
[here](tests/docker/Dockerfile)_

## TODO
- [ ] Add logic for Realtime Scheduler constraint
- [ ] Create unit tests

## Contributions
All contributions are very welcome.

Code styles is defined in the [Editorconfig](.editorconfig) file. Besides that
I use black and isort for auto-format, their configurations are defined in the
[Editorconfig](.editorconfig) and the [black.toml](black.toml) files
respectively.

## License
BSD 3-Clause “New” or “Revised” License

See [LICENSE](./LICENSE)
