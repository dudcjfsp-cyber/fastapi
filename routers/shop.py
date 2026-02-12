from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.shop_service import (
    get_items, get_user_gold, get_inventory, buy_item, sell_item, sell_all_items, 
    play_gacha_fixed, play_gacha_dynamic
)
from routers.auth import get_current_user

router = APIRouter()

# Models
class BuyRequest(BaseModel):
    item_id: int

class SellRequest(BaseModel):
    inventory_id: int

class GachaRequest(BaseModel):
    count: int = 1

# Endpoints
@router.get("/shop/items")
def read_shop_items():
    """상점 아이템 목록 조회"""
    return get_items()

@router.get("/shop/inventory/me")
def read_my_inventory(user = Depends(get_current_user)):
    """내 인벤토리 조회"""
    return get_inventory(user['username'])

@router.get("/members/me/gold")
def read_my_gold(user = Depends(get_current_user)):
    """내 골드 조회"""
    return get_user_gold(user['username'])

@router.post("/shop/buy")
def buy_item_endpoint(request: BuyRequest, user = Depends(get_current_user)):
    """아이템 구매 요청"""
    return buy_item(user['username'], request.item_id)

@router.post("/shop/sell")
def sell_item_endpoint(request: SellRequest, user = Depends(get_current_user)):
    """아이템 판매 요청"""
    return sell_item(user['username'], request.inventory_id)

@router.post("/shop/sell/all")
def sell_all_items_endpoint(user = Depends(get_current_user)):
    """아이템 전체 판매 요청"""
    return sell_all_items(user['username'])

@router.post("/shop/gacha/fixed")
def gacha_fixed_endpoint(user = Depends(get_current_user)):
    return play_gacha_fixed(user['username'])

@router.post("/shop/gacha/dynamic")
def gacha_dynamic_endpoint(request: GachaRequest, user = Depends(get_current_user)):
    return play_gacha_dynamic(user['username'], request.count)
