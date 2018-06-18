import re
import unittest

import six
import pymarc


class MARCReaderFileTest(unittest.TestCase):
    """
    Tests for the pymarc.MARCReader class which provides iterator
    based access to a MARC file.
    """

    @classmethod
    def setUpClass(cls):
        cls.seen = 0
        cls.fh = open('test/test.dat', 'rb')

    @classmethod
    def tearDownClass(cls):
        cls.fh.close()

    def setUp(self):
        self.seen = 0
        self.fh = open('test/test.dat', 'rb')
        self.reader = pymarc.MARCReader(self.fh)

    def tearDown(self):
        self.fh.close()
        if self.reader:
            self.reader.close()

    def count(self, record):
        self.seen += 1

    def test_iterator(self):
        count = 0
        for record in self.reader:
            count += 1
        self.assertEqual(count, 10, 'found expected number of MARC21 records')

    def test_map_records(self):
        with open('test/test.dat', 'rb') as fh:
            pymarc.map_records(self.count, fh)
            self.assertEqual(self.seen, 10, 'map_records appears to work')

    def test_multi_map_records(self):
        fh1 = open('test/test.dat', 'rb')
        fh2 = open('test/test.dat', 'rb')
        pymarc.map_records(self.count, fh1, fh2)
        self.assertEqual(self.seen, 20, 'map_records appears to work')
        fh1.close()
        fh2.close()

    def test_string(self):
        ## basic test of stringification
        starts_with_leader = re.compile('^=LDR')
        has_numeric_tag = re.compile('\n=\d\d\d ')
        for record in self.reader:
            text = str(record)
            self.assertTrue(starts_with_leader.search(text), 'got leader')
            self.assertTrue(has_numeric_tag.search(text), 'got a tag')

    def disabled_test_codecs(self):
        import codecs
        with codecs.open('test/test.dat', encoding='utf-8') as fh:
            reader = pymarc.MARCReader(fh)
            record = next(reader)
            self.assertEqual(record['245']['a'], u'ActivePerl with ASP and ADO /')

    def test_bad_indicator(self):
        with open('test/bad_indicator.dat', 'rb') as fh:
            reader = pymarc.MARCReader(fh)
            record = next(reader)
            self.assertEqual(record['245']['a'], 'Aristocrats of color :')

    def test_regression_45(self):
        # https://github.com/edsu/pymarc/issues/45
        with open('test/regression45.dat', 'rb') as fh:
            reader = pymarc.MARCReader(fh)
            record = next(reader)
            self.assertEqual(record['752']['a'], 'Russian Federation')
            self.assertEqual(record['752']['b'], 'Kostroma Oblast')
            self.assertEqual(record['752']['d'], 'Kostroma')


class MARCReaderStringTest(MARCReaderFileTest):

    # Inherit tests from MARCReaderFileTest

    def setUp(self):
        with open('test/test.dat') as fh:
            raw = fh.read()

        self.reader = pymarc.reader.MARCReader(six.b(raw))


def suite():
    file_suite = unittest.makeSuite(MARCReaderFileTest, 'test')
    string_suite = unittest.makeSuite(MARCReaderStringTest, 'test')
    test_suite = unittest.TestSuite((file_suite, string_suite))
    return test_suite

if __name__ == '__main__':
    unittest.main()
