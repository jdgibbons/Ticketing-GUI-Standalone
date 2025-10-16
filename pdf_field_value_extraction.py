import pdfplumber
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


# NOTE: You will need to install the following libraries if you don't have them:
# pip install pdfplumber reportlab

def create_dummy_pdf(filepath="test_document.pdf"):
    """
    Creates a multi-page PDF for demonstration purposes.
    The content and specific strings are known, making testing easier.
    """
    try:
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter

        # --- Page 1 ---
        c.drawString(72, height - 72, "Invoice Number 1001 for Alpha Corp.")
        c.drawString(72, height - 100, "The first page contains critical financial data.")
        c.drawString(100, 200, "End of Section A.")
        c.showPage()  # Start new page

        # --- Page 2 ---
        c.drawString(72, height - 72, "Report Summary: This is page two.")
        c.drawString(72, height - 100, "The quick brown fox jumps over the lazy dog.")
        c.drawString(400, 150, "Final Review Complete.")
        c.showPage()  # Start new page

        # --- Page 3 ---
        c.drawString(72, height - 72, "Contact Information")
        c.drawString(150, height - 120, "Please contact the main office for support.")
        c.drawString(150, height - 150, "Invoice Number 1002 is pending.")
        c.save()
        print(f"✅ Dummy PDF created successfully at: {filepath}")
    except Exception as e:
        print(f"❌ Error creating dummy PDF: {e}")
        return None
    return filepath


def extract_all_text_locations(pdf_path: str) -> list:
    """
    Finds and returns the page and bounding box position for every
    text segment (word) found within a PDF.

    Args:
        pdf_path: The file path to the PDF document.

    Returns:
        A list of dictionaries containing the extracted text and location data.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return []

    found_locations = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"🔍 Extracting all text from {len(pdf.pages)} pages...")

            for page_num, page in enumerate(pdf.pages, 1):
                # Extract words with their bounding boxes (x0, y0, x1, y1)
                # x_tolerance helps group letters slightly separated in the PDF structure
                # We use extract_words() because it yields granular coordinate data for each segment.
                words = page.extract_words(x_tolerance=3, y_tolerance=3)

                for word in words:
                    # The position coordinates (x0, top, x1, bottom) define the bounding box
                    position_box = {
                        "x0": round(word['x0'], 2),
                        "y0_top": round(word['top'], 2),
                        "x1": round(word['x1'], 2),
                        "y1_bottom": round(word['bottom'], 2),
                        # Note: 'top' is the y-coordinate from the top of the page (standard PDFplumber convention).
                    }

                    found_locations.append({
                        "text": word['text'],
                        "page": page_num,
                        "position_box": position_box
                    })

    except Exception as e:
        print(f"An error occurred during PDF processing: {e}")
        return []

    return found_locations


if __name__ == '__main__':
    PDF_FILE = "182131_31153_3.pdf"

    # 1. Create a dummy PDF for testing
    # pdf_path = create_dummy_pdf(PDF_FILE)
    pdf_path = PDF_FILE
    if pdf_path:
        # 2. Run the extraction (no search terms needed now)
        results_list = extract_all_text_locations(pdf_path)

        # 3. Print the final results
        print("\n--- RESULTS (All Text Segments Extracted) ---")
        if results_list:
            print(f"Total text segments found: {len(results_list)}\n")
            # Print only the first 10 results to keep the output manageable
            for i, item in enumerate(results_list[:10]):
                print(f"Page {item['page']} | Text: '{item['text']}'")
                print(f"  Coordinates: {item['position_box']}")
                print("-" * 20)
            file = open("extracted_text.txt", 'w')
            for i, item in enumerate(results_list):
                file.write(f"Page {item['page']} | Text: '{item['text']}'\n")
                file.write(f"  Coordinates: {item['position_box']}\n")
                file.write("-" * 20)
                file.write("\n")

            if len(results_list) > 10:
                print(f"... and {len(results_list) - 10} more segments extracted.")

        else:
            print("No text segments were found in the document.")

        # 4. Clean up the dummy file (optional)
        # os.remove(PDF_FILE)
