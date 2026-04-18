import re

file = 'client_dashboard.py'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

replacements = {
    'Account Score': 'Puntuación de Cuenta',
    '"Needs Optimization"': '"Necesita Optimización"',
    '"Requires Attention"': '"Requiere Atención"',
    'Account Status': 'Estado de la Cuenta',
    '>Score<': '>Puntuación<',
    '>Grade<': '>Calificación<',
    'Top Insights': 'Insights Principales',
    "Today's Summary": 'Resumen de Hoy',
    'Everything looks good': 'Todo se ve bien',
    'No urgent actions needed today': 'No hay acciones urgentes hoy',
    'Last update': 'Última actualización',
    'Just now': 'Justo ahora',
    '"⚠️ Needs Attention"': '"⚠️ Necesita Atención"',
    '"📊 Optimize"': '"📊 Optimizar"',
    '"✅ All Good"': '"✅ Todo Bien"',
    '>to stop<': '>para detener<',
    '>to fix<': '>para corregir<',
    '>to scale<': '>para escalar<',
    'Score today:': 'Puntuación de hoy:',
    'Total actions:': 'Acciones totales:',
    'Start Your Journey': 'Comienza tu Camino',
    'Complete your first action to start tracking progress': 'Completa tu primera acción para empezar a medir tu progreso',
    'Your Progress': 'Tu Progreso',
    'Actions Completed': 'Acciones Completadas',
    'Score Change (7d)': 'Cambio en Puntuación (7d)',
    'This Week': 'Esta Semana',
    'Recently completed:': 'Completadas recientemente:',
    '"CPC is 35% above average"': '"CPC es 35% superior al promedio"',
    '"Average CPC: ': '"CPC Promedio: ',
    '"CPC is excellent"': '"CPC es excelente"',
    '"CTR below benchmark"': '"CTR por debajo del benchmark"',
    '"Average CTR: ': '"CTR Promedio: ',
    '"CTR above benchmark"': '"CTR por encima del benchmark"',
    ' campaigns saturated"': ' campañas saturadas"',
    '"Frequency > 4x"': '"Frecuencia > 4x"',
    '"ROAS below 1x"': '"ROAS inferior a 1x"',
    '"Average ROAS: ': '"ROAS Promedio: ',
    '"Excellent ROAS"': '"ROAS Excelente"',
    '"Budget highly concentrated"': '"Presupuesto altamente concentrado"',
    '"Top 3 campaigns: ': '"Top 3 campañas: ',
    ' of spend"': ' del gasto"',
    '>Kill<': '>Detener<',
    '>Fix<': '>Corregir<',
    '>Scale<': '>Escalar<'
}

for old, new in replacements.items():
    text = text.replace(old, new)

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)

print("Translation done.")