#!/usr/bin/env python3

desc = '''Generate statistics about optimization records from the YAML files
generated with -fsave-optimization-record and -fdiagnostics-show-hotness.

The tools requires PyYAML and Pygments Python packages.'''

import optrecord
import argparse
import operator
from collections import defaultdict

try:
    from guppy import hpy
    hp = hpy()
except ImportError:
    print("Memory consumption not shown because guppy is not installed")
    hp = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        'yaml_dirs_or_files',
        nargs='+',
        help='List of optimization record files or directories searched '
             'for optimization record files.')
    parser.add_argument(
        '--jobs',
        '-j',
        default=None,
        type=int,
        help='Max job count (defaults to %(default)s, the current CPU count)')
    args = parser.parse_args()

    files = optrecord.find_opt_files(*args.yaml_dirs_or_files)
    if not files:
        parser.error("No *.opt.yaml files found")
        sys.exit(1)

    all_remarks, file_remarks, _ = optrecord.gather_results(
        files, args.jobs)
    print('\n')

    bypass = defaultdict(int)
    byname = defaultdict(int)
    for r in optrecord.itervalues(all_remarks):
        bypass[r.Pass] += 1
        byname[r.Pass + "/" + r.Name] += 1

    total = len(all_remarks)
    print("{:24s} {:10d}".format("Total number of remarks", total))
    if hp:
        h = hp.heap()
        print("{:24s} {:10d}".format("Memory per remark",
                                     h.size / len(all_remarks)))
    print('\n')

    print("Top 10 remarks by pass:")
    for (passname, count) in sorted(bypass.items(), key=operator.itemgetter(1),
                                    reverse=True)[:10]:
        print("  {:30s} {:2.0f}%". format(passname, count * 100. / total))

    print("\nTop 10 remarks:")
    for (name, count) in sorted(byname.items(), key=operator.itemgetter(1),
                                reverse=True)[:10]:
        print("  {:30s} {:2.0f}%". format(name, count * 100. / total))
