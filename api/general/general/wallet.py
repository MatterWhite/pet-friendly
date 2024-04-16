from auth import AuthorizedUser
from models.wallet import Wallet
from router import routes
import aiohttp.web_request


@routes.get('/wallet/real_balance')
async def get_wallet_real_balance(request: aiohttp.web_request.Request, user: AuthorizedUser) -> int:
    return Wallet.fetch(owner_id=user._id).balance_real


@routes.get('/wallet/freezed_balance')
async def get_wallet_freezed_balance(request: aiohttp.web_request.Request, user: AuthorizedUser) -> int:
    return Wallet.fetch(owner_id=user._id).balance_freezed


@routes.get('/wallet')
async def get_wallet(request: aiohttp.web_request.Request, user: AuthorizedUser) -> Wallet:
    return Wallet.fetch(owner_id=user._id)


@routes.put('/wallet/deposit')
async def put_deposit(request: aiohttp.web_request.Request, user: AuthorizedUser, amount: int) -> None:
    wallet = Wallet.fetch(owner_id=user._id)
    wallet.deposit(amount)


@routes.put('/wallet/withdraw')
async def put_withdraw(request: aiohttp.web_request.Request, user: AuthorizedUser, amount: int) -> None:
    wallet = Wallet.fetch(owner_id=user._id)
    wallet.withdraw(amount)
