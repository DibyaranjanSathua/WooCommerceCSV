"""
File:           app.py
Author:         Dibyaranjan Sathua
Created on:     01/01/2021, 17:49
"""
import datetime
from pathlib import Path
from flask import Flask, render_template, request, send_file
from src.supplier_csv_to_woocommerce_csv import SupplierCSV2WoocommerceCSV


PROJECT_ROOT = Path(__file__).parents[1]
app = Flask(__name__)
app.config["CSV_FILES"] = "csv_files"


@app.route("/")
def woocommerce():
    """ Display the home page """
    # Get a list of mapping available
    mapping_root = PROJECT_ROOT / "templates"
    mapping_files = {
        str(x.stem).split(".")[0].upper(): str(x.name)
        for x in mapping_root.iterdir() if x.is_file()
    }
    return render_template("home.html", mapping_files=mapping_files)


@app.route("/form-handling", methods=['POST'])
def form_handling():
    """ Form handling """
    now = datetime.datetime.now()
    now_str = now.strftime("%Y%m%d%H%M%S")
    input_csv = request.files.get("csv")
    mapping_file = request.form.get("mapping")
    input_csv_name = Path(input_csv.filename)
    output_csv_name = f"{input_csv_name.stem}_{now_str}.csv"
    output_csv = PROJECT_ROOT / "flaskapp" / app.config["CSV_FILES"] / output_csv_name
    obj = SupplierCSV2WoocommerceCSV(
        csv_file=input_csv,
        template=mapping_file,
        output_csv=str(output_csv)
    )
    obj.convert()
    return send_file(str(output_csv), as_attachment=True)


if __name__ == "__main__":
    app.run()
