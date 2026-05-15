import os
import xml.etree.ElementTree as ET  # nosec B405


class CameraDatabase:
    def __init__(self, xml_path=None):
        if xml_path is None:
            # Default path relative to project root
            base_path = os.path.dirname(__file__)
            xml_path = os.path.join(
                base_path, "../../../include/XML_MicMac/DicoCamera.xml"
            )

        self.cameras = {}
        if os.path.exists(xml_path):
            self._load_xml(xml_path)

    def _load_xml(self, path):
        tree = ET.parse(path)  # nosec B314
        root = tree.getroot()
        for entry in root.findall('CameraEntry'):
            name = entry.find('Name').text.strip()
            sz_mm = entry.find('SzCaptMm').text.strip().split()
            if len(sz_mm) == 2:
                short_name_elem = entry.find('ShortName')
                short_name = (
                    short_name_elem.text.strip()
                    if short_name_elem is not None else name
                )
                self.cameras[name] = {
                    'width_mm': float(sz_mm[1]),
                    'height_mm': float(sz_mm[0]),
                    'short_name': short_name
                }

    def get_camera(self, name):
        return self.cameras.get(name)

    def __iter__(self):
        return iter(self.cameras)

    def __len__(self):
        return len(self.cameras)
