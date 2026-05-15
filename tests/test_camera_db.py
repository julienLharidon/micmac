from pymicmac.utils.camera_db import CameraDatabase


def test_camera_db_load():
    # Test with the real file if possible
    db = CameraDatabase()
    if len(db) > 0:
        assert "LadyBug" in db
        cam = db.get_camera("Canon EOS 5D")
        assert cam['width_mm'] == 36.0
        assert cam['height_mm'] == 24.0

def test_camera_db_custom_path(tmp_path):
    xml_content = """<?xml version="1.0" ?>
    <MMCameraDataBase>
       <CameraEntry>
            <Name> TestCam </Name>
            <SzCaptMm> 10.0 20.0 </SzCaptMm>
       </CameraEntry>
    </MMCameraDataBase>
    """
    p = tmp_path / "custom_db.xml"
    p.write_text(xml_content)
    db = CameraDatabase(str(p))
    assert len(db) == 1
    assert "TestCam" in db
    assert db.get_camera("TestCam")['width_mm'] == 20.0
