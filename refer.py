"""
Parser for REFER databases.
"""

import sys
import re

_code_re = re.compile(r'^%([A-Za-z0-9*^])\s+')

def refer_records(input):
    record = {}
    cur_code = None
    cur_entry_lines = []
    for line in input:
        if line[-1] == '\n':
            line = line[:-1]
        if line == '':
            # blank line - emit our record and reset for the next record
            if cur_code is not None:
                if cur_code not in record:
                    record[cur_code] = []
                record[cur_code].append(' '.join(cur_entry_lines))
            yield record
            record = {}
            cur_code = None
            cur_entry_lines = []
        else:
            m = _code_re.match(line)
            if m:
                # we have a new line
                if cur_code is not None:
                    if cur_code not in record:
                        record[cur_code] = []
                    record[cur_code].append(' '.join(cur_entry_lines))
                cur_code = m.group(1).upper()
                cur_entry_lines = [line[m.end():]]
            else:
                if cur_code is None:
                    print >>sys.stderr, "invalid line:", line
                else:
                    cur_entry_lines.append(line)
    if record:
        yield record

def dedup(lst):
    seen = set()
    result = []
    for x in lst:
        if x not in seen:
            result.append(x)
            seen.add(x)
    return result