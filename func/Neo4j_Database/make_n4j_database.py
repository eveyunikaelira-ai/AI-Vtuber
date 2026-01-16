import csv
import utils
from func.Neo4j_Database import to_neo4j
from tqdm import tqdm


def check_dict_in_dict(dict_a, dict_b):
    key_name = dict_a['name']
    value = dict_a['value']

    # Check whether the key exists in dict b
    if key_name in dict_b:
        # If the value is a list, check whether value is present
        if isinstance(dict_b[key_name], list):
            return value in dict_b[key_name]
        # If the value is a scalar, compare directly
        else:
            return dict_b[key_name] == value
    return False

def make_data_dict(csv_file_path,song_dict_path):
    # Dict for storing processed data
    data_dict = {}
    # Read CSV file
    with open(csv_file_path, 'r', encoding='gbk') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Read header row
        labels = next(csv_reader)
        # Initialize dict
        for label in labels:
            data_dict[label] = []
        # Read data rows
        for row in csv_reader:
            for label, value in zip(labels, row):
                # Check whether the value contains commas
                if '；' in value:
                    # Split on Chinese comma
                    sub_values = [sub_value.strip() for sub_value in value.split('，')]
                    # Iterate through split values
                    for sub_value in sub_values:
                        # Check for duplicates
                        if sub_value not in data_dict[label]:
                            data_dict[label].append(sub_value)
                elif ';' in value:
                    # Split on English comma
                    sub_values = [sub_value.strip() for sub_value in value.split(',')]
                    # Iterate through split values
                    for sub_value in sub_values:
                        # Check for duplicates
                        if sub_value not in data_dict[label]:
                            data_dict[label].append(sub_value)
                else:
                    # Check for duplicates
                    if value not in data_dict[label]:
                        data_dict[label].append(value)
    utils.write_json(data_dict,song_dict_path)
    return data_dict

def parse_csv_to_dict_list(file_path):
    dict_list = []
    with open(file_path, 'r', encoding='gbk') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            song_info = {}
            for key, value in row.items():
                if value:  # If not empty
                    # Check for Chinese comma-separated values
                    if '；' in value:
                        song_info[key] = value.split('，')
                    else:
                        song_info[key] = value
                else:
                    song_info[key] = []
            dict_list.append(song_info)
    return dict_list

def cognition_to_neo4j(cognition_dict_path = "../../data/json/cognition.json",cognition_csv_path = "../../configs/csv/cognition.csv",config_path = "../../configs/json/config.json"):
    make_data_dict(cognition_csv_path, cognition_dict_path)
    cognition_dicts = utils.load_json(cognition_dict_path)
    cognition_nodes_no_name = []
    cognition_nodes_with_name = []
    neo = to_neo4j.Neo4jHandler(config_path)
    cognition_tags = list(cognition_dicts.keys())[:]
    # Add all nodes
    for tag in cognition_tags:
        tag_lists = cognition_dicts[tag]
        for item in tag_lists:
            if item == "":
                continue
            neo.add_node("认知", {"name": tag, "value": item})
            if tag == "名称":
                cognition_nodes_with_name.append({"name": tag, "value": item})
            else:
                cognition_nodes_no_name.append({"name": tag, "value": item})
    # Add relationships
    dict_list = parse_csv_to_dict_list(cognition_csv_path)
    progress_bar = tqdm(total=len(dict_list) * len(cognition_nodes_no_name), desc='Building node relationships')
    for cognition_d in dict_list:
        for cognition_node in cognition_nodes_no_name:
            is_present = check_dict_in_dict(cognition_node, cognition_d)
            if is_present:
                node1 = neo.search_node("认知", cognition_node)
                node2 = neo.search_node("认知", {"name": "名称", "value": cognition_d["名称"]})
                neo.set_relationship(node1[0]["node"], node2[0]["node"], "认知关系", {"name": "认知"})
                neo.set_relationship(node2[0]["node"], node1[0]["node"], "认知关系", {"name": cognition_node["name"]})
            progress_bar.update(1)
    progress_bar.close()


def song_dict_to_neo4j(song_dict_path = "../../data/json/song_dict.json",song_csv_path = "../../configs/csv/song_library.csv",config_path = "../../configs/json/config.json"):
    song_dicts = utils.load_json(song_dict_path)
    song_nodes_no_name = []
    song_nodes_with_name = []
    neo = to_neo4j.Neo4jHandler(config_path)
    song_tags = list(song_dicts.keys())[1:]
    # Add all nodes
    for tag in song_tags:
        tag_lists = song_dicts[tag]
        for item in tag_lists:
            if item == "":
                continue
            neo.add_node("歌库",{"name":tag,"value":item})
            if tag == "歌名":
                song_nodes_with_name.append({"name":tag,"value":item})
            else:
                song_nodes_no_name.append({"name":tag,"value":item})
    #print(song_nodes_no_name)
    # Add relationships
    dict_list = parse_csv_to_dict_list(song_csv_path)
    # Progress bar length = len(dict_list) * len(song_nodes_no_name)
    progress_bar = tqdm(total=len(dict_list) * len(song_nodes_no_name), desc='Building node relationships')
    for song_d in dict_list:
        for song_node in song_nodes_no_name:
            is_present = check_dict_in_dict(song_node, song_d)
            if is_present:
                node1 = neo.search_node("歌库", song_node)
                node2 = neo.search_node("歌库", {"name": "歌名", "value": song_d["歌名"]})
                # Create relationship from song info node -> title node
                neo.set_relationship(node1[0]["node"], node2[0]["node"], "歌曲关系", {"name": "歌名"})
                neo.set_relationship(node2[0]["node"], node1[0]["node"], "歌曲关系", {"name": song_node["name"]})
            progress_bar.update(1)
    progress_bar.close()



if __name__ == '__main__':
    # make_song_dict("../../configs/csv/song_library.csv","../../data/json/song_dict.json")
    song_dict_to_neo4j()
    cognition_to_neo4j()
