# Tests for parse_vsr.py

import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
from trexolists.parse_vsr import (
    safe_find_text,
    parse_repeated_by,
    parse_repeat_of,
    parse_visits,
    parse_vsr_file,
)


# Fixtures
@pytest.fixture
def sample_vsr_file():
    """Path to the sample VSR file."""
    return Path("PPS/VSR/2734_VSR.xml")


@pytest.fixture
def minimal_xml_root():
    """Factory fixture for creating minimal XML elements."""
    def _create_root(xml_string):
        return ET.fromstring(xml_string)
    return _create_root


# Utility Functions Tests
class TestSafeFindText:
    """Tests for safe_find_text function."""
    
    def test_find_text_success(self, minimal_xml_root):
        """Test successfully finding text in an element."""
        xml = '<root><TestTag>test value</TestTag></root>'
        root = minimal_xml_root(xml)
        result = safe_find_text(root, "TestTag")
        assert result == "test value"
    
    def test_find_text_with_whitespace(self, minimal_xml_root):
        """Test finding text with whitespace that gets stripped."""
        xml = '<root><TestTag>  test value  </TestTag></root>'
        root = minimal_xml_root(xml)
        result = safe_find_text(root, "TestTag")
        assert result == "test value"
    
    def test_find_text_missing_element(self, minimal_xml_root):
        """Test finding text when element doesn't exist."""
        xml = '<root></root>'
        root = minimal_xml_root(xml)
        result = safe_find_text(root, "MissingTag")
        assert result is None
    
    def test_find_text_none_text(self, minimal_xml_root):
        """Test finding element with None text."""
        xml = '<root><TestTag></TestTag></root>'
        root = minimal_xml_root(xml)
        result = safe_find_text(root, "TestTag")
        assert result is None
    
    def test_find_text_empty_string(self, minimal_xml_root):
        """Test finding element with empty string."""
        xml = '<root><TestTag></TestTag></root>'
        root = minimal_xml_root(xml)
        result = safe_find_text(root, "TestTag")
        assert result is None


# Helper Functions Tests
class TestParseRepeatedBy:
    """Tests for parse_repeated_by function."""
    
    def test_parse_repeated_by_exists_all_fields(self, minimal_xml_root):
        """Test parsing when repeatedBy element exists with all fields."""
        xml = '''<visit>
            <repeatedBy>
                <program>1234</program>
                <observation>1</observation>
                <visit>2</visit>
                <problemID>PROB001</problemID>
            </repeatedBy>
        </visit>'''
        visit = minimal_xml_root(xml)
        result = parse_repeated_by(visit)
        assert result["status"] == "Yes"
        assert result["program"] == "1234"
        assert result["observation"] == "1"
        assert result["visit"] == "2"
        assert result["problemID"] == "PROB001"
    
    def test_parse_repeated_by_exists_partial_fields(self, minimal_xml_root):
        """Test parsing when repeatedBy element exists with partial fields."""
        xml = '''<visit>
            <repeatedBy>
                <program>1234</program>
                <observation>1</observation>
            </repeatedBy>
        </visit>'''
        visit = minimal_xml_root(xml)
        result = parse_repeated_by(visit)
        assert result["status"] == "Yes"
        assert result["program"] == "1234"
        assert result["observation"] == "1"
        assert result["visit"] is None
        assert result["problemID"] is None
    
    def test_parse_repeated_by_not_exists(self, minimal_xml_root):
        """Test parsing when repeatedBy element doesn't exist."""
        xml = '<visit></visit>'
        visit = minimal_xml_root(xml)
        result = parse_repeated_by(visit)
        assert result["status"] == "No"
        assert result["program"] is None
        assert result["observation"] is None
        assert result["visit"] is None
        assert result["problemID"] is None
    
    def test_parse_repeated_by_with_whitespace(self, minimal_xml_root):
        """Test parsing with whitespace in fields."""
        xml = '''<visit>
            <repeatedBy>
                <program>  1234  </program>
                <observation>  1  </observation>
            </repeatedBy>
        </visit>'''
        visit = minimal_xml_root(xml)
        result = parse_repeated_by(visit)
        assert result["status"] == "Yes"
        assert result["program"] == "1234"
        assert result["observation"] == "1"


class TestParseRepeatOf:
    """Tests for parse_repeat_of function."""
    
    def test_parse_repeat_of_exists_all_fields(self, minimal_xml_root):
        """Test parsing when repeatOf element exists with all fields."""
        xml = '''<visit>
            <repeatOf>
                <program>1234</program>
                <observation>1</observation>
                <visit>2</visit>
                <problemID>PROB001</problemID>
            </repeatOf>
        </visit>'''
        visit = minimal_xml_root(xml)
        result = parse_repeat_of(visit)
        assert result["status"] == "Yes"
        assert result["program"] == "1234"
        assert result["observation"] == "1"
        assert result["visit"] == "2"
        assert result["problemID"] == "PROB001"
    
    def test_parse_repeat_of_exists_partial_fields(self, minimal_xml_root):
        """Test parsing when repeatOf element exists with partial fields."""
        xml = '''<visit>
            <repeatOf>
                <program>1234</program>
                <observation>1</observation>
            </repeatOf>
        </visit>'''
        visit = minimal_xml_root(xml)
        result = parse_repeat_of(visit)
        assert result["status"] == "Yes"
        assert result["program"] == "1234"
        assert result["observation"] == "1"
        assert result["visit"] is None
        assert result["problemID"] is None
    
    def test_parse_repeat_of_not_exists(self, minimal_xml_root):
        """Test parsing when repeatOf element doesn't exist."""
        xml = '<visit></visit>'
        visit = minimal_xml_root(xml)
        result = parse_repeat_of(visit)
        assert result["status"] == "No"
        assert result["program"] is None
        assert result["observation"] is None
        assert result["visit"] is None
        assert result["problemID"] is None
    
    def test_parse_repeat_of_with_whitespace(self, minimal_xml_root):
        """Test parsing with whitespace in fields."""
        xml = '''<visit>
            <repeatOf>
                <program>  1234  </program>
                <observation>  1  </observation>
            </repeatOf>
        </visit>'''
        visit = minimal_xml_root(xml)
        result = parse_repeat_of(visit)
        assert result["status"] == "Yes"
        assert result["program"] == "1234"
        assert result["observation"] == "1"


# Main Parsing Functions Tests
class TestParseVisits:
    """Tests for parse_visits function."""
    
    def test_parse_visits_all_from_file(self, sample_vsr_file):
        """Test parsing all visits from the real VSR file."""
        tree = ET.parse(sample_vsr_file)
        root = tree.getroot()
        
        visits = parse_visits(root)
        
        assert len(visits) == 2
        assert all("observation" in visit for visit in visits)
        assert all("visit" in visit for visit in visits)
        assert all("target" in visit for visit in visits)
    
    def test_parse_visits_with_target_filter_matching(self, sample_vsr_file):
        """Test parsing visits with target_name filter (matching)."""
        tree = ET.parse(sample_vsr_file)
        root = tree.getroot()
        
        visits = parse_visits(root, target_name="WASP-96")
        
        assert len(visits) == 1
        assert visits[0]["target"] == "WASP-96"
    
    def test_parse_visits_with_target_filter_non_matching(self, sample_vsr_file):
        """Test parsing visits with target_name filter (non-matching)."""
        tree = ET.parse(sample_vsr_file)
        root = tree.getroot()
        
        visits = parse_visits(root, target_name="NonExistentTarget")
        
        assert len(visits) == 0
    
    def test_parse_visits_with_target_filter_whitespace(self, minimal_xml_root):
        """Test parsing visits with target_name filter (case/whitespace handling)."""
        xml = '''<root>
            <visit observation="1" visit="1">
                <target>  WASP-96  </target>
            </visit>
        </root>'''
        root = minimal_xml_root(xml)
        
        visits = parse_visits(root, target_name="WASP-96")
        assert len(visits) == 1
        
        visits = parse_visits(root, target_name="  WASP-96  ")
        assert len(visits) == 1
    
    def test_parse_visit_all_fields(self, minimal_xml_root):
        """Test parsing visit with all fields present."""
        xml = '''<root>
            <visit observation="1" visit="1">
                <status>Archived</status>
                <target>WASP-96</target>
                <configuration>NIRISS Single-Object Slitless Spectroscopy</configuration>
                <hours>7.51</hours>
                <longRangePlanStatus>Planned</longRangePlanStatus>
                <planWindow>2022-06-21</planWindow>
                <startTime>Jun 21, 2022 02:41:18</startTime>
                <endTime>Jun 21, 2022 10:48:41</endTime>
                <repeatedBy>
                    <program>1234</program>
                    <observation>1</observation>
                </repeatedBy>
                <repeatOf>
                    <program>1234</program>
                    <visit>2</visit>
                </repeatOf>
            </visit>
        </root>'''
        root = minimal_xml_root(xml)
        
        visits = parse_visits(root)
        assert len(visits) == 1
        
        visit = visits[0]
        assert visit["observation"] == "1"
        assert visit["visit"] == "1"
        assert visit["status"] == "Archived"
        assert visit["target"] == "WASP-96"
        assert visit["configuration"] == "NIRISS Single-Object Slitless Spectroscopy"
        assert visit["hours"] == "7.51"
        assert visit["longRangePlanStatus"] == "Planned"
        assert visit["planWindow"] == "2022-06-21"
        assert visit["startTime"] == "Jun 21, 2022 02:41:18"
        assert visit["endTime"] == "Jun 21, 2022 10:48:41"
        assert visit["repeatedBy"]["status"] == "Yes"
        assert visit["repeatOf"]["status"] == "Yes"
    
    def test_parse_visit_missing_optional_fields(self, minimal_xml_root):
        """Test parsing visit with missing optional fields."""
        xml = '''<root>
            <visit observation="1" visit="1">
                <status>Archived</status>
                <target>WASP-96</target>
            </visit>
        </root>'''
        root = minimal_xml_root(xml)
        
        visits = parse_visits(root)
        assert len(visits) == 1
        
        visit = visits[0]
        assert visit["observation"] == "1"
        assert visit["visit"] == "1"
        assert visit["status"] == "Archived"
        assert visit["target"] == "WASP-96"
        assert visit["configuration"] is None
        assert visit["hours"] is None
        assert visit["longRangePlanStatus"] is None
        assert visit["planWindow"] is None
        assert visit["startTime"] is None
        assert visit["endTime"] is None
        assert visit["repeatedBy"]["status"] == "No"
        assert visit["repeatOf"]["status"] == "No"
    
    def test_parse_visit_with_repeated_by_repeat_of(self, minimal_xml_root):
        """Test parsing visit with repeatedBy and repeatOf elements."""
        xml = '''<root>
            <visit observation="1" visit="1">
                <target>WASP-96</target>
                <repeatedBy>
                    <program>1234</program>
                    <observation>1</observation>
                    <visit>2</visit>
                    <problemID>PROB001</problemID>
                </repeatedBy>
                <repeatOf>
                    <program>5678</program>
                    <observation>2</observation>
                    <visit>1</visit>
                    <problemID>PROB002</problemID>
                </repeatOf>
            </visit>
        </root>'''
        root = minimal_xml_root(xml)
        
        visits = parse_visits(root)
        assert len(visits) == 1
        
        visit = visits[0]
        assert visit["repeatedBy"]["status"] == "Yes"
        assert visit["repeatedBy"]["program"] == "1234"
        assert visit["repeatedBy"]["observation"] == "1"
        assert visit["repeatedBy"]["visit"] == "2"
        assert visit["repeatedBy"]["problemID"] == "PROB001"
        assert visit["repeatOf"]["status"] == "Yes"
        assert visit["repeatOf"]["program"] == "5678"
        assert visit["repeatOf"]["observation"] == "2"
        assert visit["repeatOf"]["visit"] == "1"
        assert visit["repeatOf"]["problemID"] == "PROB002"
    
    def test_parse_visits_none_exist(self, minimal_xml_root):
        """Test parsing when no visits exist."""
        xml = '<root></root>'
        root = minimal_xml_root(xml)
        
        visits = parse_visits(root)
        assert visits == []
    
    def test_parse_visit_attributes(self, minimal_xml_root):
        """Test parsing visit attributes (observation, visit)."""
        xml = '''<root>
            <visit observation="5" visit="10">
                <target>TestTarget</target>
            </visit>
        </root>'''
        root = minimal_xml_root(xml)
        
        visits = parse_visits(root)
        assert len(visits) == 1
        assert visits[0]["observation"] == "5"
        assert visits[0]["visit"] == "10"
    
    def test_parse_visits_target_filter_none_target(self, minimal_xml_root):
        """Test parsing visits when target is None and filter is provided."""
        xml = '''<root>
            <visit observation="1" visit="1">
            </visit>
        </root>'''
        root = minimal_xml_root(xml)
        
        visits = parse_visits(root, target_name="SomeTarget")
        assert len(visits) == 0


# End-to-End Function Tests
class TestParseVsrFile:
    """Tests for parse_vsr_file function."""
    
    def test_parse_vsr_file_end_to_end(self, sample_vsr_file):
        """Test end-to-end parsing of VSR file."""
        vsr_dict = parse_vsr_file(sample_vsr_file)
        
        # Check that all top-level fields exist
        expected_fields = [
            "observatory", "id", "title", "reportTime", "Visits"
        ]
        
        for field in expected_fields:
            assert field in vsr_dict
    
    def test_parse_root_attributes(self, sample_vsr_file):
        """Test parsing root-level attributes (observatory, id)."""
        vsr_dict = parse_vsr_file(sample_vsr_file)
        
        assert vsr_dict["observatory"] == "JWST"
        assert vsr_dict["id"] == "2734"
    
    def test_parse_root_elements(self, sample_vsr_file):
        """Test parsing root-level elements (title, reportTime)."""
        vsr_dict = parse_vsr_file(sample_vsr_file)
        
        assert vsr_dict["title"] == "Visit Information"
        assert vsr_dict["reportTime"] is not None
        assert isinstance(vsr_dict["reportTime"], str)
        assert len(vsr_dict["reportTime"]) > 0
    
    def test_parse_visits_integration(self, sample_vsr_file):
        """Test parsing visits integration."""
        vsr_dict = parse_vsr_file(sample_vsr_file)
        
        assert isinstance(vsr_dict["Visits"], list)
        assert len(vsr_dict["Visits"]) == 2
        
        # Check first visit has expected fields
        first_visit = vsr_dict["Visits"][0]
        assert "observation" in first_visit
        assert "visit" in first_visit
        assert "target" in first_visit
        assert "status" in first_visit
    
    def test_parse_with_target_name_filter(self, sample_vsr_file):
        """Test parsing with target_name filter."""
        vsr_dict = parse_vsr_file(sample_vsr_file, target_name="WASP-96")
        
        assert len(vsr_dict["Visits"]) == 1
        assert vsr_dict["Visits"][0]["target"] == "WASP-96"
    
    def test_parse_missing_root_attributes(self, tmp_path):
        """Test parsing when root attributes are missing."""
        xml = '<visitStatusReport><title>Test</title></visitStatusReport>'
        test_file = tmp_path / "test_vsr.xml"
        test_file.write_text(xml)
        
        vsr_dict = parse_vsr_file(test_file)
        
        assert vsr_dict["observatory"] is None
        assert vsr_dict["id"] is None
    
    def test_parse_missing_root_elements(self, tmp_path):
        """Test parsing when root elements are missing."""
        xml = '<visitStatusReport observatory="JWST" id="1234"></visitStatusReport>'
        test_file = tmp_path / "test_vsr.xml"
        test_file.write_text(xml)
        
        vsr_dict = parse_vsr_file(test_file)
        
        assert vsr_dict["title"] is None
        assert vsr_dict["reportTime"] is None
    
    def test_parse_file_not_found(self):
        """Test error handling when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            parse_vsr_file("nonexistent_file.xml")
    
    def test_parse_invalid_xml(self, tmp_path):
        """Test error handling with invalid XML."""
        test_file = tmp_path / "test_vsr.xml"
        test_file.write_text("not valid xml")
        
        with pytest.raises(ET.ParseError):
            parse_vsr_file(test_file)
    
    def test_parse_all_fields_initialized(self, sample_vsr_file):
        """Test that all fields are initialized even if missing."""
        vsr_dict = parse_vsr_file(sample_vsr_file)
        
        # All fields should exist, even if None
        assert "observatory" in vsr_dict
        assert "id" in vsr_dict
        assert "title" in vsr_dict
        assert "reportTime" in vsr_dict
        assert "Visits" in vsr_dict
    
    def test_parse_visit_fields_structure(self, sample_vsr_file):
        """Test that visit fields have correct structure."""
        vsr_dict = parse_vsr_file(sample_vsr_file)
        
        expected_visit_fields = [
            "observation", "visit", "status", "target", "configuration",
            "hours", "longRangePlanStatus", "planWindow", "startTime",
            "endTime", "repeatedBy", "repeatOf"
        ]
        
        for visit in vsr_dict["Visits"]:
            for field in expected_visit_fields:
                assert field in visit
            
            # Check nested structures
            assert "status" in visit["repeatedBy"]
            assert "program" in visit["repeatedBy"]
            assert "observation" in visit["repeatedBy"]
            assert "visit" in visit["repeatedBy"]
            assert "problemID" in visit["repeatedBy"]
            
            assert "status" in visit["repeatOf"]
            assert "program" in visit["repeatOf"]
            assert "observation" in visit["repeatOf"]
            assert "visit" in visit["repeatOf"]
            assert "problemID" in visit["repeatOf"]
