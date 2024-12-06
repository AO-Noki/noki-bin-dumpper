import pytest
from pathlib import Path
from noki.utils.json_filters import JsonFilter
import json

@pytest.fixture
def temp_files(tmp_path):
    # Criar arquivos de teste temporários
    items_xml = tmp_path / "items.xml"
    items_xml.write_text("""<?xml version="1.0" encoding="utf-8"?>
    <Items>
        <Item uniquename="T4_SWORD" type="WEAPON" />
    </Items>""", encoding='utf-8')
    
    locations_xml = tmp_path / "locations.xml"
    locations_xml.write_text("""<?xml version="1.0" encoding="utf-8"?>
    <Locations>
        <Location uniquename="BLACKZONE_01" type="BLACK_ZONE" />
    </Locations>""", encoding='utf-8')
    
    emotes_xml = tmp_path / "emotes.xml"
    emotes_xml.write_text("""<?xml version="1.0" encoding="utf-8"?>
    <EmoteData>
        <Emote uniquename="EMOTE_WAVE" command="wave" loop="false" />
    </EmoteData>""", encoding='utf-8')
    
    return items_xml, locations_xml, emotes_xml

def test_process_xml(temp_files):
    _, _, emotes_file = temp_files
    output_file = emotes_file.parent / "emotes.json"
    
    JsonFilter.process_file(emotes_file, output_file)
    
    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    assert "EMOTE_WAVE" in content
    assert "wave" in content
    assert "false" in content

def test_process_items(temp_files):
    items_file, _, _ = temp_files
    output_file = items_file.parent / "items.json"
    
    JsonFilter.process_file(items_file, output_file)
    
    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    assert "T4_SWORD" in content
    assert "WEAPON" in content

def test_process_locations(temp_files):
    _, locations_file, _ = temp_files
    output_file = locations_file.parent / "locations.json"
    
    JsonFilter.process_file(locations_file, output_file)
    
    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    assert "BLACKZONE_01" in content

def test_process_accessrights(tmp_path):
    access_xml = tmp_path / "accessrights.xml"
    access_xml.write_text("""<?xml version="1.0" encoding="utf-8"?>
    <AccessRights>
        <AccessRightsIslandManagement name="AccessRightsIslandManagement">
            <owner name="owner" managesroles="coowner, builder, visitor, blacklist"/>
            <coowner name="coowner" managesroles="builder, visitor, blacklist"/>
            <builder name="builder"/>
            <visitor name="visitor"/>
            <permission name="VISIT" roles="owner, coowner, builder, visitor"/>
            <permission name="PLACE_BUILDINGS" roles="owner, coowner, builder"/>
            <access name="closed"/>
            <access name="private">
                <rule who="guild" role="visitor"/>
            </access>
        </AccessRightsIslandManagement>
    </AccessRights>""", encoding='utf-8')
    
    output_file = access_xml.parent / "accessrights.json"
    JsonFilter.process_file(access_xml, output_file)
    
    assert output_file.exists()
    content = json.loads(output_file.read_text(encoding='utf-8'))
    
    assert "accessRights" in content
    assert "AccessRightsIslandManagement" in content["accessRights"]
    management = content["accessRights"]["AccessRightsIslandManagement"]
    
    # Verifica estrutura de roles
    assert "owner" in management
    assert management["owner"]["managesroles"] == ["coowner", "builder", "visitor", "blacklist"]
    
    # Verifica permissões
    assert "permission" in management
    assert "VISIT" in management["permission"]
    assert management["permission"]["VISIT"]["roles"] == ["owner", "coowner", "builder", "visitor"]
    
    # Verifica acesso
    assert "access" in management
    assert "private" in management["access"]
    assert management["access"]["private"]["rule"]["who"] == "guild" 