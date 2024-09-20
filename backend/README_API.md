# PetBnB API Documentation

## Authentication

This API uses JWT (JSON Web Tokens) for authentication. 

### Register a new user

- **URL:** `/users/`
- **Method:** `POST`
- **Data Params:** 
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "re_password": "password123",
  "user_type": "petowner",
  "bio": "User bio",
  "city": "User City",
  "district": "User District",
  "birth_date": "1990-01-01",
  "phone_number": "1234567890"
}
```
- **Success Response:** 
  - **Code:** 201 CREATED
  - **Content:** `{ "id": 1, "email": "user@example.com", ... }`

### Login

- **URL:** `/jwt/create/`
- **Method:** `POST`
- **Data Params:** 
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
- **Success Response:** 
  - **Code:** 200 OK
  - **Content:** `{ "access": "access_token", "refresh": "refresh_token" }`

### Refresh Token

- **URL:** `/jwt/refresh/`
- **Method:** `POST`
- **Data Params:** 
```json
{
  "refresh": "refresh_token"
}
```
- **Success Response:** 
  - **Code:** 200 OK
  - **Content:** `{ "access": "new_access_token" }`

### Logout

- **URL:** `/jwt/destroy/`
- **Method:** `POST`
- **Data Params:** 
```json
{
  "refresh": "refresh_token"
}
```
- **Success Response:** 
  - **Code:** 204 NO CONTENT

## Service Requests

### List Service Requests

- **URL:** `/service-requests/`
- **Method:** `GET`
- **URL Params:** 
  - `isActive=[boolean]`
  - `location=[string]`
  - `pet_breed=[string]`
  - `pet_type=[string]`
  - `start_date=[date]`
  - `end_date=[date]`
- **Success Response:** 
  - **Code:** 200 OK
  - **Content:** Array of service request objects

### Create Service Request

- **URL:** `/service-requests/`
- **Method:** `POST`
- **Data Params:** 
```json
{
  "start_date": "2024-08-01",
  "end_date": "2024-08-05",
  "pet_type": "Dog",
  "pet_breed": "Labrador",
  "location": "New York",
  "description": "Need someone to take care of my dog for 5 days."
}
```
- **Success Response:** 
  - **Code:** 201 CREATED
  - **Content:** Created service request object

### Get Service Request

- **URL:** `/service-requests/:id/`
- **Method:** `GET`
- **Success Response:** 
  - **Code:** 200 OK
  - **Content:** Service request object

### Update Service Request

- **URL:** `/service-requests/:id/`
- **Method:** `PUT`
- **Data Params:** Same as Create Service Request
- **Success Response:** 
  - **Code:** 200 OK
  - **Content:** Updated service request object

### Delete Service Request

- **URL:** `/service-requests/:id/`
- **Method:** `DELETE`
- **Success Response:** 
  - **Code:** 204 NO CONTENT

## Service Offers

### List Service Offers

- **URL:** `/service-offers/`
- **Method:** `GET`
- **Success Response:** 
  - **Code:** 200 OK
  - **Content:** Array of service offer objects

### Create Service Offer

- **URL:** `/service-offers/`
- **Method:** `POST`
- **Data Params:** 
```json
{
  "service_request": 1,
  "price": "50.00",
  "message": "I can take care of your dog"
}
```
- **Success Response:** 
  - **Code:** 201 CREATED
  - **Content:** Created service offer object

### Get Service Offer

- **URL:** `/service-offers/:id/`
- **Method:** `GET`
- **Success Response:** 
  - **Code:** 200 OK
  - **Content:** Service offer object

### Update Service Offer

- **URL:** `/service-offers/:id/`
- **Method:** `PUT`
- **Data Params:** Same as Create Service Offer
- **Success Response:** 
  - **Code:** 200 OK
  - **Content:** Updated service offer object

### Delete Service Offer

- **URL:** `/service-offers/:id/`
- **Method:** `DELETE`
- **Success Response:** 
  - **Code:** 204 NO CONTENT

## Notes

- All authenticated endpoints require a valid JWT token in the Authorization header: `Authorization: JWT <access_token>`
- Caregivers can only create and edit their own offers
- Pet owners can only create and edit their own service requests
- Admins have full access to all endpoints