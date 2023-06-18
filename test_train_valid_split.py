# tullp
import os
import random
import shutil

source_folder = "~/labelled/WowboardMini/back"  # run code with each folder
train_folder = "~/train"
test_folder = "~/test"
valid_folder = "~/valid"

file_list = os.listdir(source_folder)
name_list = [os.path.splitext(filename)[0] for filename in file_list]
ext_list = [os.path.splitext(filename)[1] for filename in file_list]

name_set = set(name_list)  # separate filename

total_count = len(name_set)
train_count = int(total_count * 0.7)
test_count = int(total_count * 0.2)
valid_count = total_count - train_count - test_count    # train:test:valid = 7:2:1 539:152:83 -> 7:1.974:1.078

name_list_shuffled = random.sample(list(name_set), total_count)  # randomize file list

# Copy files for train set
for i in range(train_count):
    name = name_list_shuffled[i]
    index = name_list.index(name)
    source_path = os.path.join(source_folder, file_list[index])
    dest_path = os.path.join(train_folder, file_list[index])
    shutil.copy(source_path, dest_path)
    xml_index = ext_list[index:].index('.xml')
    xml_file = file_list[index + xml_index]
    xml_dest_path = os.path.join(train_folder, xml_file)
    xml_source_path = os.path.join(source_folder, xml_file)
    shutil.copy(xml_source_path, xml_dest_path)

# Copy files for test set
for i in range(train_count, train_count + test_count):
    name = name_list_shuffled[i]
    index = name_list.index(name)
    source_path = os.path.join(source_folder, file_list[index])
    dest_path = os.path.join(test_folder, file_list[index])
    shutil.copy(source_path, dest_path)
    xml_index = ext_list[index:].index('.xml')
    xml_file = file_list[index + xml_index]
    xml_dest_path = os.path.join(test_folder, xml_file)
    xml_source_path = os.path.join(source_folder, xml_file)
    shutil.copy(xml_source_path, xml_dest_path)

# Copy files for valid set
for i in range(train_count + test_count, total_count):
    name = name_list_shuffled[i]
    index = name_list.index(name)
    source_path = os.path.join(source_folder, file_list[index])
    dest_path = os.path.join(valid_folder, file_list[index])
    shutil.copy(source_path, dest_path)
    xml_index = ext_list[index:].index('.xml')
    xml_file = file_list[index + xml_index]
    xml_dest_path = os.path.join(valid_folder, xml_file)
    xml_source_path = os.path.join(source_folder, xml_file)
    shutil.copy(xml_source_path, xml_dest_path)
