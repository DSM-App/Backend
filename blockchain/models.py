from django.db import models
from django.contrib.auth import get_user_model
import hashlib


class Block(models.Model):
    block_hash = models.TextField(max_length=500)
    data = models.TextField(max_length=10000)
    nonce = models.IntegerField(default=0)
    mined_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    prev_block_hash = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Block number: " + str(self.id)

    def block_info(self):
        return {
            "block_id": self.id,
            "block_hash": self.block_hash,
            "data": self.data,
            "nonce": self.nonce,
            "mined_by": self.mined_by.username,
            "prev_block_hash": self.prev_block_hash,
            "created_at": self.created_at,
        }


class BlockChain(models.Model):
    number_of_blocks = models.IntegerField(default=0)
    last_block_hash = models.TextField(max_length=500)

    def __str__(self):
        return (
            "BlockChain Id = "
            + str(self.id)
            + " Number of blocks = "
            + str(self.number_of_blocks)
        )
