from . import item_router, merchant_router, wallet_router, transaction_router

def init_routers(app):
    app.include_router(item_router.router)
    app.include_router(merchant_router.router)
    app.include_router(wallet_router.router)
    app.include_router(transaction_router.router)