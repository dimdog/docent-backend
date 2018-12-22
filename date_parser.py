import unittest


class TestDateParsers(unittest.TestCase):

    def test_rijks_date_parser(self):
        sample_lines = [
            ("in or before 1900", (1900, None)),
            ("c. 1622 - c. 1629", (1622, 1629)),
            ("1879", (1879, None)),
            ("c. 1615 - c. 1635", (1615, 1635)),
            ("1690 - 1710", (1690, 1710))]

        for row in sample_lines:
            self.assertEqual(rijks_date_parser(row[0]), row[1])


def fallback_parser(splits):
    before_date = None
    after_date = None
    for split in splits:
        try:
            a = int(split)
            if not before_date:
                before_date = a
            else:
                after_date = a
        except:
            pass
    return before_date, after_date


def rijks_date_parser(instring):
    before_date = None
    after_date = None
    splits = instring.split(" ")
    try:
        if len(splits) == 1:  # "1879"
            before_date = int(splits[0])
        elif len(splits) == 3:  # "1690 - 1710"
            before_date = int(splits[0])
            after_date = int(splits[2])
        elif len(splits) == 5:  # "c. 1615 - c. 1635"
            before_date = int(splits[1])
            after_date = int(splits[4])
        else:
            before_date, after_date = fallback_parser(splits)
    except:
        before_date, after_date = fallback_parser(splits)


    return before_date, after_date


if __name__ == '__main__':
    unittest.main()
