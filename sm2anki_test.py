import unittest
from sm2anki import *

class ReadSmFileTest(unittest.TestCase):
    def setUp(self):
        self.input = open('res/math.txt').read()

    def test_returns_correct_number_of_elements(self):
        elements = read_sm_file(self.input)
        self.assertEqual(len(elements), 8)

    def test_returns_dict(self):
        elements = read_sm_file(self.input)
        self.assertIsInstance(elements, dict)

    def test_returns_dict_of_elements(self):
        elements = read_sm_file(self.input)
        for v in elements.values():
            self.assertIsInstance(v, Element)

    def test_returns_dict_of_elements_indexed_by_id(self):
        elements = read_sm_file(self.input)
        self.assertEqual(elements[1].id, 1)
        self.assertEqual(elements[2].id, 2)
        self.assertEqual(elements[4].id, 4)
        self.assertEqual(elements[12].id, 12)


class ElementTest(unittest.TestCase):
    def setUp(self):
        self.topic = open('res/topic.txt').read()
        self.item = open('res/item.txt').read()

    def test_id(self):
        e = Element(self.item)
        self.assertEqual(12, e.id)

    def test_question(self):
        e = Element(self.item)
        self.assertEqual("2 * 3", e.get_question())

    def test_question_sound(self):
        e = Element(self.item)
        self.assertEqual(r'D:\SM\SYSTEMS\Math\elements\8.wma',
                         e.get_question_sound())

    def test_answer(self):
        e = Element(self.item)
        self.assertEqual("6", e.get_answer())

    def test_answer_sound(self):
        e = Element(self.item)
        self.assertEqual(r'D:\SM\SYSTEMS\Math\elements\7.wma',
                         e.get_answer_sound())

    def test_is_item(self):
        e = Element(self.item)
        self.assertTrue(e.is_item())


class ExporterTest(unittest.TestCase):
    def setUp(self):
        self.input = open('res/math.txt').read()

    def test_get_tags(self):
        elements = read_sm_file(self.input)
        c = Converter(elements, '')
        self.assertEqual(c.get_tags(elements[12]),
                         "Math Arithmetic Addition&Multiplication [1]Multiplication")

    def test_convert(self):
        elements = read_sm_file(self.input)
        c = Converter(elements, r'D:/SM/SYSTEMS/Math/elements/')
        expected = "2 * 3[sound:8.wma]	6[sound:7.wma]	Math Arithmetic Addition&Multiplication [1]Multiplication"
        actual = c.convert(elements[12])
        self.assertEqual(expected, actual)

    def test_convert_no_answer_and_no_question_sound(self):
        elements = read_sm_file(open('res/item_without_question_sound_and_answer_text.txt').read())
        c = Converter(elements, 'D:/SM/SYSTEMS/Math/elements/')
        expected = "2 * 3[sound:]	[sound:7.wma]	"
        self.assertEqual(expected, c.convert(elements[12]))

    def test_get_relative_path_to_media_file(self):
        elements = read_sm_file(self.input)
        c = Converter(elements, '')
        path_to_file = 'D:/SM/SYSTEMS/Math/elements/7.wma'
        deleted_part = 'D:/SM/SYSTEMS/Math/elements/'
        expected = '7.wma'
        actual = c.get_relative_path_to_media_file(path_to_file, deleted_part)
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()
