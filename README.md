# eCommerce-API 

### https://ecomm-api-demo.herokuapp.com/

### **<u>LOGIN INSTRUCTIONS</u>**

1. GET request HTTP Basic Authentication at '/login' endpoint

   You will receive a JSON web token that is valid for 30 minutes.

   ![token_example](https://user-images.githubusercontent.com/50201165/151583274-b486174b-36d6-4037-9474-0f39c45ad64c.png)

2. Place token in header under the key "x-access-token":

   ![header_example](https://user-images.githubusercontent.com/50201165/151583321-a5e7aee4-be11-42fc-bbda-6e5d5a1093f7.png)

<br>

## ADMIN-ONLY ROUTES

### <u>**USER-RELATED**</u>

**Create a user**: POST request user information to '/user' endpoint

```json
{
    "name": "username", 
    "password": "12345", 
    "email": "name@mail", 
    "admin": false
}
```

**Retrieve a user**: GET request at '/user/&lt;name>'

**Promote a user**: PUT request at '/user/&lt;name>'

**Delete a user**: DELETE request at '/user/&lt;name>'

**List all users**: GET request at '/users'

<br>

### <u>**PRODUCTS**</u>  

**Create a product**: POST request product information at '/product' endpoint

Products must have a name. You can also include a description, up to eight images, metadata and toggle the active status of a product. Products are active by default. 

```json
{
    "name": "new_product", 
    "description": "this is the description",
    "images": ["imgurl1.jpg", "imgurl2.jpg"],
    "active": false,
    "metadata": {"order_id": "01694"}
}
```

**Retrieve a product**: GET request at '/product/&lt;product_id>'

**Update a product**: PUT request at '/product/&lt;product_id>'

**Delete a product**: DELETE request at '/product/&lt;product_id>'

**List all products**: GET request at '/products'

<br>

### **<u>PRICES</u>**  

**Create a price**: POST request price information at '/price' endpoint

Prices must have a unit amount, the type of currency, and a product.

```json
{
    "unit_amount": 2000, 
    "currency": "usd", 
    "product": "prod_L2dP7B8VenrqHf"
}
```

**Retrieve a price**: GET request price at '/price/&lt;price_id>'

**Update a price**: PUT request at '/price/&lt;price_id>'

**List all prices**: GET request at '/prices'

<br>

## USER ROUTES

### **<u>ACCOUNT</u>**

**Retrieve account information**: GET request '/account' endpoint

<br>

### **<u>PRODUCTS</u>**

**Query products**: GET request at '/q?search=' followed by search parameters

**Preview a product**: Get request '/view/&lt;product_id>'

**List all products**: Get request '/view?limit=' followed by number of products to list

<br>

### **<u>CART</u>**

**Retrieve all items**: GET request at '/cart' endpoint

**Add an item**: POST request product ID at '/cart'

```json
{"product_id": "price_1KNfF5EN9TFKicCwFKRnvJqY"}
```

**Delete an item**: DELETE request product ID at '/Cart'

```json
{"product_id": "price_1KLvfbEN9TFKicCwfOGSTNnI"}
```

<br>

### **<u>CHECKOUT</u>**

GET request '/checkout/&lt;token>' in browser

![CHECK](https://user-images.githubusercontent.com/50201165/151915325-c30b1a65-951d-445e-9e5a-6d3b1569aa8a.png)
