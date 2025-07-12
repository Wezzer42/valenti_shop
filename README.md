# Valenti Shop

A Django e-commerce application prototype built with [Django Oscar](https://django-oscar.readthedocs.io/en/latest/).  
This project demonstrates how to set up and customize an online store using Python, Django, and Tailwind CSS.

---

##  Features

- Django Oscar integration
- **Tailwind CSS** for modern, responsive design
- Custom product catalog and categories
- Product validation and filtering
- Modular app structure
- Logging and error handling

---

##  Tech Stack

- Python 3.x
- Django
- Django Oscar
- Tailwind CSS
- SQLite (default) or PostgreSQL (optional)

---

##  Quick Start

###  Clone the repository

```bash
git clone https://github.com/Wezzer42/valenti_shop.git
cd valenti_shop
```
### Create a virtual environment
Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```
macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```
### Install dependencies
```bash
pip install -r requirements.txt
```
### Apply migrations
```bash
python manage.py migrate
```
### Create a superuser (optional)
```bash
python manage.py createsuperuser
```
### Run the development server
```bash
python manage.py runserver
```
Open http://127.0.0.1:8000/ in your browser.

## Frontend Customization
This project replaces the default Bootstrap templates with Tailwind CSS, providing:

Modern utility-first styles

Clean responsive layout

Easily customizable components

Tailwind is integrated via Django Tailwind.


## TODO / Roadmap
 Product search integration (ElasticSearch)

 Payment gateway support (Stripe/PayPal)

 Docker deployment

 Multi-language support

## License
This project is licensed under the MIT License.

## Author
Made by Wezzer42
