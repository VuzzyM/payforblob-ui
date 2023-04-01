from flask import Flask, render_template, request, redirect, url_for
import subprocess
import json
import secrets
import binascii
import requests
import time
import re
import getpass

def generate_rand_hex_encoded_namespace_id():
    # Generate 8 random bytes.
    n_id = secrets.token_bytes(8)
    # Return hex-encoded string representation of bytes.
    return binascii.hexlify(n_id).decode()

def generate_rand_message():
    # Generate a random message length of 1-100 bytes.
    len_msg = secrets.choice(range(16, 65))
    # Generate random bytes for the message
    msg = secrets.token_bytes(len_msg)
    # Return hex-encoded string representation of bytes.
    return binascii.hexlify(msg).decode()

def set_password():
    while True:
        password = getpass.getpass(prompt="Enter a password for payforblob: ")
        confirm_password = getpass.getpass(prompt="Confirm password: ")
        if password == confirm_password:
            return password
        print("Passwords do not match. Please try again.")

app = Flask(__name__)
password = set_password()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/set_password", methods=["POST"])
def set_password_route():
    global password
    new_password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    if new_password == confirm_password:
        password = new_password
        return "Password set successfully."
    else:
        return render_template("index.html", message="Passwords do not match. Please try again.")

@app.route("/submit", methods=["POST"])
def submit():
    if request.form["password"] != password:
        return render_template("index.html", message="Incorrect password. Please try again.")

    # Generate random n_id and msg
    n_id, msg = generate_rand_hex_encoded_namespace_id(), generate_rand_message()

    # Submit data via curl
    curl_cmd = f"curl -X POST -H 'Content-type: application/json' -d '{{\"namespace_id\": \"{n_id}\", \"data\": \"{msg}\", \"gas_limit\": 80000, \"fee\": 2000}}' http://localhost:26659/submit_pfb"
    submit_output = subprocess.check_output(curl_cmd, shell=True)

    # Get height from the response
    submit_response = json.loads(submit_output)
    height = submit_response["height"]
    logs = submit_response["logs"]
    signer = logs[0]['events'][0]['attributes'][2]['value'].strip('"')
    # Get share message via curl using header
    header_url = f"http://localhost:26659/namespaced_shares/{n_id}/height/{height}"
    header_cmd = f"curl {header_url}"
    header_output = subprocess.check_output(header_cmd, shell=True)

    # Extract share message from header output
    share_msg = json.loads(header_output.decode())["shares"][0]

    return render_template("result.html", n_id=n_id, msg=msg, height=height, share_msg=share_msg, signer=signer)


if __name__ == "__main__":
    app.run()
