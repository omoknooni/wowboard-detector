# tu11p
import os
import glob
import xml.etree.ElementTree as ET

folder_path = "/~/"  # run code with each folder


for xml_file in glob.glob(os.path.join(folder_path, "*.xml")):
    if "_aug" in xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for annotation in root.iter("annotation"):  # <filename> modify
            for filename in annotation.iter("filename"):
                if filename.text.endswith(".png") and not filename.text.endswith("_aug.png"):   # already edited file filter
                    filename.text = filename.text.replace(".png", "_aug.png")
        tree.write(xml_file)