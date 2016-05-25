# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\util\util.py


def calculate_score_bar_length(experience, total_xp_needed_for_current_rank, total_xp_needed_for_next_rank, max_score_bar_length):
    xp_available_for_next_rank = float(experience - total_xp_needed_for_current_rank)
    xp_needed_for_next_rank = float(total_xp_needed_for_next_rank - total_xp_needed_for_current_rank)
    tol = 0.001
    if xp_needed_for_next_rank < tol:
        ratio = 1
    else:
        ratio = xp_available_for_next_rank / xp_needed_for_next_rank
    length = ratio * max_score_bar_length
    if length > max_score_bar_length:
        length = max_score_bar_length
    return length