##!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: telegram_controller.py
# Capitulo: Estilo Microservicios
# Autor(es): Perla Velasco & Yonathan Mtz. & Jorge Solís
# Version: 3.0.0 Febrero 2022
# Descripción:
#
#   Ésta clase define el controlador del microservicio API. 
#   Implementa la funcionalidad y lógica de negocio del Microservicio.
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                             Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |     send_message()     |         Ninguno          |  - Procesa el mensaje |
#           |                        |                          |    recibido en la     |
#           |                        |                          |    petición y ejecuta |
#           |                        |                          |    el envío a         |
#           |                        |                          |    Telegram.          |
#           +------------------------+--------------------------+-----------------------+
#
#-------------------------------------------------------------------------
from flask import request, jsonify, Blueprint
import json
import requests
from configparser import ConfigParser
import os
import logging

class TelegramController:

    @staticmethod
    def send_message():
        data = json.loads(request.data)
        message = data.get("message")

        if not data:
            return jsonify({"msg": "invalid request"}), 400

        # Cargar configuración de Telegram
        config = ConfigParser()
        config_path = os.path.abspath("settings.ini")
        config.read(config_path)
        
        token = config.get("TELEGRAM", "TOKEN")
        chat_id = config.get("TELEGRAM", "CHAT_ID")

        # 1. Enviar mensaje
        msg_url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        msg_response = requests.post(msg_url, json=payload)

        # 2. Enviar PDF 
        pdf_path = "/tmp/policy.pdf"
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as pdf_file:
                file_url = f"https://api.telegram.org/bot{token}/sendDocument"
                file_payload = {
                    "chat_id": chat_id,
                    "caption": "✅ 📄 Aquí tienes la póliza generada :D."
                }
                files = {
                    "document": pdf_file
                }
                file_response = requests.post(file_url, data=file_payload, files=files)
        else:
            return jsonify({"msg": "Mensaje enviado, pero el archivo PDF no fue encontrado"}), 200

        if msg_response.status_code == 200 and file_response.status_code == 200:
            return jsonify({"msg": "Mensaje y archivo enviados correctamente"}), 200
        else:
            return jsonify({"msg": "Error al enviar mensaje o archivo"}), 500

    notifier = Blueprint('notifier', __name__)

    @notifier.route('/recibir-pdf', methods=['POST'])
    def receive_pdf():
        if 'file' not in request.files:
            return jsonify({"msg": "No se encontró el archivo PDF en la solicitud"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"msg": "Nombre de archivo vacío"}), 400

        try:
            save_path = os.path.join("/tmp", "policy.pdf") 
            file.save(save_path)
            print(f"PDF recibido y guardado en: {save_path}", flush=True)
            return jsonify({"msg": "Archivo recibido correctamente"}), 200
        except Exception as e:
            return jsonify({"msg": f"Error al guardar archivo: {str(e)}"}), 500
