from .admin_handlers.price_edit_handlers import router as price_edit_router
from .admin_handlers.statistic_handlers import router as statistic_router

from .user_handlers.start import router as start_router
from .user_handlers.registration import router as registration_router
from .user_handlers.buy import router as buy_router
from .user_handlers.notifications import router as notifications_router
from .user_handlers.profile import router as profile_router



__all__ = [
    'price_edit_router',
    'statistic_router', 
    'user_router',
    'start_router',
    'registration_router',
    'buy_router',
    'notifications_router',
    'profile_router'
    ]