# E-commerce API

This repository contains a source code for an e-commerce API. The API provides a set of functionalities to support common e-commerce features, such as cart management, product management, order processing, user authentication, and payment processing.
### Features
* Cart CRUD: Allows users to create, read, update, and delete items in their shopping cart.
* Product CRUD: Manage products by creating, reading, updating, and deleting product information.
* Order CRUD: Provides the ability to create, read, update, and delete orders,
* Authentication: Implements JSON Web Token (JWT) based authentication.
* Stripe Payment: Integrates with the Stripe API for payment processing.

*Checkout the front-end [here](https://github.com/leihtsale/e-commerce-frontend)*
## Test and Install
1. Install Docker
2. Clone this repository \
```git clone https://github.com/leihtsale/e-commerce-api```
3. Navigate inside the directory, there's a file ```docker-compose.yml```
4. Make sure docker is installed, then run \
```docker compose up```
5. It runs on port 8000, open your browser and enter ```http://localhost:8000/```
6. You can test out the API endpoints on, ```http://localhost:8000/api/docs/```

