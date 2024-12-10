def levenshtein_distance_ignore_word_order(str1, str2):
    # Split the strings into words
    words1 = str1.split()
    words2 = str2.split()

    # Sort the words
    sorted_words1 = "".join(sorted(words1))
    sorted_words2 = "".join(sorted(words2))

    # Calculate Levenshtein distance
    return levenshtein_distance(sorted_words1, sorted_words2)


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # len(s1) >= len(s2)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
