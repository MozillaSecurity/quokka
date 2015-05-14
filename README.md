Quokka
======

<h3>Requirements</h3>
---
None


<h3>Basic Usage Examples</h3>
---
Launch an application with a plugin class and plugin configuration.
```
./quokka.py -plugin configs/firefox.json
```

It is possible to declare **@macros@** in the configuration files and define those over the command-line.

```
./quokka.py -plugin configs/firefox.json -conf-vars params=/srv/fuzzers/dharma/grammars/var/index.html
```

To find out wheather or which macros are declared in a configuration file you can run the following command.
```
./quokka.py -list-conf-vars -plugin configs/firefox.json
[Quokka] 2015-05-14 18:49:44 INFO: List of available configuration variables:
[Quokka] 2015-05-14 18:49:44 INFO: 	'params'
```

You can use a dot-notation of keys to access and edit nested configuration values.
```
./quokka.py -plugin configs/firefox.json -conf-vars params=google.com -conf-args environ.ASAN_OPTIONS.strict_init_order=1
```

Quokka comes with a command.json configuration, in order execute simple programs which do not need complex setup routines.

```
./quokka.py -plugin configs/command.json -conf-args plugin.kargs.binary=/sbin/ping plugin.kargs.params="-c 10 google.com"
```

<h3>Configurations</h3>
---

There are two types of configurations. The main Quokka configuration and a plugin configuration. The Quokka configuration is the main configuration which is used to define default values.

Example: quokka.conf

```
{
  "environ": {
    "ASAN_OPTIONS": {},
    "ASAN_SYMBOLIZE": "/srv/repos/llvm/r233758/build/bin/llvm-symbolizer"
  },
  "loggers": [
    {
      "class": "filesystem.FileLogger",
      "kargs": {
        "path": "/srv/logs"
      }
    }
  ],
  "monitors": [
    {
      "class": "console.ConsoleMonitor",
      "kargs": {},
      "listeners": [
        {
          "class": "sanitizer.ASanListener",
          "kargs": {}
        },
        {
          "class": "testcase.TestcaseListener",
          "kargs": {}
        }
      ]
    }
  ]
}
```

Example: plugin.conf

```
{
  "plugin": {
    "class": "command.ConsoleApplication",
    "kargs": {
      "binary": "",
      "params": ""
    }
  }
}
```



<h3>Help Menu</h3>
---
```
usage: ./quokka.py -plugin file [-quokka file] [-conf-args k=v [k=v ...]]
                   [-conf-vars k=v [k=v ...]] [-list-conf-vars]
                   [-verbosity {1..5}]

Quokka Runtime

Mandatory Arguments:
  -plugin file          Run an application. (default: None)

Optional Arguments:
  -quokka file          Quokka configuration (default: configs/quokka.json)
  -conf-args k=v [k=v ...]
                        Add/edit configuration properties. (default: None)
  -conf-vars k=v [k=v ...]
                        Subsitute configuration variables. (default: None)
  -list-conf-vars       List used configuration variables. (default: False)
  -verbosity {1..5}     Level of verbosity for logging module. (default: 2)

The exit status is 0 for non-failures and 1 for failures.
```