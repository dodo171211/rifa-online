"""Servidor da rifa online: site + API + banco SQLite."""
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from rifa_db import get_estatisticas, init_database, listar_compras, reservar_numeros

init_database()

BASE = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(BASE), static_url_path="")


@app.route("/")
def index():
    return send_from_directory(BASE, "index.html")


@app.route("/api/estatisticas")
def estatisticas():
    return jsonify(get_estatisticas())


@app.route("/api/reservar", methods=["POST"])
def reservar():
    data = request.get_json(silent=True) or {}
    try:
        compra = reservar_numeros(
            nome=data.get("nome", ""),
            telefone=data.get("telefone", ""),
            email=data.get("email"),
            numeros=data.get("numeros", []),
        )
        return jsonify({"ok": True, "compra": compra}), 201
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400


@app.route("/api/compras")
def compras():
    return jsonify({"compras": listar_compras()})
