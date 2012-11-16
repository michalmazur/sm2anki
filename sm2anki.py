"""This module converts SuperMemo collections to Anki."""

class Converter:

    """
    This class converts a dictionary of Element objects into a format
    that can be imported into an Anki deck.
    """

    def __init__(self, elements, path_to_media_directory):
        """
        elements:
            A dictionary of Element objects indexed by ID.

        path_to_media_directory:
            Full path to the directory that contains the
            media files for the collection, e.g.:
            c:/sm/systems/your_collection/elements/
            The path can use either slashes or backslashes
            but must include a trailing slash or backslash.
        """
        self.elements = elements
        self.full_path_to_media = path_to_media_directory

    def get_tags(self, element):
        """
        Return the tags of an element as a string.

        SuperMemo organizes elements into categories but Anki uses tags to
        organize facts. To convert, elements are tagged with the names of all
        categories they belong to in the original collection.
        """
        tags = []
        while element.properties['Parent'] != '0':
            parent_id = int(element.properties['Parent'])
            element = self.elements[parent_id]
            # Cleanup of category names. Anki uses spaces to separate tags.
            tag = (element.element_info['Title']
                   .replace(' & ', '&')
                   .replace('] ', ']')
                   .replace(',', '')
                   .replace(' ', '_'))
            tags.append(tag)
        return ' '.join(tags[::-1])

    def get_relative_path_to_media_file(self, path_to_file, path_to_media_directory):
        """
        Return the relative path to a media file.

        SuperMemo stores full paths to media files but in Anki media files
        are relative to the location of the deck.
        """
        path_to_file = path_to_file.replace('\\', '/')
        path_to_media_directory = path_to_media_directory.replace('\\', '/')
        return path_to_file.replace(path_to_media_directory, '')

    def convert(self, element):
        """Return the element in a format compatible with Anki."""
        question_text = element.get_question() or ''
        answer_text = element.get_answer() or ''

        try:
            answer_sound = self.get_relative_path_to_media_file(
                element.get_answer_sound(), self.full_path_to_media)
        except AttributeError:
            answer_sound = ''

        try:
            question_sound = self.get_relative_path_to_media_file(
                element.get_question_sound(), self.full_path_to_media)
        except AttributeError:
            question_sound = ''

        out = "{0}[sound:{1}]\t{2}[sound:{3}]\t{4}".format(
            question_text, question_sound, answer_text, answer_sound,
            self.get_tags(element))
        return out

    def convert_all(self):
        """Return all elements in a format compatible with Anki."""
        exportable_elements = [self.convert(e) for e
                               in self.elements.values() if e.is_item()]
        return "\n".join(exportable_elements)


class Element:

    """
    This class represents a SuperMemo element such as a topic or an item.

    Accessing individual pieces of information about an element:
        ComponentNo -> self.properties['ComponentNo']
        Status -> self.element_info['Status']
        Type of component #2 -> self.components[1]['Type']
        (Note that SuperMemo component numbers start at 1.)
    """

    # Bits that determine if a component is a question or an answer.
    question = 0b00100000
    answer = 0b01000000

    def __init__(self, element_body):
        """
        Instantiate an Element from its textual representation.

        The textual representation of an element starts with
        "Begin Element #N" and ends with "End Element #N"
        where N is the ID of the element.
        """

        self.properties = {}
        self.element_info = {}
        self.components = []
        self.id = 0

        # Extract information from the element body line by line.
        inside_element_info = False
        inside_component = False
        for line in element_body.strip().split("\n"):
            line = line.strip()
            if line == "":
                pass
            if line.startswith("Begin Element "):
                self.id = int(line.split(' #')[-1])
            elif line.startswith("End Element "):
                pass
            elif line.startswith("Begin ElementInfo"):
                inside_element_info = True
            elif line.startswith("End ElementInfo"):
                inside_element_info = False
            elif line.startswith("Begin Component"):
                self.components.append({})
                inside_component = True
            elif line.startswith("End Component"):
                inside_component = False
            else:
                key, value = line.split('=', 1)
                if not inside_element_info and not inside_component:
                    self.properties[key] = value
                elif inside_component:
                    # There are other properties besides PlayAt and DisplayAt
                    # that could be converted to integers, but those two are
                    # the only ones currently used by the converter.
                    if key in ['PlayAt', 'DisplayAt']:
                        value = int(value)
                    self.components[-1][key] = value
                elif inside_element_info:
                    self.element_info[key] = value

    def get_question(self):
        """Return the text of the question."""
        for c in self.components:
            if (c['Type'] == 'Text' and c['DisplayAt'] & self.question
                and c['DisplayAt'] & self.answer):
                return c['Text']

    def get_answer(self):
        """Return the text of the answer."""
        for c in self.components:
            if (c['Type'] == 'Text' and not c['DisplayAt'] & self.question
                and c['DisplayAt'] & self.answer):
                return c['Text']

    def get_question_sound(self):
        """Return the full path to the audio file associated with the question."""
        for c in self.components:
            if c['Type'] == 'Sound' and c['PlayAt'] & self.question:
                return c['SoundFile']

    def get_answer_sound(self):
        """Return the full path to the audio file associated with the answer."""
        for c in self.components:
            if c['Type'] == 'Sound' and c['PlayAt'] & self.answer:
                return c['SoundFile']

    def is_item(self):
        """Return True if the element represents an item rather than a topic."""
        return self.element_info['Type'] == 'Item'

    def __str__(self):
        str = "Type: {} Id: {} Title: {}\n".format(
            self.element_info['Type'], self.id, self.element_info['Title'])
        for c in self.components:
            try:
                str += "Component -> Type: {} {} PlayAt {}\n".format(
                    c['Type'], c['SoundFile'], c['PlayAt'])
            except KeyError:
                str += "Component -> Type: {} {} DisplayAt {}\n".format(
                    c['Type'], c['Text'], c['DisplayAt'])
        return str

def read_sm_file(sm_file_contents):
    """Return a dictionary of Element objects indexed by ID."""
    elements = [Element(element_body) for element_body
                in sm_file_contents.strip().split("\n\n")]
    return dict((e.id, e) for e in elements)
