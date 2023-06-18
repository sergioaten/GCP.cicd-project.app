#!/usr/bin/python3
"""
This code is used as an example for the Chapter10 of the book DevOps With Linux

"""
from functools import wraps
import json
import platform
from flask import Flask, request, jsonify

APP = Flask(__name__)


def check_card(func):
    """
    This function validates the credit card transactions
    """
    wraps(func)

    def validation(*args, **kwargs):
        """
            This function is a decorator,
            which will return the function corresponding to the respective action
        """
        data = request.get_json()
        if not data.get("status"):
            response = {"approved": False,
                        "newLimit": data.get("limit"),
                        "reason": "Blocked Card"}
            return jsonify(response)

        if data.get("limit") < data.get("transaction").get("amount"):
            response = {"approved": False,
                        "newLimit": data.get("limit"),
                        "reason": "Transaction above the limit"}
            return jsonify(response)
        return func(*args, **kwargs)

    return validation


@APP.route("/api/transaction", methods=["POST"])
@check_card
def transaction():
    """
    This function is resposible to expose the endpoint for receiving the incoming transactions
    """
    card = request.get_json()
    new_limit = card.get("limit") - card.get("transaction").get("amount")
    response = {"approved": True, "newLimit": new_limit}
    return jsonify(response)

@APP.route('/osinfo', methods=["GET"])
def get_data():
    """
        This function is resposible to expose the endpoint for receiving the incoming transactions
    """
    system_info = {
        'platform': platform.platform(),
        'release': platform.release(),
        'system': platform.system(),
        'architecture' : platform.machine(),
        'python_version' : platform.python_version(),
        'node': platform.node(),
        'msg': "Mensaje de prueba para testear la integración continua.."
    }

    # Convert the data to JSON format
    json_data = json.dumps(system_info, indent=2)

    # Set up the HTTP response with the appropriate header
    response = APP.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )

    return response


if __name__ == '__main__':
    APP.run(debug=True,host="0.0.0.0",port="5000")
