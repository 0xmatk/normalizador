import pandas as pd
import numpy as np
from argentina_phone_normalizer import ArgentinaPhoneNormalizer
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def procesar_telefonos():
    """Procesa el archivo llamadas.csv y normaliza todos los números"""
    
    print("=== PROCESADOR DE TELEFONOS ARGENTINOS ===\n")
    
    # Inicializar normalizador
    normalizer = ArgentinaPhoneNormalizer()
    
    try:
        # Cargar archivo
        print("1. Cargando archivo llamadas.csv...")
        df = pd.read_csv('llamadas.csv')
        
        if 'TELEFONO' not in df.columns:
            print("Error: No se encontró la columna 'TELEFONO' en el archivo")
            return
        
        print(f"   Total números encontrados: {len(df)}")
        
        # Mostrar muestra de números
        print(f"\n2. Muestra de números originales:")
        for i, numero in enumerate(df['TELEFONO'].head(10)):
            print(f"   {i+1:2d}. {numero}")
        
        # Procesar números
        print(f"\n3. Normalizando {len(df)} números telefónicos...")
        
        results = []
        processed = 0
        
        for i, phone in enumerate(df['TELEFONO']):
            if i % 500 == 0:
                print(f"   Progreso: {i}/{len(df)} ({i/len(df)*100:.1f}%)")
            
            result = normalizer.normalize_phone_number(phone)
            results.append(result)
            processed += 1
        
        print(f"   Completado: {processed}/{len(df)} números procesados")
        
        # Crear DataFrame con resultados
        results_df = pd.DataFrame(results)
        
        # Combinar con datos originales
        df_final = pd.concat([df.reset_index(drop=True), results_df], axis=1)
        
        # Estadísticas generales
        print(f"\n4. Estadísticas de normalización:")
        
        total_numeros = len(df_final)
        numeros_validos = len(df_final[df_final['is_valid'] == True])
        numeros_invalidos = total_numeros - numeros_validos
        
        print(f"   Total números: {total_numeros}")
        print(f"   Números válidos: {numeros_validos} ({numeros_validos/total_numeros*100:.1f}%)")
        print(f"   Números inválidos: {numeros_invalidos} ({numeros_invalidos/total_numeros*100:.1f}%)")
        
        # Análisis de números válidos
        if numeros_validos > 0:
            df_validos = df_final[df_final['is_valid'] == True]
            
            print(f"\n5. Análisis de números válidos:")
            
            # Por tipo de número
            tipos = df_validos['type'].value_counts()
            print(f"   Distribución por tipo:")
            for tipo, cantidad in tipos.items():
                print(f"     {tipo}: {cantidad} ({cantidad/numeros_validos*100:.1f}%)")
            
            # Por operador
            operadores = df_validos['operator'].value_counts()
            print(f"\n   Distribución por operador:")
            for operador, cantidad in operadores.items():
                print(f"     {operador}: {cantidad} ({cantidad/numeros_validos*100:.1f}%)")
            
            # Por región
            regiones = df_validos['region'].value_counts()
            print(f"\n   Top 10 regiones:")
            for region, cantidad in regiones.head(10).items():
                print(f"     {region.replace('_', ' ')}: {cantidad}")
        
        # Análisis de errores
        if numeros_invalidos > 0:
            print(f"\n6. Análisis de números inválidos:")
            
            error_counts = {}
            for errors in df_final['errors']:
                if errors:
                    for error in errors:
                        error_counts[error] = error_counts.get(error, 0) + 1
            
            print(f"   Errores más frecuentes:")
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"     {error}: {count} números")
        
        # Crear carpeta de reportes si no existe
        import os
        os.makedirs('reportes', exist_ok=True)
        
        # Guardar archivos
        print(f"\n7. Guardando resultados...")
        
        # Archivo completo
        output_completo = 'reportes/telefonos_procesados_completo.csv'
        df_final.to_csv(output_completo, index=False, encoding='utf-8')
        print(f"   ✓ Archivo completo: {output_completo}")
        
        # Solo números válidos normalizados
        if numeros_validos > 0:
            df_validos_clean = df_validos[['TELEFONO', 'normalized', 'type', 'operator', 'region', 'format_e164', 'format_national']].copy()
            df_validos_clean.rename(columns={
                'TELEFONO': 'numero_original',
                'normalized': 'numero_normalizado',
                'type': 'tipo',
                'operator': 'operador',
                'region': 'region',
                'format_e164': 'formato_internacional',
                'format_national': 'formato_nacional'
            }, inplace=True)
            
            output_limpios = 'reportes/telefonos_validos.csv'
            df_validos_clean.to_csv(output_limpios, index=False, encoding='utf-8')
            print(f"   ✓ Solo números válidos: {output_limpios}")
        
        # Lista simple de números para llamar desde Argentina
        if numeros_validos > 0:
            # Formato para llamadas desde Argentina (sin +54)
            numeros_para_marcar = []
            
            for _, row in df_validos.iterrows():
                if row['type'] == 'mobile':
                    # Móviles: 15 + código área + número local
                    numero_nacional = f"15{row['area_code']}{row['local_number']}"
                else:
                    # Fijos: código área + número local
                    numero_nacional = f"{row['area_code']}{row['local_number']}"
                
                numeros_para_marcar.append(numero_nacional)
            
            # Guardar formato para marcar desde Argentina
            df_marcar = pd.DataFrame({'TELEFONO_PARA_MARCAR': numeros_para_marcar})
            output_marcar = 'telefonos_para_marcar_argentina.csv'
            df_marcar.to_csv(output_marcar, index=False, encoding='utf-8')
            print(f"   ✓ Para marcar desde Argentina: {output_marcar}")
            
            # Guardar como TXT (uno por línea)
            output_marcar_txt = 'telefonos_para_marcar_argentina.txt'
            with open(output_marcar_txt, 'w', encoding='utf-8') as f:
                for numero in numeros_para_marcar:
                    f.write(f"{numero}\n")
            print(f"   ✓ Lista TXT para marcar: {output_marcar_txt}")
            
            # También mantener formato internacional (por si acaso)
            numeros_internacionales = df_validos['normalized'].tolist()
            df_internacional = pd.DataFrame({'TELEFONO_INTERNACIONAL': numeros_internacionales})
            output_internacional = 'reportes/telefonos_formato_internacional.csv'
            df_internacional.to_csv(output_internacional, index=False, encoding='utf-8')
            print(f"   ✓ Formato internacional: {output_internacional}")
        
        # Números problemáticos
        if numeros_invalidos > 0:
            df_problemas = df_final[df_final['is_valid'] == False][['TELEFONO', 'errors']].copy()
            output_problemas = 'reportes/telefonos_con_problemas.csv'
            df_problemas.to_csv(output_problemas, index=False, encoding='utf-8')
            print(f"   ✓ Números con problemas: {output_problemas}")
        
        # Reporte JSON
        reporte = {
            'fecha_procesamiento': datetime.now().isoformat(),
            'total_numeros': total_numeros,
            'numeros_validos': numeros_validos,
            'numeros_invalidos': numeros_invalidos,
            'porcentaje_validez': round(numeros_validos/total_numeros*100, 2),
            'distribucion_tipos': tipos.to_dict() if numeros_validos > 0 else {},
            'distribucion_operadores': operadores.to_dict() if numeros_validos > 0 else {},
            'distribucion_regiones': regiones.to_dict() if numeros_validos > 0 else {},
            'errores_frecuentes': sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10] if numeros_invalidos > 0 else []
        }
        
        output_reporte = 'reportes/reporte_procesamiento.json'
        with open(output_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        print(f"   ✓ Reporte detallado: {output_reporte}")
        
        # Crear visualizaciones
        print(f"\n8. Generando gráficos...")
        crear_graficos(df_final, numeros_validos, numeros_invalidos)
        
        # Resumen final
        print(f"\n" + "="*50)
        print(f"PROCESAMIENTO COMPLETADO")
        print(f"="*50)
        print(f"📊 Números procesados: {total_numeros}")
        print(f"✅ Números válidos: {numeros_validos} ({numeros_validos/total_numeros*100:.1f}%)")
        print(f"❌ Números inválidos: {numeros_invalidos} ({numeros_invalidos/total_numeros*100:.1f}%)")
        
        if numeros_validos > 0:
            print(f"\n📱 Tipos encontrados:")
            for tipo, cantidad in tipos.items():
                print(f"   {tipo}: {cantidad}")
            
            print(f"\n🏢 Operadores encontrados:")
            for operador, cantidad in operadores.items():
                print(f"   {operador}: {cantidad}")
        
        print(f"\n📁 Archivos generados:")
        print(f"   • {output_completo}")
        if numeros_validos > 0:
            print(f"   • {output_limpios}")
            print(f"   • {output_marcar} ⭐ PRINCIPAL PARA LLAMAR")
            print(f"   • {output_marcar_txt}")
            print(f"   • {output_internacional}")
        if numeros_invalidos > 0:
            print(f"   • {output_problemas}")
        print(f"   • {output_reporte}")
        print(f"   • reportes/graficos_procesamiento.png")
        
        return df_final, reporte
        
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'llamadas.csv'")
        print("   Asegúrate de que el archivo esté en el directorio actual.")
        return None, None
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {str(e)}")
        return None, None

def crear_graficos(df_final, numeros_validos, numeros_invalidos):
    """Crea gráficos del procesamiento"""
    
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Gráfico de validez general
    ax1 = axes[0, 0]
    labels = ['Válidos', 'Inválidos']
    sizes = [numeros_validos, numeros_invalidos]
    colors = ['#2ecc71', '#e74c3c']
    
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title('Validez de Números Telefónicos', fontsize=14, fontweight='bold')
    
    # 2. Distribución por tipo (solo válidos)
    ax2 = axes[0, 1]
    if numeros_validos > 0:
        df_validos = df_final[df_final['is_valid'] == True]
        tipos = df_validos['type'].value_counts()
        
        colors_tipo = ['#3498db', '#9b59b6', '#f39c12']
        bars = ax2.bar(tipos.index, tipos.values, color=colors_tipo[:len(tipos)])
        ax2.set_title('Distribución por Tipo de Número', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Cantidad')
        ax2.tick_params(axis='x', rotation=45)
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
    else:
        ax2.text(0.5, 0.5, 'No hay números\nvástalidos para mostrar', 
                ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Distribución por Tipo de Número', fontsize=14, fontweight='bold')
    
    # 3. Top operadores
    ax3 = axes[1, 0]
    if numeros_validos > 0:
        operadores = df_validos['operator'].value_counts().head(5)
        
        colors_op = ['#1abc9c', '#e67e22', '#8e44ad', '#2c3e50', '#d35400']
        bars = ax3.bar(operadores.index, operadores.values, color=colors_op[:len(operadores)])
        ax3.set_title('Top 5 Operadores', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Cantidad')
        ax3.tick_params(axis='x', rotation=45)
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
    else:
        ax3.text(0.5, 0.5, 'No hay datos de\noperadores disponibles', 
                ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Top 5 Operadores', fontsize=14, fontweight='bold')
    
    # 4. Top regiones
    ax4 = axes[1, 1]
    if numeros_validos > 0:
        regiones = df_validos['region'].value_counts().head(5)
        
        colors_reg = ['#27ae60', '#f1c40f', '#e74c3c', '#3498db', '#9b59b6']
        bars = ax4.barh(regiones.index, regiones.values, color=colors_reg[:len(regiones)])
        ax4.set_title('Top 5 Regiones', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Cantidad')
        
        # Limpiar nombres de región
        labels = [region.replace('_', ' ').title() for region in regiones.index]
        ax4.set_yticklabels(labels)
        
        # Añadir valores en las barras
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax4.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{int(width)}', ha='left', va='center')
    else:
        ax4.text(0.5, 0.5, 'No hay datos de\nregiones disponibles', 
                ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Top 5 Regiones', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('reportes/graficos_procesamiento.png', dpi=300, bbox_inches='tight')
    print(f"   ✓ Gráficos guardados: reportes/graficos_procesamiento.png")
    plt.show()

def mostrar_ejemplos_normalizacion():
    """Muestra ejemplos de cómo quedan normalizados diferentes tipos de números"""
    
    normalizer = ArgentinaPhoneNormalizer()
    
    ejemplos = [
        "1234567890",      # Número sin formatear de CABA
        "01112345678",     # Con prefijo nacional
        "541112345678",    # Con código de país
        "+541112345678",   # Formato internacional
        "15-1234-5678",    # Formato móvil
        "221-456-7890",    # Fijo de La Plata
        "351-123-4567",    # Fijo de Córdoba
        "invalid123"       # Número inválido
    ]
    
    print("\n" + "="*60)
    print("EJEMPLOS DE NORMALIZACIÓN")
    print("="*60)
    
    for numero in ejemplos:
        resultado = normalizer.normalize_phone_number(numero)
        
        print(f"\nOriginal: {numero}")
        print(f"Válido: {'✅' if resultado['is_valid'] else '❌'}")
        
        if resultado['is_valid']:
            print(f"Normalizado: {resultado['normalized']}")
            print(f"Tipo: {resultado['type']}")
            print(f"Operador: {resultado['operator']}")
            print(f"Región: {resultado['region'].replace('_', ' ')}")
            print(f"Formato nacional: {resultado['format_national']}")
        else:
            print(f"Errores: {', '.join(resultado['errors'])}")
        
        print("-" * 40)

if __name__ == "__main__":
    # Mostrar ejemplos primero
    mostrar_ejemplos_normalizacion()
    
    # Procesar archivo real
    df_resultado, reporte = procesar_telefonos()
    
    if df_resultado is not None:
        print(f"\n✅ ¡Procesamiento exitoso!")
        print(f"Revisa los archivos generados para ver los resultados.")
    else:
        print(f"\n❌ No se pudo completar el procesamiento.")