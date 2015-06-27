#!/usr/bin/env python
import logging
import os
import platform
import subprocess

logger = logging.getLogger(__name__)

LATEX_TEMPLATE = '''
\\documentclass{{article}}\n
\\usepackage{{qtree}}\n
\\usepackage[active,tightpage]{{preview}}\n
\\usepackage{{varwidth}}\n
\\AtBeginDocument{{\\begin{{preview}}\\begin{{varwidth}}{{\\linewidth}}}}\n
\\AtEndDocument{{\\end{{varwidth}}\\end{{preview}}}}\n

\\begin{{document}}\n
{tree}\n
\\end{{document}}
'''

OS_TO_OPENER = dict(
    Darwin=lambda filename: subprocess.call(('open', filename)),
    Linux=lambda filename: subprocess.call(('xdg-open', filename))
)


def qtree_to_pdf(qtree, filename='out', tex_template=LATEX_TEMPLATE):
    """
    Insert a qtree string into a latex template, and use pdflatex to generate
    a pdf. It will try to open the generated PDF, if possible on the OS.

    :param qtree: a valid qtree string. For more details refer to
    http://www.ling.upenn.edu/advice/latex/qtree/qtreenotes.pdf
    :param filename: a prefix for the names of the generated files.
    :param tex_template: a latex template string. Expects the token '{tree}' at
    the location the qtree string is to be inserted.
    """
    tex_fp = os.path.abspath('{}.tex'.format(filename))
    with open(tex_fp, 'w') as output:
        output.write(tex_template.format(tree=qtree))

    # To create a TEX file, we need to be in the parent directory of the file.
    subprocess.call(('pdflatex', tex_fp),
                    cwd=os.path.dirname(tex_fp),
                    stdout=subprocess.DEVNULL)

    # Open the created file.
    try:
        pdf_fp = os.path.abspath('{}.pdf'.format(filename))
        retcode = OS_TO_OPENER[platform.system()](pdf_fp)
        if retcode < 0:
            raise OSError(-retcode)
    except KeyError as err:
        logger.warn('Cannot open PDF on this OS', err)
    except OSError as err:
        logger.warn('Failed to open PDF', err)
