import cmd
import logging
import shlex
import subprocess

from latex import qtree_to_pdf

logger = logging.getLogger(__name__)


class RaptureREPL(cmd.Cmd):
    intro = 'Welcome to the Rapture REPL.\n\n' \
            'The REPL uses Rapt to translate and execute relational \n' \
            'algebra statements on a database.\n\n' \
            'Type help or ? to list commands.\n'
    prompt = 'π '
    ruler = '-'
    doc_header = 'Available Commands (type help <command> for more details):'

    def __init__(self, rapt, schema, config, completekey='tab', stdin=None,
                 stdout=None):
        """
        :type rapt: rapt.Rapt
        :type schema: dict
        """
        super().__init__(completekey, stdin, stdout)
        self.rapt = rapt
        self.schema = schema
        self.config = config
        self.previous = None
        self._syntax = None

    @property
    def syntax(self):
        if self._syntax is None:
            self._syntax = []
            for key, value in self.config['syntax'].items():
                self._syntax.append(
                    (key.replace('_op', '').replace('_', ' ').title(), value))
            self._syntax.sort()
        return self._syntax

    def preloop(self):
        subprocess.call('clear')
        super().preloop()

    def default(self, line):
        try:
            self.previous = line
            statement = ';'.join(self.rapt.to_sql(line, self.schema, True))
            subprocess.call(('psql', '-c', statement))
            print('\nSQL: {}\n'.format(statement))
        except Exception as err:
            logger.error('Error: {}'.format(err))

    def do_draw(self, line):
        """
        Draw the syntax tree of the most recently executed relational algebra
        statement.

        Requires pdflatex.

        The files created during the pdf generation process are prefixed with
        'out' (e.g. out.pdf). Optionally, a filename (without extension) can
        be provided instead.

        Usage:  draw [filename]
        """
        if self.previous is not None:
            args = shlex.split(line)
            if len(args) == 1:
                qtree = ''.join(self.rapt.to_qtree(self.previous, self.schema))
                qtree_to_pdf(qtree, args[0])

    def do_EOF(self, line):
        """
        Exit the Rapture.
        """
        return True

    def do_help(self, arg):
        """
        List available commands with "help" or detailed help with "help cmd".
        """
        super().do_help(arg)

    def help_syntax(self):
        width = max([len(name) for name, _ in self.syntax]) + 2
        print('\nRapt Syntax\n')
        for name, operator in self.syntax:
            print('{name:{width}}\t{operator}'.format(name=name, width=width,
                                                      operator=operator))
        print()

    def emptyline(self):
        pass


if __name__ == '__main__':
    import os.path
    import json

    from rapt import Rapt

    # Define the grammar and syntax.
    _config = os.path.join('example', 'config.json')
    with open(_config) as config_file:
        _config = json.load(config_file)

    # Setup the schema.
    _schema = os.path.join('example', 'schema.json')
    with open(_schema) as schema_file:
        _schema = json.load(schema_file)

    # Start the REPL.
    rapt_instance = Rapt(**_config)
    RaptureREPL(rapt_instance, _schema, _config).cmdloop()
