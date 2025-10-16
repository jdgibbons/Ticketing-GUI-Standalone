from pypdf import PdfReader


def get_text_box_info(pdf_path):
    """
    Extracts names and positions of text boxes from a PDF form.
    Returns a list of dictionaries, each containing 'name' and 'position'.
    Position is returned as a tuple (x, y, width, height).
    """
    reader = PdfReader(pdf_path)
    text_box_info = []

    # Iterate through all fields
    # Note: In pypdf, fields are often represented by their "widget" annotations
    # which contain the /Rect (position) information.
    # The /AcroForm dictionary in the PDF's root also lists fields.

    # get_fields() gives higher-level field objects which might abstract some properties.
    # We might need to go directly to page annotations for rect.

    for page in reader.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                # Get the PDF object for the annotation
                obj = annot.get_object()

                # Check if it's a form field annotation
                # And if it has a subtype of 'Widget' and a field type of 'Tx' (Text)
                if "/Subtype" in obj and obj["/Subtype"] == "/Widget":
                    if "/FT" in obj and obj["/FT"] == "/Tx":  # '/Tx' is the field type for Text
                        field_name = obj.get("/T", "Unnamed Field")  # /T is the field name
                        rect = obj.get("/Rect")  # [x1, y1, x2, y2]

                        if rect:
                            x1, y1, x2, y2 = rect
                            x = float(x1)
                            y = float(y1)  # Note: PDF coordinates usually have (0,0) at bottom-left
                            width = float(x2) - float(x1)
                            height = float(y2) - float(y1)

                            text_box_info.append({
                                "name": field_name,
                                "position": (x, y, width, height)
                            })
    return text_box_info


# --- Usage Example ---
pdf_file = "3.pdf"  # Replace with your PDF file path
info = get_text_box_info(pdf_file)

if info:
    print("Exporting text box information:")
    # Print to console or save to CSV
    print("Name,X,Y,Width,Height")  # CSV header
    for box in info:
        pos = box["position"]
        print(f"{box['name']},{pos[0]},{pos[1]},{pos[2]},{pos[3]}")
else:
    print(f"No text boxes found in {pdf_file} or an error occurred.")
