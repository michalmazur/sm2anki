"""Command line script for sm2anki."""

import sm2anki
import sys

if len(sys.argv) == 4:
    source = sys.argv[1]
    media_directory = sys.argv[2]
    target = sys.argv[3]

    print "Reading {}.".format(source)
    elements = sm2anki.read_sm_file(open(source).read())
    converter = sm2anki.Converter(elements, media_directory)
    print "Saving {} SuperMemo elements in Anki format to {}.".format(
        len(elements), target)
    with open(target, "w") as f:
        f.write(converter.convert_all())
    print "Done."
    sys.exit(0)
else:
    args = [('source', 'full path to the SuperMemo export file'),
            ('media_directory', 'full path to the media directory of the '
                                'collection (includes the trailing slash)'),
            ('target', 'full path to the desired location of the output file')]

    arg_names = ' '.join([arg for arg, desc in args])
    arg_desc = '\n    '.join(["{0}: {1}".format(arg, desc) for arg, desc in args])

    if len(sys.argv) != 1:
        error_msg = ("Invalid number of arguments: expected {0} "
        "but received {1}.\n\n".format(len(args), len(sys.argv) - 1))
        sys.stderr.write(error_msg)

    usage = ("Usage: python convert.py {0}\n\n".format(arg_names) +
             "Arguments:\n    " + arg_desc)
    print usage
    sys.exit(1)