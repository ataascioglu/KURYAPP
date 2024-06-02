# KURYAPP

## Introduction

KURYAPP is a Flask-based web application designed for managing shipments. Users can register as either customers or couriers. Customers can create shipments, and couriers can accept and deliver them. The application includes user authentication, session management, and CRUD operations for addresses and shipments.

## Features

### User Authentication

- **Registration**: Users can register as either customers or couriers.
- **Login**: Users can log in and out, with optional "remember me" functionality.
- **Session Management**: Secure session handling with expiration based on user preference.

### User Roles

- **Customers**:
  - Create shipments.
  - Check shipment status.
  - Manage addresses.
- **Couriers**:
  - Accept pending shipments.
  - Update shipment status (In Transit, Delivered).
  - Manage addresses.

### Shipment Management

- **Create Shipments**: Customers can create new shipments.
- **Accept Shipments**: Couriers can accept available shipments.
- **Update Shipment Status**: Couriers can update the status of accepted shipments.
- **Check Shipment Status**: Anyone can check the status of a shipment using its code.

### Address Management

- **Add Address**: Users can add addresses to their profile.
- **View Addresses**: Users can view and manage their saved addresses.
- **Delete Address**: Users can delete addresses from their profile.

## Installation

### Prerequisites

- Python 3.6+
- SQLite3

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ataascioglu/KURYAPP.git
   cd KURYAPP
2. **Create a virtual environment and activate it**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
4. **Initialize the database**:
   ```bash
   python -c "from app import init_db; init_db()"
5. **Run the application**:
   ```bash
   flask run
6. **Open your web browser and navigate to**:
   ```bash
   http://127.0.0.1:5000/

## Project Structure

- **app.py**: Main application file containing all routes and logic.
- **templates/**: Folder containing HTML templates for rendering web pages.
- **static/**: Folder containing static files (CSS, JS, images).
- **database.db**: SQLite database file (generated upon initialization).

## Routes

### Public Routes

- **/**: Home page.
- **/about**: About page.
- **/contact**: Contact page.
- **/login**: Login page.
- **/register**: Registration page.

### Customer Routes

- **/customer-home**: Customer dashboard.
- **/create-shipment**: Create a new shipment.
- **/check-shipment-status**: Check the status of a shipment.
- **/profile**: View and manage user profile and addresses.
- **/add-address**: Add a new address.
- **/delete-address/int:address_id**: Delete an address.

### Courier Routes

- **/courier-home**: Courier dashboard.
- **/accept-shipment/int:shipment_id**: Accept a pending shipment.
- **/pick-up-shipment/int:shipment_id**: Mark a shipment as picked up.
- **/mark-delivered/int:shipment_id**: Mark a shipment as delivered.

### Session Management

- **/logout**: Log out the current user.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.
