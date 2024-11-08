import re

NAMED_CAPTURING_GROUP_START = r"^(?:\(\?P<\w+>|\(\?'\w+'|\(\?<\w+>)"

REGEX_QUOTE = r"\\Q.*?\\E"
OCTAL_ESCAPE = r"\\\d{3}"


def remove_quotes_and_octal_escapes(regex):
    regex = re.sub(REGEX_QUOTE, "", regex)
    regex = re.sub(OCTAL_ESCAPE, "", regex)
    assert re.match(REGEX_QUOTE, regex) is None
    assert re.match(OCTAL_ESCAPE, regex) is None
    return regex


def get_backreferences(regex):
    assert re.match(REGEX_QUOTE, regex) is None
    assert re.match(OCTAL_ESCAPE, regex) is None
    backref = r"\\[1-9]"
    for match in re.finditer(backref, regex):
        if match:
            yield match.group(0)


def get_groups(regex) -> list[str]:
    assert re.match(REGEX_QUOTE, regex) is None
    assert re.match(OCTAL_ESCAPE, regex) is None
    j = 0
    groups = []
    start_indices = []
    is_capturing = []
    while j < len(regex):
        c = regex[j]
        if c == "\\":
            j += 2  # Skip the next character
            continue
        elif c == "[":
            j += 1
            while j < len(regex) and regex[j] != "]":
                if regex[j] == "\\":
                    j += 2
                    continue
                j += 1
        elif c == "(":
            start_indices.append(j)
            if j + 1 >= len(regex):
                raise ValueError(
                    f"Unmatched opening parenthesis @ {j} in regex[:{j+1}]={regex[:j+1]}"
                )
            is_capturing.append(
                regex[j + 1] != "?"
                or re.match(NAMED_CAPTURING_GROUP_START, regex[j:]) is not None
            )
        elif c == ")":
            try:
                group_start = start_indices.pop()
                is_capture_group = is_capturing.pop()
                if is_capture_group:
                    groups.append(regex[group_start : j + 1])
            except IndexError:
                raise ValueError(
                    f"Unmatched closing parenthesis @ {j} in regex[:{j+1}]={regex[:j+1]}"
                )
        j += 1
    if len(start_indices) > 0:
        raise ValueError(
            f"Unmatched opening parenthesis @ {start_indices[-1]} in regex={regex}"
        )
    return groups


def validate_backreferences(backrefs, groups, regex):
    for backref in backrefs:
        group_index = int(str(backref)[1:])
        if group_index - 1 >= len(groups):
            raise ValueError(
                f"Backreference {backref} in regex {regex} refers to non-existent group {group_index}"
            )


def main(file_path):
    reject_file = open("rejected_regexps.txt", "w")
    with open(file_path, "r", newline="") as tsvfile:
        for line in tsvfile.readlines():
            row = line.split("\t")
            regex = row[0]
            if "\n" in regex:
                continue
            preprocessed_regex = remove_quotes_and_octal_escapes(regex)
            backrefs = list(get_backreferences(preprocessed_regex))
            if len(backrefs) == 0:
                reject_file.write(f"{regex}\tNo backreferences found\n")
                continue
            try:
                groups = get_groups(preprocessed_regex)
                validate_backreferences(backrefs, groups, regex)
            except ValueError as e:
                reject_file.write(f"{regex}\t{e}\n")
                continue

            print(
                line.strip(),
                " ".join(str(backref) for backref in backrefs),
                " ".join(groups),
                sep="\t",
            )
    reject_file.close()


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
