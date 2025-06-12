##!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: processor.py
# Capitulo: Estilo Microservicios
# Autor(es): Perla Velasco & Yonathan Mtz. & Jorge Solís
# Version: 3.0.0 Febrero 2022
# Descripción:
#
#   Éste archivo define el proceso de creación de las pólizas de seguro a partir de una plantilla
#
#   A continuación se describen los métodos que se implementaron en éste archivo:
#
#                                             Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |    create_policy()     | - data: representa los   |  - Crea un archivo    |
#           |                        |   datos del cliente para |    que representa la  |
#           |                        |   el cual se creará la   |    la póliza de       |
#           |                        |   póliza del seguro      |    seguro de un       |
#           |                        |                          |    cliente específico |
#           |                        |                          |    a partir de una    |
#           |                        |                          |    plantilla          |
#           +------------------------+--------------------------+-----------------------+
#
#-------------------------------------------------------------------------
from jinja2 import Environment, FileSystemLoader
import weasyprint
import os


def create_policy(data):
    # Asegura que exista la carpeta donde se guardará el PDF
    output_dir = os.path.join(os.getcwd(), 'documentos')
    os.makedirs(output_dir, exist_ok=True)
    # Carga y renderiza la plantilla HTML
    environment = Environment(loader=FileSystemLoader('./templates'))
    template = environment.get_template('template-policy.html')
    rendered_html = template.render(data)

    # Guarda el HTML intermedio 
    html_path = os.path.join(output_dir, 'policy.html')
    with open(html_path, mode="w", encoding="utf-8") as results:
        results.write(rendered_html)

    # Genera el PDF
    pdf_path = os.path.join(output_dir, 'policy.pdf')
    weasyprint.HTML(html_path).write_pdf(pdf_path)

    return pdf_path  # Devolvemos la ruta completa al PDF generado
