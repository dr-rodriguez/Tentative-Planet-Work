# Tests for parse_apt.py

import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
from trexolists.parse_apt import (
    safe_find_text,
    extract_text_by_tag,
    extract_common_attributes,
    extract_from_exposure,
    parse_niriss_soss,
    parse_nircam_gts,
    parse_nirspec_bots,
    parse_miri_lrs,
    parse_miri_imaging,
    parse_miri_mrs,
    parse_targets,
    parse_data_requests,
    parse_apt_file,
    NS,
)


# Fixtures
@pytest.fixture
def sample_apt_file():
    """Path to the sample APT file."""
    return Path("PPS/APT/2734_APT.xml")


@pytest.fixture
def xml_namespace():
    """XML namespace constant."""
    return NS


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
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT"><TestTag>test value</TestTag></root>'
        root = minimal_xml_root(xml)
        result = safe_find_text(root, f"{NS}TestTag")
        assert result == "test value"
    
    def test_find_text_with_whitespace(self, minimal_xml_root):
        """Test finding text with whitespace that gets stripped."""
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT"><TestTag>  test value  </TestTag></root>'
        root = minimal_xml_root(xml)
        result = safe_find_text(root, f"{NS}TestTag")
        assert result == "test value"
    
    def test_find_text_missing_element(self, minimal_xml_root):
        """Test finding text when element doesn't exist."""
        xml = '<root></root>'
        root = minimal_xml_root(xml)
        result = safe_find_text(root, f"{NS}MissingTag")
        assert result is None
    
    def test_find_text_none_text(self, minimal_xml_root):
        """Test finding element with None text."""
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT"><TestTag></TestTag></root>'
        root = minimal_xml_root(xml)
        result = safe_find_text(root, f"{NS}TestTag")
        assert result is None
    
    def test_find_text_empty_string(self, minimal_xml_root):
        """Test finding element with empty string."""
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT"><TestTag></TestTag></root>'
        root = minimal_xml_root(xml)
        result = safe_find_text(root, f"{NS}TestTag")
        assert result is None


class TestExtractTextByTag:
    """Tests for extract_text_by_tag function."""
    
    def test_extract_text_pattern_match(self, minimal_xml_root):
        """Test extracting text by tag pattern."""
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT"><SomeSubarray>SUBSTRIP256</SomeSubarray></root>'
        root = minimal_xml_root(xml)
        result = extract_text_by_tag(root, "Subarray")
        assert result == "SUBSTRIP256"
    
    def test_extract_text_multiple_matches(self, minimal_xml_root):
        """Test extracting text when multiple matches exist (first wins)."""
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT">\n            <FirstSubarray>FIRST</FirstSubarray>\n            <SecondSubarray>SECOND</SecondSubarray>\n        </root>'
        root = minimal_xml_root(xml)
        result = extract_text_by_tag(root, "Subarray")
        assert result == "FIRST"
    
    def test_extract_text_no_match(self, minimal_xml_root):
        """Test extracting text when no pattern matches."""
        xml = '<root><OtherTag>value</OtherTag></root>'
        root = minimal_xml_root(xml)
        result = extract_text_by_tag(root, "Subarray")
        assert result is None
    
    def test_extract_text_none_text(self, minimal_xml_root):
        """Test extracting text when element has None text."""
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT"><SomeSubarray></SomeSubarray></root>'
        root = minimal_xml_root(xml)
        result = extract_text_by_tag(root, "Subarray")
        assert result is None
    
    def test_extract_text_with_whitespace(self, minimal_xml_root):
        """Test extracting text with whitespace that gets stripped."""
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT"><SomeSubarray>  SUBSTRIP256  </SomeSubarray></root>'
        root = minimal_xml_root(xml)
        result = extract_text_by_tag(root, "Subarray")
        assert result == "SUBSTRIP256"


# Template Helper Functions Tests
class TestExtractCommonAttributes:
    """Tests for extract_common_attributes function."""
    
    def test_extract_all_attributes(self, minimal_xml_root):
        """Test extracting all common attributes."""
        xml = '<template xmlns="http://www.stsci.edu/JWST/APT">\n            <Subarray>SUBSTRIP256</Subarray>\n            <ReadoutPattern>NISRAPID</ReadoutPattern>\n            <Groups>9</Groups>\n        </template>'
        templ = minimal_xml_root(xml)
        result = extract_common_attributes(templ)
        assert result["obs_subarray"] == "SUBSTRIP256"
        assert result["obs_rop"] == "NISRAPID"
        assert result["obs_groups"] == "9"
    
    def test_extract_partial_attributes(self, minimal_xml_root):
        """Test extracting when some attributes are missing."""
        xml = '<template xmlns="http://www.stsci.edu/JWST/APT">\n            <Subarray>SUBSTRIP256</Subarray>\n            <Groups>9</Groups>\n        </template>'
        templ = minimal_xml_root(xml)
        result = extract_common_attributes(templ)
        assert result["obs_subarray"] == "SUBSTRIP256"
        assert result["obs_rop"] is None
        assert result["obs_groups"] == "9"
    
    def test_extract_no_attributes(self, minimal_xml_root):
        """Test extracting when no attributes are present."""
        xml = '<template></template>'
        templ = minimal_xml_root(xml)
        result = extract_common_attributes(templ)
        assert result["obs_subarray"] is None
        assert result["obs_rop"] is None
        assert result["obs_groups"] is None
    
    def test_extract_pattern_matching(self, minimal_xml_root):
        """Test that pattern matching works for tag names."""
        xml = '<template xmlns="http://www.stsci.edu/JWST/APT">\n            <SomeSubarray>SUBSTRIP256</SomeSubarray>\n            <SomeReadoutPattern>NISRAPID</SomeReadoutPattern>\n            <SomeGroups>9</SomeGroups>\n        </template>'
        templ = minimal_xml_root(xml)
        result = extract_common_attributes(templ)
        assert result["obs_subarray"] == "SUBSTRIP256"
        assert result["obs_rop"] == "NISRAPID"
        assert result["obs_groups"] == "9"


class TestExtractFromExposure:
    """Tests for extract_from_exposure function."""
    
    def test_extract_all_fields(self, minimal_xml_root):
        """Test extracting ReadoutPattern and Groups from Exposure."""
        xml = '<exposure xmlns="http://www.stsci.edu/JWST/APT">\n            <ReadoutPattern>NISRAPID</ReadoutPattern>\n            <Groups>9</Groups>\n        </exposure>'
        templ_attr = minimal_xml_root(xml)
        result = extract_from_exposure(templ_attr)
        assert result["obs_rop"] == "NISRAPID"
        assert result["obs_groups"] == "9"
    
    def test_extract_partial_fields(self, minimal_xml_root):
        """Test extracting when some fields are missing."""
        xml = '<exposure xmlns="http://www.stsci.edu/JWST/APT">\n            <ReadoutPattern>NISRAPID</ReadoutPattern>\n        </exposure>'
        templ_attr = minimal_xml_root(xml)
        result = extract_from_exposure(templ_attr)
        assert result["obs_rop"] == "NISRAPID"
        assert result["obs_groups"] is None
    
    def test_extract_no_fields(self, minimal_xml_root):
        """Test extracting when no fields are present."""
        xml = '<exposure></exposure>'
        templ_attr = minimal_xml_root(xml)
        result = extract_from_exposure(templ_attr)
        assert result["obs_rop"] is None
        assert result["obs_groups"] is None
    
    def test_extract_pattern_matching(self, minimal_xml_root):
        """Test that pattern matching works for tag names."""
        xml = '<exposure xmlns="http://www.stsci.edu/JWST/APT">\n            <SomeReadoutPattern>NISRAPID</SomeReadoutPattern>\n            <SomeGroups>9</SomeGroups>\n        </exposure>'
        templ_attr = minimal_xml_root(xml)
        result = extract_from_exposure(templ_attr)
        assert result["obs_rop"] == "NISRAPID"
        assert result["obs_groups"] == "9"


# Template Parser Functions Tests
class TestParseNirissSoss:
    """Tests for parse_niriss_soss function."""
    
    def test_parse_complete_soss(self, minimal_xml_root):
        """Test parsing complete NIRISS SOSS template."""
        xml = '''<root xmlns:nisoss="http://www.stsci.edu/JWST/APT/Template/NirissSoss">
            <nisoss:NirissSoss>
                <nisoss:Subarray>SUBSTRIP256</nisoss:Subarray>
                <nisoss:Exposure>
                    <nisoss:ReadoutPattern>NISRAPID</nisoss:ReadoutPattern>
                    <nisoss:Groups>9</nisoss:Groups>
                </nisoss:Exposure>
            </nisoss:NirissSoss>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_niriss_soss(templ)
        assert result["obs_mode"] == "SOSS"
        assert result["obs_subarray"] == "SUBSTRIP256"
        assert result["obs_rop"] == "NISRAPID"
        assert result["obs_groups"] == "9"
        assert result["obs_opt_elem"] is None
    
    def test_parse_soss_missing_fields(self, minimal_xml_root):
        """Test parsing SOSS template with missing fields."""
        xml = '<root xmlns:nisoss="http://www.stsci.edu/JWST/APT/Template/NirissSoss"><nisoss:NirissSoss></nisoss:NirissSoss></root>'
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_niriss_soss(templ)
        assert result["obs_mode"] == "SOSS"
        assert result["obs_subarray"] is None
        assert result["obs_rop"] is None
        assert result["obs_groups"] is None
        assert result["obs_opt_elem"] is None
    
    def test_parse_soss_subarray_only(self, minimal_xml_root):
        """Test parsing SOSS template with only Subarray."""
        xml = '''<root xmlns:nisoss="http://www.stsci.edu/JWST/APT/Template/NirissSoss">
            <nisoss:NirissSoss>
                <nisoss:Subarray>SUBSTRIP256</nisoss:Subarray>
            </nisoss:NirissSoss>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_niriss_soss(templ)
        assert result["obs_mode"] == "SOSS"
        assert result["obs_subarray"] == "SUBSTRIP256"
        assert result["obs_rop"] is None
        assert result["obs_groups"] is None


class TestParseNircamGts:
    """Tests for parse_nircam_gts function."""
    
    def test_parse_complete_gts(self, minimal_xml_root):
        """Test parsing complete NIRCam GTS template."""
        xml = '''<root xmlns:ncgts="http://www.stsci.edu/JWST/APT/Template/NircamGrismTimeSeries">
            <ncgts:NircamGrismTimeSeries>
                <ncgts:Subarray>SUBSTRIP256</ncgts:Subarray>
                <ncgts:ReadoutPattern>NISRAPID</ncgts:ReadoutPattern>
                <ncgts:Groups>9</ncgts:Groups>
                <ncgts:LongPupilFilter>F322W2</ncgts:LongPupilFilter>
            </ncgts:NircamGrismTimeSeries>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_nircam_gts(templ)
        assert result["obs_mode"] == "GTS"
        assert result["obs_subarray"] == "SUBSTRIP256"
        assert result["obs_rop"] == "NISRAPID"
        assert result["obs_groups"] == "9"
        assert result["obs_opt_elem"] == "F322W2"
    
    def test_parse_gts_missing_fields(self, minimal_xml_root):
        """Test parsing GTS template with missing fields."""
        xml = '<root xmlns:ncgts="http://www.stsci.edu/JWST/APT/Template/NircamGrismTimeSeries"><ncgts:NircamGrismTimeSeries></ncgts:NircamGrismTimeSeries></root>'
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_nircam_gts(templ)
        assert result["obs_mode"] == "GTS"
        assert result["obs_subarray"] is None
        assert result["obs_rop"] is None
        assert result["obs_groups"] is None
        assert result["obs_opt_elem"] is None
    
    def test_parse_gts_filter_only(self, minimal_xml_root):
        """Test parsing GTS template with only LongPupilFilter."""
        xml = '''<root xmlns:ncgts="http://www.stsci.edu/JWST/APT/Template/NircamGrismTimeSeries">
            <ncgts:NircamGrismTimeSeries>
                <ncgts:LongPupilFilter>F322W2</ncgts:LongPupilFilter>
            </ncgts:NircamGrismTimeSeries>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_nircam_gts(templ)
        assert result["obs_mode"] == "GTS"
        assert result["obs_opt_elem"] == "F322W2"
        assert result["obs_subarray"] is None


class TestParseNirspecBots:
    """Tests for parse_nirspec_bots function."""
    
    def test_parse_complete_bots(self, minimal_xml_root):
        """Test parsing complete NIRSpec BOTS template."""
        xml = '''<root xmlns:nsbots="http://www.stsci.edu/JWST/APT/Template/NirspecBrightObjectTimeSeries">
            <nsbots:NirspecBrightObjectTimeSeries>
                <nsbots:Subarray>SUBSTRIP256</nsbots:Subarray>
                <nsbots:ReadoutPattern>NRSRAPID</nsbots:ReadoutPattern>
                <nsbots:Groups>9</nsbots:Groups>
                <nsbots:Grating>G395H</nsbots:Grating>
            </nsbots:NirspecBrightObjectTimeSeries>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_nirspec_bots(templ)
        assert result["obs_mode"] == "BOTS"
        assert result["obs_subarray"] == "SUBSTRIP256"
        assert result["obs_rop"] == "NRSRAPID"
        assert result["obs_groups"] == "9"
        assert result["obs_opt_elem"] == "G395H"
    
    def test_parse_bots_missing_fields(self, minimal_xml_root):
        """Test parsing BOTS template with missing fields."""
        xml = '<root xmlns:nsbots="http://www.stsci.edu/JWST/APT/Template/NirspecBrightObjectTimeSeries"><nsbots:NirspecBrightObjectTimeSeries></nsbots:NirspecBrightObjectTimeSeries></root>'
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_nirspec_bots(templ)
        assert result["obs_mode"] == "BOTS"
        assert result["obs_subarray"] is None
        assert result["obs_rop"] is None
        assert result["obs_groups"] is None
        assert result["obs_opt_elem"] is None
    
    def test_parse_bots_grating_only(self, minimal_xml_root):
        """Test parsing BOTS template with only Grating."""
        xml = '''<root xmlns:nsbots="http://www.stsci.edu/JWST/APT/Template/NirspecBrightObjectTimeSeries">
            <nsbots:NirspecBrightObjectTimeSeries>
                <nsbots:Grating>G395H</nsbots:Grating>
            </nsbots:NirspecBrightObjectTimeSeries>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_nirspec_bots(templ)
        assert result["obs_mode"] == "BOTS"
        assert result["obs_opt_elem"] == "G395H"
        assert result["obs_subarray"] is None


class TestParseMiriLrs:
    """Tests for parse_miri_lrs function."""
    
    def test_parse_complete_lrs(self, minimal_xml_root):
        """Test parsing complete MIRI LRS template."""
        xml = '''<root xmlns:mlrs="http://www.stsci.edu/JWST/APT/Template/MiriLRS">
            <mlrs:MiriLRS>
                <mlrs:Subarray>FULL</mlrs:Subarray>
                <mlrs:ReadoutPattern>FAST</mlrs:ReadoutPattern>
                <mlrs:Groups>5</mlrs:Groups>
            </mlrs:MiriLRS>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_miri_lrs(templ)
        assert result["obs_mode"] == "LRS"
        assert result["obs_subarray"] == "FULL"
        assert result["obs_rop"] == "FAST"
        assert result["obs_groups"] == "5"
        assert result["obs_opt_elem"] is None
    
    def test_parse_lrs_missing_fields(self, minimal_xml_root):
        """Test parsing LRS template with missing fields."""
        xml = '<root xmlns:mlrs="http://www.stsci.edu/JWST/APT/Template/MiriLRS"><mlrs:MiriLRS></mlrs:MiriLRS></root>'
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_miri_lrs(templ)
        assert result["obs_mode"] == "LRS"
        assert result["obs_subarray"] is None
        assert result["obs_rop"] is None
        assert result["obs_groups"] is None
        assert result["obs_opt_elem"] is None


class TestParseMiriImaging:
    """Tests for parse_miri_imaging function."""
    
    def test_parse_complete_imaging(self, minimal_xml_root):
        """Test parsing complete MIRI Imaging template."""
        xml = '''<root xmlns:mi="http://www.stsci.edu/JWST/APT/Template/MiriImaging">
            <mi:MiriImaging>
                <mi:Subarray>FULL</mi:Subarray>
                <mi:Filters>
                    <mi:FilterConfig>
                        <mi:ReadoutPattern>FAST</mi:ReadoutPattern>
                        <mi:Groups>5</mi:Groups>
                        <mi:Filter>F770W</mi:Filter>
                    </mi:FilterConfig>
                </mi:Filters>
            </mi:MiriImaging>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_miri_imaging(templ)
        assert result["obs_mode"] == "F770W"
        assert result["obs_subarray"] == "FULL"
        assert result["obs_rop"] == "FAST"
        assert result["obs_groups"] == "5"
        assert result["obs_opt_elem"] is None
    
    def test_parse_imaging_missing_fields(self, minimal_xml_root):
        """Test parsing Imaging template with missing fields."""
        xml = '<root xmlns:mi="http://www.stsci.edu/JWST/APT/Template/MiriImaging"><mi:MiriImaging></mi:MiriImaging></root>'
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_miri_imaging(templ)
        assert result["obs_mode"] is None
        assert result["obs_subarray"] is None
        assert result["obs_rop"] is None
        assert result["obs_groups"] is None
        assert result["obs_opt_elem"] is None
    
    def test_parse_imaging_subarray_only(self, minimal_xml_root):
        """Test parsing Imaging template with only Subarray."""
        xml = '''<root xmlns:mi="http://www.stsci.edu/JWST/APT/Template/MiriImaging">
            <mi:MiriImaging>
                <mi:Subarray>FULL</mi:Subarray>
            </mi:MiriImaging>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_miri_imaging(templ)
        assert result["obs_subarray"] == "FULL"
        assert result["obs_mode"] is None


class TestParseMiriMrs:
    """Tests for parse_miri_mrs function."""
    
    def test_parse_complete_mrs(self, minimal_xml_root):
        """Test parsing complete MIRI MRS template."""
        xml = '''<root xmlns:mmrs="http://www.stsci.edu/JWST/APT/Template/MiriMRS">
            <mmrs:MiriMRS>
                <mmrs:Subarray>FULL</mmrs:Subarray>
                <mmrs:Detector>CH1</mmrs:Detector>
                <mmrs:ExposureList>
                    <mmrs:Exposure>
                        <mmrs:ReadoutPatternLong>FAST</mmrs:ReadoutPatternLong>
                        <mmrs:GroupsLong>5</mmrs:GroupsLong>
                    </mmrs:Exposure>
                </mmrs:ExposureList>
            </mmrs:MiriMRS>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_miri_mrs(templ)
        assert result["obs_mode"] == "CH1"
        assert result["obs_subarray"] == "FULL"
        assert result["obs_rop"] == "FAST"
        assert result["obs_groups"] == "5"
        assert result["obs_opt_elem"] is None
    
    def test_parse_mrs_missing_fields(self, minimal_xml_root):
        """Test parsing MRS template with missing fields."""
        xml = '<root xmlns:mmrs="http://www.stsci.edu/JWST/APT/Template/MiriMRS"><mmrs:MiriMRS></mmrs:MiriMRS></root>'
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_miri_mrs(templ)
        assert result["obs_mode"] is None
        assert result["obs_subarray"] is None
        assert result["obs_rop"] is None
        assert result["obs_groups"] is None
        assert result["obs_opt_elem"] is None
    
    def test_parse_mrs_detector_only(self, minimal_xml_root):
        """Test parsing MRS template with only Detector."""
        xml = '''<root xmlns:mmrs="http://www.stsci.edu/JWST/APT/Template/MiriMRS">
            <mmrs:MiriMRS>
                <mmrs:Detector>CH1</mmrs:Detector>
            </mmrs:MiriMRS>
        </root>'''
        root = minimal_xml_root(xml)
        templ = root[0]
        result = parse_miri_mrs(templ)
        assert result["obs_mode"] == "CH1"
        assert result["obs_subarray"] is None


# Main Parsing Functions Tests
class TestParseTargets:
    """Tests for parse_targets function."""
    
    def test_parse_targets_from_file(self, sample_apt_file):
        """Test parsing targets from the real APT file."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        proposal_id = "2734"
        
        targets = parse_targets(root, proposal_id)
        
        assert len(targets) >= 1
        assert all("ProposalID" in target for target in targets)
        assert all(target["ProposalID"] == proposal_id for target in targets)
        
        # Check first target has expected fields
        first_target = targets[0]
        assert "Number" in first_target
        assert "TargetName" in first_target
        assert "TargetArchiveName" in first_target
        assert "TargetID" in first_target
        assert "EquatorialCoordinates" in first_target
    
    def test_parse_targets_equatorial_coordinates(self, sample_apt_file):
        """Test that EquatorialCoordinates Value attribute is extracted."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        proposal_id = "2734"
        
        targets = parse_targets(root, proposal_id)
        
        # Check that EquatorialCoordinates is extracted from Value attribute
        for target in targets:
            if target["EquatorialCoordinates"] is not None:
                assert isinstance(target["EquatorialCoordinates"], str)
                assert len(target["EquatorialCoordinates"]) > 0
    
    def test_parse_targets_all_fields(self, sample_apt_file):
        """Test that all target fields are present."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        proposal_id = "2734"
        
        targets = parse_targets(root, proposal_id)
        
        expected_fields = [
            "ProposalID", "Number", "TargetName", "TargetArchiveName",
            "TargetID", "Comments", "RAProperMotion", "DecProperMotion",
            "RAProperMotionUnits", "DecProperMotionUnits", "Epoch",
            "AnnualParallax", "Extended", "Category", "Keywords",
            "EquatorialCoordinates", "BackgroundTargetReq",
            "TargetConfirmationRun"
        ]
        
        for target in targets:
            for field in expected_fields:
                assert field in target
    
    def test_parse_targets_empty_section(self, minimal_xml_root):
        """Test parsing when Targets section is empty."""
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT"><Targets></Targets></root>'
        root = minimal_xml_root(xml)
        targets = parse_targets(root, "1234")
        assert targets == []
    
    def test_parse_targets_missing_section(self, minimal_xml_root):
        """Test parsing when Targets section is missing."""
        xml = "<root></root>"
        root = minimal_xml_root(xml)
        targets = parse_targets(root, "1234")
        assert targets == []
    
    def test_parse_targets_none_proposal_id(self, sample_apt_file):
        """Test parsing targets with None proposal_id."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        
        targets = parse_targets(root, None)
        
        # Should still parse targets but with None ProposalID
        assert len(targets) >= 1
        assert all(target["ProposalID"] is None for target in targets)


class TestParseDataRequests:
    """Tests for parse_data_requests function."""
    
    def test_parse_data_requests_from_file(self, sample_apt_file):
        """Test parsing data requests from the real APT file."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        proposal_id = "2734"
        
        observations = parse_data_requests(root, proposal_id)
        
        assert len(observations) >= 1
        assert all("ProposalID" in obs for obs in observations)
        assert all(obs["ProposalID"] == proposal_id for obs in observations)
    
    def test_parse_observation_group_label(self, sample_apt_file):
        """Test that ObservationGroup Label is extracted."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        proposal_id = "2734"
        
        observations = parse_data_requests(root, proposal_id)
        
        # Check that Label field exists
        assert all("Label" in obs for obs in observations)
    
    def test_parse_observation_fields(self, sample_apt_file):
        """Test that all observation fields are extracted."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        proposal_id = "2734"
        
        observations = parse_data_requests(root, proposal_id)
        
        expected_fields = [
            "ProposalID", "Label", "Obs_Number", "TargetID",
            "Target_Number", "Label2", "Instrument", "ObservingMode",
            "ScienceDuration", "CoordinatedParallel", "ZeroPhase",
            "Period", "PhaseStart", "PhaseEnd", "TimeSeriesObservation",
            "Subarray", "ReadoutPattern", "Groups", "GratingGrism"
        ]
        
        for obs in observations:
            for field in expected_fields:
                assert field in obs
    
    def test_parse_target_id_parsing(self, sample_apt_file):
        """Test that TargetID is parsed correctly to extract Target_Number."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        proposal_id = "2734"
        
        observations = parse_data_requests(root, proposal_id)
        
        # Check that Target_Number is extracted from TargetID
        for obs in observations:
            if obs["TargetID"] is not None and " " in obs["TargetID"]:
                assert obs["Target_Number"] is not None
    
    def test_parse_template_integration(self, sample_apt_file):
        """Test that template parsing is integrated correctly."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        proposal_id = "2734"
        
        observations = parse_data_requests(root, proposal_id)
        
        # Check that observing mode and template fields are populated
        for obs in observations:
            if obs["Instrument"] == "NIRISS":
                # Should have observing mode if template was parsed
                assert "ObservingMode" in obs
    
    def test_parse_special_requirements(self, sample_apt_file):
        """Test parsing SpecialRequirements section."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        proposal_id = "2734"
        
        observations = parse_data_requests(root, proposal_id)
        
        # Check for SpecialRequirements fields
        for obs in observations:
            assert "ZeroPhase" in obs
            assert "Period" in obs
            assert "PhaseStart" in obs
            assert "PhaseEnd" in obs
            assert "TimeSeriesObservation" in obs
    
    def test_parse_time_series_observation(self, sample_apt_file):
        """Test that TimeSeriesObservation flag is set correctly."""
        tree = ET.parse(sample_apt_file)
        root = tree.getroot()
        proposal_id = "2734"
        
        observations = parse_data_requests(root, proposal_id)
        
        # Check if any observation has TimeSeriesObservation set
        # This depends on the actual file content
        assert all(
            obs["TimeSeriesObservation"] in [None, 0, 1]
            for obs in observations
        )
    
    def test_parse_empty_data_requests(self, minimal_xml_root):
        """Test parsing when DataRequests section is empty."""
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT"><DataRequests></DataRequests></root>'
        root = minimal_xml_root(xml)
        observations = parse_data_requests(root, "1234")
        assert observations == []
    
    def test_parse_missing_data_requests(self, minimal_xml_root):
        """Test parsing when DataRequests section is missing."""
        xml = "<root></root>"
        root = minimal_xml_root(xml)
        observations = parse_data_requests(root, "1234")
        assert observations == []
    
    def test_parse_observation_group_no_label(self, minimal_xml_root):
        """Test parsing when ObservationGroup has no Label."""
        xml = '<root xmlns="http://www.stsci.edu/JWST/APT">\n            <DataRequests>\n                <ObservationGroup>\n                    <Observation>\n                        <Number>1</Number>\n                        <TargetID>1 Target</TargetID>\n                        <Instrument>NIRISS</Instrument>\n                    </Observation>\n                </ObservationGroup>\n            </DataRequests>\n        </root>'
        root = minimal_xml_root(xml)
        observations = parse_data_requests(root, "1234")
        
        assert len(observations) == 1
        assert observations[0]["Label"] == "NONE"


class TestParseAptFile:
    """Tests for parse_apt_file function."""
    
    def test_parse_apt_file_end_to_end(self, sample_apt_file):
        """Test end-to-end parsing of APT file."""
        apt_dict = parse_apt_file(sample_apt_file)
        
        # Check that all top-level fields exist
        expected_fields = [
            "ProposalPhase", "Title", "Abstract", "ProposalID",
            "StsciEditNumber", "ProposalCategory", "ProposalSize",
            "ProprietaryPeriod", "Cycle", "AllocatedTime", "ChargedTime",
            "ObservingDescription", "LastName", "Targets", "DataRequests"
        ]
        
        for field in expected_fields:
            assert field in apt_dict
    
    def test_parse_proposal_information_fields(self, sample_apt_file):
        """Test that proposal information fields are extracted."""
        apt_dict = parse_apt_file(sample_apt_file)
        
        assert apt_dict["ProposalID"] == "2734"
        assert apt_dict["Title"] is not None
        assert apt_dict["Abstract"] is not None
        assert apt_dict["Cycle"] is not None
    
    def test_parse_principal_investigator(self, sample_apt_file):
        """Test that PrincipalInvestigator LastName is extracted."""
        apt_dict = parse_apt_file(sample_apt_file)
        
        assert apt_dict["LastName"] is not None
        assert isinstance(apt_dict["LastName"], str)
    
    def test_parse_targets_integration(self, sample_apt_file):
        """Test that targets are parsed and included."""
        apt_dict = parse_apt_file(sample_apt_file)
        
        assert isinstance(apt_dict["Targets"], list)
        assert len(apt_dict["Targets"]) >= 1
    
    def test_parse_data_requests_integration(self, sample_apt_file):
        """Test that data requests are parsed and included."""
        apt_dict = parse_apt_file(sample_apt_file)
        
        assert isinstance(apt_dict["DataRequests"], list)
        assert len(apt_dict["DataRequests"]) >= 1
    
    def test_parse_missing_proposal_information(self, tmp_path):
        """Test parsing when ProposalInformation node is missing."""
        xml = "<JwstProposal></JwstProposal>"
        test_file = tmp_path / "test_apt.xml"
        test_file.write_text(xml)
        
        apt_dict = parse_apt_file(test_file)
        
        # Should return dict with all None fields
        assert apt_dict["ProposalID"] is None
        assert apt_dict["Title"] is None
        assert apt_dict["Targets"] == []
        assert apt_dict["DataRequests"] == []
    
    def test_parse_file_not_found(self):
        """Test error handling when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            parse_apt_file("nonexistent_file.xml")
    
    def test_parse_invalid_xml(self, tmp_path):
        """Test error handling with invalid XML."""
        test_file = tmp_path / "test_apt.xml"
        test_file.write_text("not valid xml")
        
        with pytest.raises(ET.ParseError):
            parse_apt_file(test_file)
    
    def test_parse_all_fields_initialized(self, sample_apt_file):
        """Test that all fields are initialized even if missing."""
        apt_dict = parse_apt_file(sample_apt_file)
        
        # All fields should exist, even if None
        assert "ProposalPhase" in apt_dict
        assert "Title" in apt_dict
        assert "Abstract" in apt_dict
        assert "ProposalID" in apt_dict
        assert "StsciEditNumber" in apt_dict
        assert "ProposalCategory" in apt_dict
        assert "ProposalSize" in apt_dict
        assert "ProprietaryPeriod" in apt_dict
        assert "Cycle" in apt_dict
        assert "AllocatedTime" in apt_dict
        assert "ChargedTime" in apt_dict
        assert "ObservingDescription" in apt_dict
        assert "LastName" in apt_dict
        assert "Targets" in apt_dict
        assert "DataRequests" in apt_dict
