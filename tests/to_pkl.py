#!/usr/bin/env python3

r"""
save elem from panflute.run_filter
"""

import panflute
import pickle


def action(elem, doc):
    with open('tests/grid_tables.pkl', 'wb') as file:
        pickle.dump(elem, file)


if __name__ == '__main__':
    panflute.run_filter(action)
