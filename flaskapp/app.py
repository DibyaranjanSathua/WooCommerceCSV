"""
File:           app.py
Author:         Dibyaranjan Sathua
Created on:     01/01/2021, 17:49
"""
import datetime
import traceback
from pathlib import Path
from flask import Flask, render_template, request, send_file
from src.supplier_csv_to_woocommerce_csv import SupplierCSV2WoocommerceCSV
from src.product_integration import ProductIntegration


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


@app.route("/submit", methods=['POST'])
def submit():
    """ Form submission """
    now = datetime.datetime.now()
    now_str = now.strftime("%Y%m%d%H%M%S")
    input_csv = request.files.get("csv")
    mapping_file = request.form.get("mapping")
    update_image = request.form.get("updateImageOptions")
    downloadcsv_btn = request.form.get("downloadcsv")
    api_btn = request.form.get("api")

    print(update_image)
    # Save the input CSV file
    input_csv_name_orig = Path(input_csv.filename)
    input_csv_name = f"input_{input_csv_name_orig.stem}_{now_str}.csv"
    input_csv_path = PROJECT_ROOT / "flaskapp" / app.config["CSV_FILES"] / input_csv_name
    input_csv.save(input_csv_path)

    obj = SupplierCSV2WoocommerceCSV(
        csv_file=input_csv_path,
        template=mapping_file
    )
    obj.convert()
    if downloadcsv_btn is not None and downloadcsv_btn == "downloadcsv":
        output_csv_name = f"output_{input_csv_name_orig.stem}_{now_str}.csv"
        output_csv = PROJECT_ROOT / "flaskapp" / app.config["CSV_FILES"] / output_csv_name
        obj.save_to_csv(output_csv=str(output_csv))
        return send_file(str(output_csv), as_attachment=True)

    if api_btn is not None and api_btn == "api":
        if obj.product_records:
            # CSV file headers
            headers = list(obj.product_records[0].keys())
            return render_template(
                "table.html",
                headers=headers,
                records=obj.product_records,
                csv=input_csv_path,
                mapping=mapping_file,
                update_image=update_image
            )
        return "<h3> No Product Record </h3>"
    return "<h3> Click a valid button </h3>"


@app.route("/create-or-update", methods=['POST'])
def create_or_update():
    """ Create or Update products using API """
    input_csv = request.form.get("csv")
    mapping_file = request.form.get("mapping")
    update_image = request.form.get("update_image")
    print(f"\n\n{'=' * 30}")
    print(f"Processing on {datetime.datetime.now()}")
    print(f"{'=' * 30}")
    print(input_csv)
    print(mapping_file)
    print(update_image)
    if update_image == "newProducts":
        obj = ProductIntegration(
            csv_file=input_csv,
            template=mapping_file,
            update_image_mode=ProductIntegration.UpdateImageCode.NewProducts
        )
    else:
        obj = ProductIntegration(
            csv_file=input_csv,
            template=mapping_file,
            update_image_mode=ProductIntegration.UpdateImageCode.ALlProducts
        )
    obj.setup()
    try:
        obj.create_or_update_products()
    except Exception as err:
        print(err)
        print(traceback.print_exc())
    print(f"\n\n{'=' * 30}")
    table_headers = []
    if obj.product_upload_table:
        table_headers = list(obj.product_upload_table[0].keys())
    return render_template(
        "api_status.html",
        responses=obj.api_responses,
        product_status=obj.product_upload_table,
        table_headers=table_headers
    )


# @app.route("/download-csv", methods=['POST'])
# def download_csv():
#     """ Download output CSV file """
#     now = datetime.datetime.now()
#     now_str = now.strftime("%Y%m%d%H%M%S")
#     input_csv = request.files.get("csv")
#     mapping_file = request.form.get("mapping")
#
#     input_csv_name = Path(input_csv.filename)
#     output_csv_name = f"{input_csv_name.stem}_{now_str}.csv"
#     output_csv = PROJECT_ROOT / "flaskapp" / app.config["CSV_FILES"] / output_csv_name
#     obj = SupplierCSV2WoocommerceCSV(
#         csv_file=input_csv,
#         template=mapping_file
#     )
#     obj.convert()
#     obj.save_to_csv(output_csv=str(output_csv))
#     return send_file(str(output_csv), as_attachment=True)
#
#
# @app.route("/api-confirmation")
# def api_confirmation():
#     """ Display the CSV data and confirm user to upload it to woocommerce """
#     input_csv = request.files.get("csv")
#     mapping_file = request.form.get("mapping")
#     obj = SupplierCSV2WoocommerceCSV(
#         csv_file=input_csv,
#         template=mapping_file
#     )
#     obj.convert()
#     if obj.product_records:
#         headers = list(obj.product_records[0].keys())
#         return render_template("table.html", headers=headers, records=obj.product_records)
#     return "<h3> No Product Record </h3>"


if __name__ == "__main__":
    app.run(debug=True)
