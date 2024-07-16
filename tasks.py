from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

@task
def order_robot_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves a screenshot of the ordered robot.
    Embeds the screenshot in the PDF receipt.
    Creates a ZIP archive of the receipts and screenshots.
    """
    browser.configure(slowmo=300)
    open_robot_order_website()
    download_orders_file()
    process_orders()
    archive_receipts()


def open_robot_order_website():
    """Opens the robot order website and dismisses the pop-up."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    browser.page().click('text=OK')

def download_orders_file():
    """Downloads the orders CSV file."""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def order_another_bot():
    """Clicks the 'Order Another' button to start a new order."""
    browser.page().click("#order-another")

def clicks_ok():
    """Clicks the 'OK' button after placing an order."""
    browser.page().click('text=OK')

def process_orders():
    """Processes all orders listed in the CSV file."""
    csv_file = Tables()
    robot_orders = csv_file.read_table_from_csv("orders.csv")
    for order in robot_orders:
        process_single_order(order)

def process_single_order(order):
    """Processes a single robot order."""
    fill_and_submit_robot_data(order)
    pdf_path = store_receipt_as_pdf(int(order["Order number"]))
    screenshot_path = screenshot_robot(int(order["Order number"]))
    embed_screenshot_to_receipt(screenshot_path, pdf_path)
    order_another_bot()
    clicks_ok()

def fill_and_submit_robot_data(order):
    """Fills in the robot order form and submits the order."""
    page = browser.page()
    head_names = {
        "1": "Roll-a-thor head",
        "2": "Peanut crusher head",
        "3": "D.A.V.E head",
        "4": "Andy Roid head",
        "5": "Spanner mate head",
        "6": "Drillbit 2000 head"
    }
    page.select_option("#head", head_names[order["Head"]])
    page.click(f'//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{order["Body"]}]/label')
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    
    while True:
        page.click("#order")
        if page.query_selector("#order-another"):
            break

def store_receipt_as_pdf(order_number):
    """Stores the order receipt as a PDF file."""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def screenshot_robot(order_number):
    """Takes a screenshot of the ordered robot."""
    page = browser.page()
    screenshot_path = f"output/screenshots/{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """Embeds the robot screenshot into the PDF receipt."""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot_path,
        source_path=pdf_path,
        output_path=pdf_path
    )

def archive_receipts():
    """Creates a ZIP archive of all the receipt PDFs."""
    archive = Archive()
    archive.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")
