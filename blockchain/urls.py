from django.urls import path
from .views import CreateBlock, DisplayBlockChain, ValidateBlockChain

urlpatterns = [
    path("create-block/", CreateBlock.as_view()),
    path("display-blockchain/", DisplayBlockChain.as_view()),
    path("validate-blockchain/", ValidateBlockChain.as_view()),
]
