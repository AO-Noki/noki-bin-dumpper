import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ValidationLogger:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.validations: List[Dict[str, Any]] = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.handlers = []
        
        # Configura logger específico para validação
        self.logger = logging.getLogger('validation')
        self.logger.setLevel(logging.INFO)
        
        # Impede a propagação dos logs para o logger root (console)
        self.logger.propagate = False
        
        # Remove handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler para arquivo
        validation_log = self.log_dir / f"validation_{self.timestamp}.log"
        fh = logging.FileHandler(validation_log, encoding='utf-8')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)
        self.handlers.append(fh)
    
    def __del__(self):
        """Garante que os handlers sejam fechados ao destruir o objeto."""
        self.close()
    
    def close(self):
        """Fecha todos os handlers de log."""
        for handler in self.handlers:
            handler.close()
            self.logger.removeHandler(handler)
        self.handlers.clear()
    
    def add_validation(self, validation: Dict[str, Any]) -> None:
        """Adiciona um resultado de validação ao log."""
        if any(v.get('file') == validation['file'] for v in self.validations):
            return
        
        validation['timestamp'] = datetime.now().isoformat()
        
        if not validation.get('match', False):
            xml_count = validation.get('xml_elements', 0)
            json_count = validation.get('json_elements', 0)
            
            file_type = 'desconhecido'
            if validation['file'].endswith('.cluster.xml'):
                file_type = 'cluster'
            elif validation['file'].endswith('.template.xml'):
                file_type = 'template'
            
            self.logger.info(
                f"Validação ({file_type}): {validation['file']} - "
                f"XML: {xml_count}, JSON: {json_count}, "
                f"{'Faltando' if xml_count > json_count else 'Extras'}: "
                f"{abs(xml_count - json_count)}"
            )
            
            if 'error' in validation:
                self.logger.error(f"Erro na validação de {validation['file']}: {validation['error']}")
            
        self.validations.append(validation)
    
    def save_report(self) -> Path:
        """Salva o relatório completo de validação."""
        try:
            validation_dir = self.log_dir / "validation"
            validation_dir.mkdir(parents=True, exist_ok=True)
            
            report_file = validation_dir / f"validation_report_{self.timestamp}.json"
            summary_file = validation_dir / f"validation_summary_{self.timestamp}.txt"
            
            summary = {
                'total_files': len(self.validations),
                'failed_validations': len([v for v in self.validations if not v.get('match', False)]),
                'total_missing_elements': sum(v.get('missing', 0) for v in self.validations),
                'validations': self.validations
            }
            
            report_file.write_text(
                json.dumps(summary, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            
            with summary_file.open('w', encoding='utf-8') as f:
                f.write(f"Relatório de Validação - {datetime.now().isoformat()}\n")
                f.write("-" * 80 + "\n\n")
                f.write(f"Total de arquivos processados: {summary['total_files']}\n")
                f.write(f"Validações com falha: {summary['failed_validations']}\n")
                f.write(f"Total de elementos faltando: {summary['total_missing_elements']}\n")
            
            return report_file
            
        finally:
            # Fecha os handlers antes de finalizar
            self.close()
    
    def save_detailed_report(self) -> Path:
        """Gera um relatório detalhado com análise por categoria."""
        report_file = self.log_dir / f"detailed_validation_{self.timestamp}.txt"
        
        with report_file.open('w', encoding='utf-8') as f:
            f.write("=== Relatório Detalhado de Validação ===\n\n")
            
            # Agrupa por categoria
            by_category = {'CLUSTER': [], 'TEMPLATE': [], 'CONFIG': []}
            for v in self.validations:
                if v['file'].endswith('.cluster.xml'):
                    by_category['CLUSTER'].append(v)
                elif v['file'].endswith('.template.xml'):
                    by_category['TEMPLATE'].append(v)
                else:
                    by_category['CONFIG'].append(v)
            
            # Análise por categoria
            for category, validations in by_category.items():
                f.write(f"\n=== {category} Files ===\n")
                f.write(f"Total arquivos: {len(validations)}\n")
                f.write(f"Arquivos com diferenças: {len([v for v in validations if not v['match']])}\n")
                
                # Estatísticas detalhadas
                xml_counts = [v['xml_elements'] for v in validations]
                json_counts = [v['json_elements'] for v in validations]
                
                f.write(f"Média elementos XML: {sum(xml_counts)/len(xml_counts):.2f}\n")
                f.write(f"Média elementos JSON: {sum(json_counts)/len(json_counts):.2f}\n")
        
        return report_file