#!/usr/bin/env python
"""
Usage:  rapture.py sql [options] <input>
        rapture.py qtree [options] <input>
        rapture.py pdf [options] <input>
        rapture.py seq [options] <input>
        rapture.py repl

Options:
  -h --help                             Show this screen.
  -c <config> --config-file <config>    Specifies a json formatted config file.
  -s <schema> --schema-file <schema>    Specifies a schema file for the query.
"""
import json
import os

from docopt import docopt

from rapt import Rapt

from latex import qtree_to_pdf
from repl import RaptureREPL


def to_sql(instance, instring, schema):
    return '; '.join(instance.to_sql(instring, schema, True))


def to_qtree(instance, instring, schema):
    return ''.join(instance.to_qtree(instring, schema))


def to_sequence(instance, instring, schema):
    return '; '.join(
        [sql for statement in instance.to_sql_sequence(instring, schema) for sql
         in statement])


def to_repl(rapt, schema, config):
    RaptureREPL(rapt, schema, config).cmdloop()


def execute(arguments):
    # Setup the configuration file.
    config = arguments.get('--config-file', None) or os.path.join(
        'example', 'config.json')
    with open(config) as config_file:
        config = json.load(config_file)

    # Setup the schema.
    schema = arguments.get('--schema-file', None) or os.path.join(
        'example', 'schema.json')
    with open(schema) as schema_file:
        schema = json.load(schema_file)

    # Get the input string.
    ra_string = arguments.get('<input>')
    rapt_instance = Rapt(**config)

    try:
        if arguments.get('sql'):
            print(to_sql(rapt_instance, ra_string, schema))
        elif arguments.get('qtree'):
            print(to_qtree(rapt_instance, ra_string, schema))
        elif arguments.get('pdf'):
            qtree = to_qtree(rapt_instance, ra_string, schema)
            qtree_to_pdf(qtree)
            print(qtree)
        elif arguments.get('seq'):
            print(to_sequence(rapt_instance, ra_string, schema))
        elif arguments.get('repl'):
            print(to_repl(rapt_instance, schema, config))
    except Exception as err:
        print('Error: {}'.format(err))


def main():
    execute(docopt(__doc__))


if __name__ == '__main__':
    main()
