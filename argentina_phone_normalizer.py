import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import json
from datetime import datetime
import logging

class ArgentinaPhoneNormalizer:
    def __init__(self):
        self.setup_logging()
        
        # Códigos de área de Argentina
        self.area_codes = {
            # CABA y Gran Buenos Aires
            '11': {'type': 'mobile_landline', 'region': 'CABA_GBA', 'operator': 'mixed'},
            
            # Códigos de área por provincia
            '220': {'type': 'landline', 'region': 'Buenos_Aires', 'operator': 'landline'},
            '221': {'type': 'landline', 'region': 'La_Plata', 'operator': 'landline'},
            '223': {'type': 'landline', 'region': 'Mar_del_Plata', 'operator': 'landline'},
            '236': {'type': 'landline', 'region': 'Junin', 'operator': 'landline'},
            '237': {'type': 'landline', 'region': 'Tandil', 'operator': 'landline'},
            '249': {'type': 'landline', 'region': 'Azul', 'operator': 'landline'},
            '261': {'type': 'landline', 'region': 'Mendoza', 'operator': 'landline'},
            '264': {'type': 'landline', 'region': 'San_Juan', 'operator': 'landline'},
            '266': {'type': 'landline', 'region': 'San_Luis', 'operator': 'landline'},
            '280': {'type': 'landline', 'region': 'Viedma', 'operator': 'landline'},
            '291': {'type': 'landline', 'region': 'Bahia_Blanca', 'operator': 'landline'},
            '294': {'type': 'landline', 'region': 'San_Carlos_Bariloche', 'operator': 'landline'},
            '297': {'type': 'landline', 'region': 'Comodoro_Rivadavia', 'operator': 'landline'},
            '298': {'type': 'landline', 'region': 'Neuquen', 'operator': 'landline'},
            '299': {'type': 'landline', 'region': 'Zapala', 'operator': 'landline'},
            
            # Córdoba
            '351': {'type': 'landline', 'region': 'Cordoba_Capital', 'operator': 'landline'},
            '353': {'type': 'landline', 'region': 'Villa_Maria', 'operator': 'landline'},
            '354': {'type': 'landline', 'region': 'Bell_Ville', 'operator': 'landline'},
            '358': {'type': 'landline', 'region': 'Rio_Cuarto', 'operator': 'landline'},
            
            # Santa Fe
            '341': {'type': 'landline', 'region': 'Rosario', 'operator': 'landline'},
            '342': {'type': 'landline', 'region': 'Santa_Fe_Capital', 'operator': 'landline'},
            '343': {'type': 'landline', 'region': 'Parana', 'operator': 'landline'},
            
            # Norte
            '381': {'type': 'landline', 'region': 'Tucuman', 'operator': 'landline'},
            '383': {'type': 'landline', 'region': 'Catamarca', 'operator': 'landline'},
            '385': {'type': 'landline', 'region': 'Santiago_del_Estero', 'operator': 'landline'},
            '387': {'type': 'landline', 'region': 'Salta', 'operator': 'landline'},
            '388': {'type': 'landline', 'region': 'Jujuy', 'operator': 'landline'},
        }
        
        # Rangos de números móviles por operador
        self.mobile_operators = {
            'Personal': {
                'prefixes': ['15-2', '15-3'],
                'ranges': [
                    (1150000000, 1159999999),
                    (1152000000, 1159999999)
                ]
            },
            'Movistar': {
                'prefixes': ['15-1', '15-6', '15-7'],
                'ranges': [
                    (1151000000, 1151999999),
                    (1156000000, 1157999999)
                ]
            },
            'Claro': {
                'prefixes': ['15-4', '15-5', '15-9'],
                'ranges': [
                    (1154000000, 1155999999),
                    (1159000000, 1159999999)
                ]
            }
        }
        
        # Patrones de validación
        self.patterns = {
            'with_country': re.compile(r'^(\+54|0054|54)[-\s]?(.+)$'),
            'area_code': re.compile(r'^(\d{2,4})[-\s]?(.+)$'),
            'mobile_format': re.compile(r'^9[-\s]?(\d{2,4})[-\s]?15[-\s]?(.+)$'),
            'landline_format': re.compile(r'^(\d{2,4})[-\s]?(\d{6,8})$'),
            'clean_number': re.compile(r'[^\d]'),
        }
    
    def setup_logging(self):
        """Configurar sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def clean_input(self, phone_number: str) -> str:
        """Limpia el input removiendo caracteres especiales"""
        if not phone_number or not isinstance(phone_number, str):
            return ""
        
        # Remover espacios al inicio y final
        cleaned = phone_number.strip()
        
        # Remover caracteres comunes de formateo pero mantener + al inicio
        cleaned = re.sub(r'[\(\)\-\s\.]', '', cleaned)
        
        return cleaned
    
    def extract_country_code(self, phone_number: str) -> Tuple[str, str]:
        """Extrae código de país si existe"""
        match = self.patterns['with_country'].match(phone_number)
        if match:
            country_code = match.group(1)
            remaining_number = match.group(2)
            return country_code, remaining_number
        
        return "", phone_number
    
    def identify_number_type(self, number: str) -> Dict[str, str]:
        """Identifica si es móvil o fijo y extrae componentes"""
        # Limpiar número
        clean_number = self.patterns['clean_number'].sub('', number)
        
        # Verificar formato móvil (9 + código área + 15 + número)
        mobile_match = self.patterns['mobile_format'].match(number)
        if mobile_match:
            area_code = mobile_match.group(1)
            local_number = mobile_match.group(2)
            
            return {
                'type': 'mobile',
                'area_code': area_code,
                'local_number': local_number,
                'full_clean': clean_number
            }
        
        # Verificar formato fijo
        if len(clean_number) >= 8:
            # Intentar extraer código de área (2-4 dígitos)
            for area_len in [2, 3, 4]:
                potential_area = clean_number[:area_len]
                potential_local = clean_number[area_len:]
                
                if potential_area in self.area_codes and len(potential_local) >= 6:
                    return {
                        'type': 'landline',
                        'area_code': potential_area,
                        'local_number': potential_local,
                        'full_clean': clean_number
                    }
        
        # Si no coincide con patrones conocidos
        return {
            'type': 'unknown',
            'area_code': '',
            'local_number': clean_number,
            'full_clean': clean_number
        }
    
    def validate_area_code(self, area_code: str, number_type: str) -> bool:
        """Valida si el código de área es correcto"""
        if not area_code:
            return False
        
        if area_code in self.area_codes:
            area_info = self.area_codes[area_code]
            
            # Validar que el tipo coincida
            if number_type == 'mobile' and area_info['type'] not in ['mobile_landline', 'mobile']:
                return False
            if number_type == 'landline' and area_info['type'] not in ['mobile_landline', 'landline']:
                return False
            
            return True
        
        return False
    
    def detect_mobile_operator(self, area_code: str, local_number: str) -> str:
        """Detecta el operador móvil basado en el número"""
        if area_code == '11':  # CABA/GBA
            # Construir número completo para análisis
            full_number = int(f"11{local_number}")
            
            for operator, info in self.mobile_operators.items():
                for min_range, max_range in info['ranges']:
                    if min_range <= full_number <= max_range:
                        return operator
        
        return 'Unknown'
    
    def normalize_phone_number(self, phone_number: Union[str, int, float]) -> Dict[str, any]:
        """
        Función principal que normaliza un número telefónico argentino
        """
        result = {
            'original': phone_number,
            'normalized': '',
            'is_valid': False,
            'type': '',
            'area_code': '',
            'local_number': '',
            'operator': '',
            'region': '',
            'format_e164': '',
            'format_national': '',
            'format_international': '',
            'errors': []
        }
        
        try:
            # Convertir a string si es necesario
            if isinstance(phone_number, (int, float)):
                phone_str = str(int(phone_number))
            else:
                phone_str = str(phone_number) if phone_number else ""
            
            if not phone_str or phone_str.lower() in ['nan', 'none', '']:
                result['errors'].append("Número vacío o inválido")
                return result
            
            # Limpiar input
            cleaned = self.clean_input(phone_str)
            if not cleaned:
                result['errors'].append("Número inválido después de limpieza")
                return result
            
            # Extraer código de país
            country_code, remaining = self.extract_country_code(cleaned)
            
            # Identificar tipo de número
            number_info = self.identify_number_type(remaining)
            
            # Validar código de área
            if not self.validate_area_code(number_info['area_code'], number_info['type']):
                result['errors'].append(f"Código de área inválido: {number_info['area_code']}")
                return result
            
            # Validar longitud del número local
            local_length = len(number_info['local_number'])
            if number_info['type'] == 'mobile' and local_length not in [7, 8]:
                result['errors'].append(f"Longitud inválida para móvil: {local_length} dígitos")
                return result
            
            if number_info['type'] == 'landline' and local_length not in [6, 7, 8]:
                result['errors'].append(f"Longitud inválida para fijo: {local_length} dígitos")
                return result
            
            # Si llegamos aquí, el número es válido
            result['is_valid'] = True
            result['type'] = number_info['type']
            result['area_code'] = number_info['area_code']
            result['local_number'] = number_info['local_number']
            
            # Obtener información adicional
            if number_info['area_code'] in self.area_codes:
                area_info = self.area_codes[number_info['area_code']]
                result['region'] = area_info['region']
                
                # Detectar operador para móviles
                if number_info['type'] == 'mobile':
                    result['operator'] = self.detect_mobile_operator(
                        number_info['area_code'], 
                        number_info['local_number']
                    )
                else:
                    result['operator'] = 'Landline'
            
            # Generar formatos normalizados
            if number_info['type'] == 'mobile':
                result['format_e164'] = f"+549{result['area_code']}{result['local_number']}"
                result['format_national'] = f"15-{result['area_code']}-{result['local_number']}"
                result['format_international'] = f"+54 9 {result['area_code']} {result['local_number']}"
            else:
                result['format_e164'] = f"+54{result['area_code']}{result['local_number']}"
                result['format_national'] = f"{result['area_code']}-{result['local_number']}"
                result['format_international'] = f"+54 {result['area_code']} {result['local_number']}"
            
            result['normalized'] = result['format_e164']
            
        except Exception as e:
            result['errors'].append(f"Error de procesamiento: {str(e)}")
            self.logger.error(f"Error procesando {phone_number}: {str(e)}")
        
        return result
    
    def batch_normalize(self, phone_numbers: List[Union[str, int, float]]) -> pd.DataFrame:
        """Normaliza una lista de números telefónicos"""
        results = []
        
        for i, number in enumerate(phone_numbers):
            if i % 1000 == 0:
                self.logger.info(f"Procesando número {i+1}/{len(phone_numbers)}")
            
            result = self.normalize_phone_number(number)
            results.append(result)
        
        return pd.DataFrame(results)
    
    def validate_csv_file(self, file_path: str, phone_column: str) -> pd.DataFrame:
        """Procesa un archivo CSV con números telefónicos"""
        try:
            df = pd.read_csv(file_path)
            
            if phone_column not in df.columns:
                raise ValueError(f"Columna '{phone_column}' no encontrada en el archivo")
            
            self.logger.info(f"Procesando {len(df)} números del archivo {file_path}")
            
            # Normalizar números
            normalized_results = self.batch_normalize(df[phone_column].tolist())
            
            # Combinar con datos originales
            result_df = pd.concat([df, normalized_results], axis=1)
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"Error procesando archivo: {str(e)}")
            raise
    
    def generate_report(self, results_df: pd.DataFrame) -> Dict[str, any]:
        """Genera reporte de estadísticas de normalización"""
        total_numbers = len(results_df)
        valid_numbers = len(results_df[results_df['is_valid'] == True])
        
        report = {
            'total_numbers': total_numbers,
            'valid_numbers': valid_numbers,
            'invalid_numbers': total_numbers - valid_numbers,
            'validity_rate': (valid_numbers / total_numbers * 100) if total_numbers > 0 else 0,
            'type_distribution': results_df['type'].value_counts().to_dict(),
            'operator_distribution': results_df[results_df['is_valid']]['operator'].value_counts().to_dict(),
            'region_distribution': results_df[results_df['is_valid']]['region'].value_counts().to_dict(),
            'common_errors': [],
            'processed_at': datetime.now().isoformat()
        }
        
        # Analizar errores comunes
        error_counts = {}
        for errors in results_df['errors']:
            if errors:  # Si hay errores
                for error in errors:
                    error_counts[error] = error_counts.get(error, 0) + 1
        
        report['common_errors'] = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        return report
    
    def save_results(self, results_df: pd.DataFrame, output_path: str):
        """Guarda resultados en archivo CSV"""
        results_df.to_csv(output_path, index=False, encoding='utf-8')
        self.logger.info(f"Resultados guardados en: {output_path}")

def main():
    """Función principal de ejemplo"""
    print("=== NORMALIZADOR DE NÚMEROS TELEFÓNICOS ARGENTINOS ===\n")
    
    # Inicializar normalizador
    normalizer = ArgentinaPhoneNormalizer()
    
    # Ejemplos de números para probar
    test_numbers = [
        "+54 11 1234-5678",      # Móvil CABA formato internacional
        "011 15-1234-5678",      # Móvil CABA formato nacional
        "11-1234-5678",          # Fijo CABA
        "+54 221 456-7890",      # Fijo La Plata
        "0221-456-7890",         # Fijo La Plata con 0
        "54 9 11 1234 5678",     # Móvil formato alternativo
        "1123456789",            # Número sin formatear
        "invalid_number",        # Número inválido
        "",                      # Número vacío
        "999999999999999",       # Número muy largo
    ]
    
    print("Probando números de ejemplo:")
    print("-" * 80)
    
    results = []
    for number in test_numbers:
        result = normalizer.normalize_phone_number(number)
        results.append(result)
        
        print(f"Original: {number}")
        print(f"Válido: {result['is_valid']}")
        if result['is_valid']:
            print(f"Tipo: {result['type']}")
            print(f"Normalizado: {result['normalized']}")
            print(f"Operador: {result['operator']}")
            print(f"Región: {result['region']}")
        else:
            print(f"Errores: {', '.join(result['errors'])}")
        print("-" * 80)
    
    # Crear DataFrame con resultados
    results_df = pd.DataFrame(results)
    
    # Generar reporte
    report = normalizer.generate_report(results_df)
    
    print("\n=== REPORTE DE NORMALIZACIÓN ===")
    print(f"Total de números: {report['total_numbers']}")
    print(f"Números válidos: {report['valid_numbers']}")
    print(f"Números inválidos: {report['invalid_numbers']}")
    print(f"Tasa de validez: {report['validity_rate']:.2f}%")
    
    print(f"\nDistribución por tipo:")
    for type_name, count in report['type_distribution'].items():
        print(f"  {type_name}: {count}")
    
    print(f"\nDistribución por operador:")
    for operator, count in report['operator_distribution'].items():
        print(f"  {operator}: {count}")
    
    print(f"\nErrores comunes:")
    for error, count in report['common_errors'][:5]:  # Top 5 errores
        print(f"  {error}: {count} veces")
    
    # Guardar resultados
    normalizer.save_results(results_df, 'normalized_phones_test.csv')
    
    # Guardar reporte
    with open('normalization_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nReporte guardado en: normalization_report.json")
    print("Prueba completada exitosamente!")

if __name__ == "__main__":
    main()