import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

def parse_value(value: str) -> Any:
    """Converte string para tipo apropriado mantendo consistência com ao-bin-dumps."""
    if not isinstance(value, str):
        return value
    if value.lower() == 'true': return True
    if value.lower() == 'false': return False
    if ',' in value and all(v.strip().isalpha() for v in value.split(',')):
        return [v.strip() for v in value.split(',')]
    try:
        if '.' in value: return float(value)
        return int(value)
    except ValueError:
        return value

def clean_xml_content(content: str) -> str:
    """Limpa e valida o conteúdo XML antes do parsing."""
    # Remove BOM se presente
    content = content.strip('\ufeff')
    
    # Remove caracteres inválidos
    content = ''.join(char for char in content if ord(char) < 0xD800 or ord(char) > 0xDFFF)
    
    # Verifica se tem um elemento raiz
    if not content.strip().startswith('<?xml') and not content.strip().startswith('<'):
        content = f'<?xml version="1.0" encoding="utf-8"?><root>{content}</root>'
        
    return content

def element_to_dict(element: ET.Element) -> Dict[str, Any]:
    """Converte elemento XML em dict seguindo padrão do ao-bin-dumps."""
    result = {}
    
    # Caso especial para avatars e avatarrings
    if element.tag.endswith('avatars'):
        result = {
            "avatars": [],
            "peraccountavatars": [],
            "avatarrings": [],
            "peraccountavatarrings": []
        }
        
        # Processa avatars normais
        for avatar in element.findall('.//avatar'):
            parent_path = element.findall(f'.//*/{avatar.tag}/..')[0].tag
            if parent_path.endswith('peraccountavatars'):
                target_list = result['peraccountavatars']
            else:
                target_list = result['avatars']
                
            avatar_data = {}
            for key, value in avatar.attrib.items():
                if ':' not in key:
                    if key in ('locked', 'hidden'):
                        avatar_data[key] = value.lower() == 'true'
                    else:
                        avatar_data[key] = value
            target_list.append(avatar_data)
        
        # Processa avatarrings
        for ring in element.findall('.//avatarring'):
            parent_path = element.findall(f'.//*/{ring.tag}/..')[0].tag
            if parent_path.endswith('peraccountavatarrings'):
                target_list = result['peraccountavatarrings']
            else:
                target_list = result['avatarrings']
                
            ring_data = {}
            for key, value in ring.attrib.items():
                if ':' not in key:
                    if key in ('locked', 'hidden'):
                        ring_data[key] = value.lower() == 'true'
                    else:
                        ring_data[key] = value
            target_list.append(ring_data)
        
        # Remove listas vazias
        return {k: v for k, v in result.items() if v}
    
    # Processamento normal para outros elementos
    if element.attrib:
        for key, value in element.attrib.items():
            if ':' not in key:
                result[key] = parse_value(value)
                
    # Processa elementos filhos
    for child in element:
        tag = child.tag.split('}')[-1].lower()
        child_data = element_to_dict(child)
        
        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(child_data)
        else:
            result[tag] = child_data
            
    return result

def validate_json_output(xml_path: Path, json_path: Path) -> Dict[str, Any]:
    """Valida se o JSON gerado mantém todos os dados do XML original."""
    try:
        # Carrega o XML original
        xml_content = xml_path.read_text(encoding='utf-8-sig')
        cleaned_xml = clean_xml_content(xml_content)
        xml_root = ET.fromstring(cleaned_xml)
        
        # Carrega o JSON gerado
        json_content = json_path.read_text(encoding='utf-8')
        json_data = json.loads(json_content)
        
        # Análise detalhada
        xml_analysis = analyze_xml_structure(xml_root)
        json_analysis = analyze_json_structure(json_data)
        
        validation = {
            'file': xml_path.name,
            'xml_elements': xml_analysis['total_elements'],
            'json_elements': json_analysis['total_elements'],
            'xml_analysis': xml_analysis,
            'json_analysis': json_analysis,
            'match': xml_analysis['total_elements'] == json_analysis['total_elements'],
            'missing': xml_analysis['total_elements'] - json_analysis['total_elements'] if xml_analysis['total_elements'] > json_analysis['total_elements'] else 0,
            'extra': json_analysis['total_elements'] - xml_analysis['total_elements'] if json_analysis['total_elements'] > xml_analysis['total_elements'] else 0
        }
        
        # Mudando para debug ao invés de warning/info
        if not validation['match']:
            logger.debug(
                f"Validação ({xml_path.name}): "
                f"XML: {validation['xml_elements']}, "
                f"JSON: {validation['json_elements']}, "
                f"{'Faltando' if validation['missing'] else 'Extras'}: "
                f"{validation['missing'] or validation['extra']}"
            )
        
        return validation
        
    except Exception as e:
        logger.debug(f"Erro ao validar {xml_path}: {e}")
        return {
            'file': xml_path.name,
            'error': str(e),
            'match': False
        }

def analyze_xml_structure(root: ET.Element) -> Dict[str, Any]:
    """Analisa a estrutura do XML em detalhes."""
    analysis = {
        'total_elements': 0,
        'elements_with_text': 0,
        'elements_with_attrs': 0,
        'depth': 0
    }
    
    def analyze_element(elem: ET.Element, depth: int):
        analysis['total_elements'] += 1
        if elem.text and elem.text.strip():
            analysis['elements_with_text'] += 1
        if elem.attrib:
            analysis['elements_with_attrs'] += 1
        analysis['depth'] = max(analysis['depth'], depth)
        
        for child in elem:
            analyze_element(child, depth + 1)
    
    analyze_element(root, 0)
    return analysis

def analyze_json_structure(data: Any) -> Dict[str, Any]:
    """Analisa a estrutura do JSON em detalhes."""
    analysis = {
        'total_elements': 0,
        'leaf_nodes': 0,
        'array_elements': 0,
        'depth': 0
    }
    
    def analyze_value(value: Any, depth: int):
        analysis['depth'] = max(analysis['depth'], depth)
        
        if isinstance(value, dict):
            analysis['total_elements'] += 1
            for v in value.values():
                analyze_value(v, depth + 1)
        elif isinstance(value, list):
            analysis['total_elements'] += 1
            for item in value:
                analyze_value(item, depth + 1)
        else:
            analysis['leaf_nodes'] += 1
    
    analyze_value(data, 0)
    return analysis

class JsonFilter:
    """Classe responsável por filtrar e transformar dados em JSON."""
    
    @staticmethod
    def process_file(input_path: Path, output_path: Path) -> Dict[str, Any]:
        """Processa arquivo de entrada e salva como JSON, retornando validação."""
        if input_path.suffix.lower() == '.xml':
            data = JsonFilter._process_xml(input_path)
        else:
            data = JsonFilter._process_default(input_path)
            
        # Salva o resultado
        output_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        # Valida o resultado
        if input_path.suffix.lower() == '.xml':
            return validate_json_output(input_path, output_path)
        return {'file': input_path.name, 'match': True}

    @staticmethod
    def _process_xml(file_path: Path) -> Dict[str, Any]:
        """Processa arquivos XML de forma consistente."""
        try:
            content = file_path.read_text(encoding='utf-8-sig')
            
            # Tratamento especial para arquivos de profanidade
            if 'profanity_' in file_path.name:
                return {
                    "words": [
                        line.strip() 
                        for line in content.splitlines() 
                        if line.strip() and not line.startswith('<?xml')
                    ]
                }
            
            cleaned_content = clean_xml_content(content)
            root = ET.fromstring(cleaned_content)
            
            # Pega o nome da tag raiz sem namespace
            root_tag = root.tag.split('}')[-1].lower()
            
            # Processa o conteúdo
            data = element_to_dict(root)
            
            # Retorna com a tag raiz
            return {root_tag: data}
            
        except Exception as e:
            logger.error(f"Erro ao processar XML {file_path}: {e}")
            raise

    @staticmethod
    def _process_default(file_path: Path) -> Dict[str, Any]:
        """Processa arquivos genéricos."""
        content = file_path.read_text(encoding='utf-8')
        return {
            "filename": file_path.name,
            "content": [line for line in content.splitlines() if line.strip() and not line.startswith('@')]
        }