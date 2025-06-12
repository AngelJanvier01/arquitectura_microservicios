##!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: policy_controller.py
# Capitulo: Estilo Microservicios
# Autor(es): Perla Velasco & Yonathan Mtz. & Jorge Solís
# Version: 3.0.0 Febrero 2022
# Descripción:
#
#   Ésta clase define el controlador del microservicio Reporter. 
#   Implementa la funcionalidad y lógica de negocio del Microservicio.
#
#   Las características de ésta clase son las siguientes:
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                             Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |    download_policy()   |         Ninguno          |  - Procesa la         |
#           |                        |                          |    creación de la     |
#           |                        |                          |    póliza de seguro   |
#           |                        |                          |    de un cliente y la |
#           |                        |                          |    envía como         |
#           |                        |                          |    respuesta.         |
#           +------------------------+--------------------------+-----------------------+
#           |     health_check()     |         Ninguno          |  - Permite comprobar  |
#           |                        |                          |    si el servicio se  |
#           |                        |                          |    encuentra activo   |
#           |                        |                          |    o no.              |
#           +------------------------+--------------------------+-----------------------+
#
#-------------------------------------------------------------------------
from flask import request, send_file, jsonify
from src.helpers.processor import create_policy
import json, os
from datetime import datetime, timedelta
import requests

class PolicyController:

    @staticmethod
    def download_policy():
        if request.args:
            try:
                data = json.loads(request.args.get("data"))
                if isinstance(data, dict):
                    # Generar fechas de póliza
                    policy_from = datetime.now()
                    data['policy_from'] = policy_from.strftime("%d-%m-%Y")
                    data['policy_to'] = (policy_from + timedelta(weeks=52)).strftime("%d-%m-%Y")

                    # Crear el PDF
                    pdf_path = create_policy(data)
                    pdf_name = os.path.basename(pdf_path)

                    # Enviar al notificador
                    with open(pdf_path, 'rb') as f:
                        response = requests.post("http://notificador:8001/recibir-pdf", files={"file": (pdf_name, f)})

                    if response.status_code != 200:
                        return "Error al enviar PDF al notificador", 500

                    # Muestra el PDF en el navegador
                    return send_file(pdf_path, as_attachment=False)

                else:
                    return "Datos inválidos", 400
            except Exception:
                return "Error interno al procesar la póliza", 500
        else:
            return "Solicitud incorrecta", 400
        
    @staticmethod
    def health_check():
        return jsonify({"status": "ok"}), 200