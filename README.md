# 📱 PROTOTIPO 1: Normalizador de Números Telefónicos Argentinos

Sistema inteligente para validar, normalizar y optimizar números telefónicos argentinos para campañas de calling.

## 🗂️ Estructura del Proyecto

```
prototipo_1_normalizador/
├── README.md                           # Este archivo
├── argentina_phone_normalizer.py       # Clase principal del normalizador
├── procesar_llamadas.py                # Script principal de procesamiento
├── llamadas.csv                        # Archivo de entrada (números a procesar)
├── telefonos_para_marcar_argentina.csv # 🎯 SALIDA PRINCIPAL para dialer
├── telefonos_para_marcar_argentina.txt # Lista simple para importar
└── reportes/                           # 📊 Todos los reportes y análisis
    ├── telefonos_procesados_completo.csv
    ├── telefonos_validos.csv
    ├── telefonos_formato_internacional.csv
    ├── telefonos_con_problemas.csv
    ├── reporte_procesamiento.json
    └── graficos_procesamiento.png
```

## 🚀 Instalación y Uso

### 1. Requisitos
```bash
pip install pandas numpy matplotlib seaborn
```

### 2. Preparar datos
- Coloca tu archivo `llamadas.csv` con una columna `TELEFONO`
- Cada fila debe contener un número telefónico

### 3. Ejecutar procesamiento
```bash
cd prototipo_1_normalizador
python procesar_llamadas.py
```

## 📋 Archivos de Salida

### 🎯 **Archivos Principales (para usar en campaigns)**

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| `telefonos_para_marcar_argentina.csv` | **PRINCIPAL** - Números listos para marcar desde Argentina | Importar en dialer |
| `telefonos_para_marcar_argentina.txt` | Mismos números, formato texto | Sistemas que leen TXT |

### 📊 **Reportes de Análisis (carpeta reportes/)**

| Archivo | Contenido |
|---------|-----------|
| `reporte_procesamiento.json` | Estadísticas completas del procesamiento |
| `graficos_procesamiento.png` | Visualizaciones de validez, operadores, regiones |
| `telefonos_procesados_completo.csv` | Dataset completo con todas las validaciones |
| `telefonos_validos.csv` | Solo números válidos con metadatos |
| `telefonos_con_problemas.csv` | Números que fallaron validación |
| `telefonos_formato_internacional.csv` | Formato +54 (para llamadas internacionales) |

## 🔍 Validaciones Realizadas

### ✅ Números Válidos
- **Códigos de área argentinos**: 11, 221, 351, 341, etc.
- **Longitud correcta**: Móviles 7-8 dígitos, Fijos 6-8 dígitos
- **Formato estructural**: Patrones reconocidos de Argentina

### 📱 Detección Automática
- **Tipo**: Móvil vs Fijo
- **Operador**: Personal, Movistar, Claro
- **Región**: CABA, Córdoba, Rosario, La Plata, etc.

### 📞 Formatos de Salida

```
Número Original: 1533887576
↓
Para marcar desde Argentina: 1533887576
Formato internacional: +541533887576
Tipo: mobile
Operador: Personal
Región: CABA_GBA
```

## 📊 Métricas y Estadísticas

El sistema genera automáticamente:

- **Tasa de validez** de números
- **Distribución por operadores** (Personal, Movistar, Claro)
- **Distribución geográfica** por provincias/regiones
- **Análisis de errores** más comunes
- **Gráficos visuales** de todas las métricas

## 🛠️ Configuración Avanzada

### Personalizar Validaciones
Edita `argentina_phone_normalizer.py` para:
- Agregar nuevos códigos de área
- Modificar rangos de operadores
- Ajustar reglas de validación

### Personalizar Reportes
Edita `procesar_llamadas.py` para:
- Cambiar formatos de salida
- Agregar nuevas métricas
- Modificar visualizaciones

## 🎯 Casos de Uso

1. **Limpieza de bases de datos** antes de campañas
2. **Segmentación por operador** para optimizar costos
3. **Análisis geográfico** para targeting regional
4. **Detección de números problemáticos** para eliminar
5. **Formato correcto** para diferentes sistemas de dialing

## 📈 Beneficios

- ✅ **Reducción de costos**: Elimina números inválidos
- ✅ **Mayor contactabilidad**: Formato correcto garantizado  
- ✅ **Análisis inteligente**: Insights automáticos por operador/región
- ✅ **Compliance**: Validación según estándares argentinos
- ✅ **Escalabilidad**: Procesa miles de números en minutos

## 🔧 Soporte Técnico

Para modificaciones o dudas:
1. Revisa los logs de procesamiento
2. Consulta `reportes/reporte_procesamiento.json` 
3. Verifica números problemáticos en `reportes/telefonos_con_problemas.csv`

---

**✨ ¡Listo para optimizar tus campañas de calling con números perfectamente normalizados!**