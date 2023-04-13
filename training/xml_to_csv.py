import os
import glob
import argparse
import pandas as pd
import xml.etree.ElementTree as ET


def xml_to_csv(path):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                     int(root.find('size')[0].text),
                     int(root.find('size')[1].text),
                     member[0].text,
                     int(member[4][0].text),
                     int(member[4][1].text),
                     int(member[4][2].text),
                     int(member[4][3].text)
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert XML to CSV')
    parser.add_argument('--image_dir', required=True, help='Path of image directory')
    parser.add_argument('--output_dir', required=False, help='Path of output CSV file')

    args = parser.parse_args()
    if os.path.exists(args.image_dir):
        if not args.output_dir:
            args.output_dir = args.image_dir
        else:
            pass
    else:
        raise Exception(f'[!] Path {args.image_dir} is not exists')

    for folder in ['train', 'test']:
        image_path = os.path.join(args.image_dir,folder)
        xml_df = xml_to_csv(image_path)
        csv_path = os.path.join(args.output_dir,f'{folder}_labels.csv')
        xml_df.to_csv(csv_path, index=None)
        print(f'[*] Successfully converted xml to csv. >> {csv_path}')