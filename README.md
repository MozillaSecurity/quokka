Quokka
======

<h3>Setup</h3>
```
pip install -r requirements.txt



<h3>Basic Usage Examples</h3>
Launch an application with a plugin class and plugin configuration.
```
./quokka.py -plugin configs/firefox.json
```

It is possible to use @macros@ in the configuration files and set those over the command-line.

```
./quokka.py -plugin configs/firefox.json -conf-vars params=google.com
```

Further it is possible to edit nested configuration values by using the dot-notation.

```
./quokka.py -plugin configs/firefox.json -conf-vars params=google.com -conf-args environ.ASAN_OPTIONS.strict_init_order=1
```



<h3>Help Menu</h3>
```
usage: ./quokka.py (-command str | -plugin file) [-quokka file]
                   [-conf-args k=v [k=v ...]] [-conf-vars k=v [k=v ...]]
                   [-list-conf-vars] [-verbosity {1..5}]

Quokka Runtime

Mandatory Arguments:
  -command str          Run an application. (default: None)
  -plugin file          Run an application with a setup script. (default:
                        None)

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