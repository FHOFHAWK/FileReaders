import os
import json
import xml
import xml.etree.ElementTree as et
import csv


def write_in_common_table(indexes_list: list, lists: list) -> None:
    """Write common headers`s data from files in common table."""
    try:
        for header in FileReader.headers_intersection:
            if header in lists[0]:
                indexes_list.append(lists[0].index(header))
        lists.pop(0)
        for _list in lists:
            items_list = []
            for index in indexes_list:
                items_list.append(_list[index])
            FileReader.common_table.append(items_list)
    except IndexError:
        pass


class FileReader:
    headers_intersection = []
    common_table = []

    def __init__(self, file_name: str):
        self.file_name = file_name

    def get_reader_object(self):
        """Return reader depending from file type."""
        if self.file_name.endswith(".csv"):
            return CSVReader(self.file_name)

        elif self.file_name.endswith(".xml"):
            return XMLReader(self.file_name)

        elif self.file_name.endswith(".json"):
            return JSONReader(self.file_name)

        elif self.file_name.endswith((".yaml", ".yml")):
            return YAMLReader(self.file_name)


class JSONReader(FileReader):
    def __init__(self, file_name):
        super(JSONReader, self).__init__(file_name)

    def _get_json_dict_from_file(self):
        try:
            with open(self.file_name) as json_file:
                json_dict = json.load(json_file)
                return json_dict
        except json.decoder.JSONDecodeError:
            print("JSON is empty or corrupted. "
                  "Data will be missing in common table.")

    def find_common_headers(self):
        """Write common headers from JSON in FileReader.headers_intersection."""
        json_dict = self._get_json_dict_from_file()
        try:
            for key in json_dict:
                for list_item in json_dict[key]:
                    if not FileReader.headers_intersection:
                        FileReader.headers_intersection = list(
                            set([str(x) for x in list(list_item)]))
                    else:
                        FileReader.headers_intersection = list(
                            set(FileReader.headers_intersection) &
                            set([str(x) for x in list(list_item)]))
        except TypeError:
            print("JSON is empty or corrupted. "
                  "Data will be missing in common table.")

    def read_file(self):
        json_dict = self._get_json_dict_from_file()
        try:
            for key in json_dict:
                for list_item in json_dict[key]:
                    lists = []
                    indexes_list = []

                    lists.append([str(x) for x in list(list_item)])
                    lists.append([str(x) for x in list(list_item.values())])

                    write_in_common_table(indexes_list, lists)
        except TypeError:
            print("JSON is empty or corrupted. "
                  "Data will be missing in common table.")


class XMLReader(FileReader):
    def __init__(self, file_name):
        super(XMLReader, self).__init__(file_name)

    def find_common_headers(self):
        """Write common headers from XML in FileReader.headers_intersection."""
        try:
            root = et.parse(self.file_name).getroot()
            for list_of_tag_objects in root.findall('objects'):
                header_str = ''
                for obj in list_of_tag_objects:
                    header_str += obj.get('name') + ' '

                if not FileReader.headers_intersection:
                    FileReader.headers_intersection = list(set(header_str.strip().split(' ')))
                else:
                    FileReader.headers_intersection = list(
                        set(FileReader.headers_intersection) & set(header_str.strip().split(' ')))
        except xml.etree.ElementTree.ParseError:
            print("XML is empty or corrupted. "
                  "Data will be missing in common table.")

    def read_file(self):
        try:
            root = et.parse(self.file_name).getroot()
            for tag_object in root.findall('objects'):
                lists = []
                indexes_list = []

                value_str = ''
                header_str = ''
                for item in tag_object:
                    header_str += item.get('name') + ' '
                    value_str += item[0].text + ' '

                lists.append(header_str.strip().split(' '))
                lists.append(value_str.strip().split(' '))

                write_in_common_table(indexes_list, lists)
        except xml.etree.ElementTree.ParseError:
            print("XML is empty or corrupted. "
                  "Data will be missing in common table.")


class CSVReader(FileReader):
    def __init__(self, file_name):
        super(CSVReader, self).__init__(file_name)

    def find_common_headers(self):
        """Write common headers from CVS in FileReader.headers_intersection."""
        with open(self.file_name) as f:
            header = f.readline()
            if not FileReader.headers_intersection:
                FileReader.headers_intersection = list(set(header.rstrip("\n").split(",")))
            else:
                FileReader.headers_intersection = list(
                    set(FileReader.headers_intersection) & set(header.rstrip("\n").split(",")))

    def read_file(self):
        lists = []
        indexes_list = []
        with open(self.file_name) as file:
            reader = csv.reader(file)

            for row in reader:
                lists.append(row)

        write_in_common_table(indexes_list, lists)


class YAMLReader(FileReader):
    def __init__(self, file_name):
        super(YAMLReader, self).__init__(file_name)

    def find_common_headers(self):
        pass

    def read_file(self):
        pass


def main() -> None:
    grabbed_files_names = take_supported_files_in_directory()
    files_list = []
    try:
        for file_name in grabbed_files_names:
            files_list.append(FileReader(file_name=file_name).get_reader_object())
    except TypeError:
        print("Program cannot be executed.")

    for file in files_list:
        file.find_common_headers()

    FileReader.headers_intersection = sorted(FileReader.headers_intersection)
    FileReader.common_table.append(FileReader.headers_intersection)

    for file in files_list:
        file.read_file()

    try:
        for _list in FileReader.common_table[1:]:
            FileReader.common_table = sorted(FileReader.common_table,
                                             key=lambda first_elem: first_elem[0])
    except IndexError:
        pass

    with open("my_basic_result.tsv", "w") as output:
        for _list in FileReader.common_table:
            output.write(" ".join(_list) + '\n')

    if grabbed_files_names:
        solve_advanced(FileReader.common_table)


def take_supported_files_in_directory() -> list:
    """Return list of files`s names with supported extensions."""
    supported_file_types = (".csv", ".json", ".xml", ".yaml", ".yml")
    grabbed_files = []
    try:
        for file in os.listdir(os.getcwd()):
            if file.endswith(supported_file_types):
                grabbed_files.append(file)
        return grabbed_files
    except FileNotFoundError:
        print("There are not files with extensions .csv, .json, .xml, .yaml, .yml in directory.")
    except NameError:
        print("Invalid directory.")


def solve_advanced(common_table: list) -> None:
    index = common_table[0].index('M1')
    headers = common_table.pop(0)
    headers = ['MS' + x[1:] if x.startswith('M') else x for x in headers]

    advance_common_table = []

    all_indexes = list(range(len(common_table)))

    for i in range(len(common_table)):
        tmp_lists = []
        tmp_indexes = []

        tmp_lists.append(common_table[i][index:])
        tmp_indexes.append(i)

        for j in range(i + 1, len(common_table) - 1):
            if common_table[i][0:index] == common_table[j][0:index] and i != j:
                tmp_lists.append(common_table[j][index:])
                tmp_indexes.append(int(j))

        if len(tmp_indexes) > 1:
            for i in tmp_indexes:
                all_indexes.remove(i)

            tmp_lists = [[int(elem) for elem in _list] for _list in tmp_lists]

            tmp_lists = list(map(sum, zip(*tmp_lists)))
            advance_common_table.append(common_table[i][0:index] + tmp_lists)

    for i in all_indexes:
        advance_common_table.append(common_table[i])

    advance_common_table = sorted(advance_common_table, key=lambda el: el[0])
    advance_common_table = [[str(elem) for elem in _list] for _list in advance_common_table]
    advance_common_table.insert(0, headers)

    with open("my_advanced_result.tsv", "w") as output:
        for _list in advance_common_table:
            output.write(" ".join(_list) + '\n')


if __name__ == "__main__":
    main()
