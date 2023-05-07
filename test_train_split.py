# tullp
import os
import random
import shutil

source_folder = "~/labelled/WowboardMini/back"  # run code with each folder
train_folder = "~/train"
test_folder = "~/test"

file_list = os.listdir(source_folder)
name_list = [os.path.splitext(filename)[0] for filename in file_list]
ext_list = [os.path.splitext(filename)[1] for filename in file_list]

name_set = set(name_list)  # seperate filename

test_count = int(len(name_set) * 0.8)  # test : train = 8 : 2 -> editable

name_list_shuffled = random.sample(name_set, len(name_set))  # randomize file list

for i in range(test_count):  # test copy
    name = name_list_shuffled[i]
    index = name_list.index(name)  # png copy
    source_path = os.path.join(source_folder, file_list[index])
    dest_path = os.path.join(test_folder, file_list[index])
    shutil.copy(source_path, dest_path)
    xml_index = ext_list[index:].index('.xml')  # xml copy
    xml_file = file_list[index + xml_index]
    xml_dest_path = os.path.join(test_folder, xml_file)
    xml_source_path = os.path.join(source_folder, xml_file)
    shutil.copy(xml_source_path, xml_dest_path)

for i in range(test_count, len(name_set)):  # train copy
    name = name_list_shuffled[i]
    index = name_list.index(name)  # png copy
    source_path = os.path.join(source_folder, file_list[index])
    dest_path = os.path.join(train_folder, file_list[index])
    shutil.copy(source_path, dest_path)
    xml_index = ext_list[index:].index('.xml')  # xml copy
    xml_file = file_list[index + xml_index]
    xml_dest_path = os.path.join(train_folder, xml_file)
    xml_source_path = os.path.join(source_folder, xml_file)
    shutil.copy(xml_source_path, xml_dest_path)