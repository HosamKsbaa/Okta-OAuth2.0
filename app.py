from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import httpx
import uvicorn
from auth import *
from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import httpx
import base64
import httpx

app = FastAPI()



# Define data models
class Item(BaseModel):
    name: str
    quantity: int

class ItemCreate(Item):
    pass

class ItemUpdate(Item):
    pass

shopping_list = []



#============================================================================


import httpx
# Define roles and their corresponding permissions
#temp 
roles = {
    "parents": ["create", "read", "update", "delete"],
    "everyone": ["read"],
    "grandparents": ["create", "read", "update"],
    "kid1": ["read", "update"],
    "grandfather": ["read", "update"]
}
async def is_authorized(role: str = Depends(oauth2_scheme)):
    # Replace this with your custom logic to check user role
    if role in roles.keys():
        return role
    raise HTTPException(status_code=403, detail="Unauthorized")



@app.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print("f")
    async with httpx.AsyncClient() as client:
        data = {
            "username": form_data.username,
            "password": form_data.password,
            "options": {
                "multiOptionalFactorEnroll": False,
                "warnBeforePasswordExpired": False
            }
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = await client.post(f"https://{okta_domain}/api/v1/authn", json=data, headers=headers)

    if response.status_code == 200:
        access_token = response.json().get("sessionToken")
        if access_token:
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="Access token not found in the response")
    else:
        raise HTTPException(status_code=401, detail=response.json())


#============================================================================
def get_item(item_id: int):
    return shopping_list[item_id - 1] if 1 <= item_id <= len(shopping_list) else None

@app.post("/api/shopping-list/", response_model=Item)
async def create_item(item: ItemCreate, role: str = Depends(is_authorized)):
    if role in roles.get("parents", []):
        new_item = item.dict()
        shopping_list.append(new_item)
        return new_item
    raise HTTPException(status_code=403, detail="Permission denied")

@app.get("/api/shopping-list/", response_model=list[Item])
async def read_items():
    return shopping_list

@app.put("/api/shopping-list/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate, role: str = Depends(is_authorized)):
    existing_item = get_item(item_id)
    if existing_item:
        if role in roles.get("parents", []):
            existing_item.update(item.dict())
            return existing_item
        raise HTTPException(status_code=403, detail="Permission denied")
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/api/shopping-list/{item_id}", response_model=Item)
async def delete_item(item_id: int, role: str = Depends(is_authorized)):
    existing_item = get_item(item_id)
    if existing_item:
        if role in roles.get("parents", []):
            shopping_list.pop(item_id - 1)
            return existing_item
        raise HTTPException(status_code=403, detail="Permission denied")
    raise HTTPException(status_code=404, detail="Item not found")


HOST = "0.0.0.0"
PORT = 8000

if __name__ == "__main__":
    # Run the FastAPI app using uvicorn
    uvicorn.run(app, host=HOST, port=PORT)