ALIGN_TO_LETTER = {"AlignLeft": 'L',
                   "AlignCenter": 'C',
                   "AlignRight": 'R',
                   "AlignDefault": 'D'}


LETTER_TO_ALIGN = {
    'l': "AlignLeft",
    'c': "AlignCenter",
    'r': "AlignRight",
    'd': "AlignDefault"
}


ALIGN_TO_IDXS = {
    'AlignLeft': [0],
    'AlignCenter': [0, -1],
    'AlignRight': [-1],
    'AlignDefault': []
}


ALIGN_TO_PIPE_TABLE_DELIMITER = {
    "AlignLeft": ':---',
    "AlignCenter": ':---:',
    "AlignRight": '---:',
    "AlignDefault": '---'
}
