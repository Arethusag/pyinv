
# README

## Invoice Generator
Invoice Generator is a powerful yet simple desktop application designed for small businesses to manage their invoicing process efficiently.

## Installation

1. Ensure you have Python 3.x installed on your system.
2. Clone the repository or download the source code.
3. Install required dependencies:

`pip install -r requirements.txt`

## Running the Application
Navigate to the project directory and run:

`python main.py`

## Key Features
- **Invoice Management**: Create, update, and delete invoices easily.
- **Client Management**: Keep track of your clients' information.
- **Line Item Management**: Manage your products or services as line items.
- **Invoice Filtering**: Filter invoices by status (paid/unpaid) and date range.
- **Data Export**: Export your invoice data to CSV for further analysis.
- **Invoice Printing**: Generate printable HTML invoices.
- **Preferences**: Set your company information for invoices.

## Usage Tips
Regularly backup your invoices.db file to prevent data loss.
Use the "Manage Clients" and "Manage Line Items" features to keep your data up-to-date.
Utilize the filter options to quickly find specific invoices.

## Contributing
We welcome contributions to improve Invoice Generator. Please fork the repository and submit a pull request with your changes.

## Support
For support, please open an issue in the GitHub repository.

## License
This project is licensed under GPL. See the LICENSE file for details.

# Invoice Generator Manual

# NAME
invoice-generator - A simple invoice generation and management system

# SYNOPSIS
invoice-generator

# DESCRIPTION
Invoice Generator is a desktop application designed for small businesses to create, manage, and track invoices. It provides a user-friendly interface for generating invoices, managing clients and line items, and exporting invoice data.

# FEATURES
- Create and manage invoices
- Add, edit, and delete clients
- Manage line items for invoices
- Mark invoices as paid or unpaid
- Filter invoices by status and date range
- Export invoice data to CSV
- Print invoices as HTML
- Set company preferences

# USAGE
1. Launch the application by running invoice-generator.
2. Use the menu bar or buttons to navigate through different functionalities.

## Creating an Invoice
1. Select a client from the dropdown menu.
2. Enter quantities for line items.
3. Click "Create Invoice" button.

## Managing Clients
Click "Manage Clients" button.
Use the dialog to add, edit, or delete clients.

## Managing Line Items
Click "Manage Line Items" button.
Use the dialog to add, edit, or delete line items.

## Exporting Invoices
Click "File" in the menu bar.
Select "Export Invoices to CSV".
Choose a location to save the CSV file.

## Setting Preferences
Click "Edit" in the menu bar.
Select "Preferences".
Enter your company name and address.

# FILES
- **invoices.db**: SQLite database storing all invoice data
- **preferences.json**: JSON file storing user preferences

# ENVIRONMENT
The application requires Python 3.x and the following libraries:

- tkinter
- sqlite3
- csv
- json

# BUGS
No known bugs at this time. Please report any issues to the developer.
