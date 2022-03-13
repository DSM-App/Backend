from django.shortcuts import render
from rest_framework.views import APIView
from .models import Block, BlockChain
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import permissions, status
import hashlib
from .utils import *


User = get_user_model()


class CreateBlock(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            data = request.data
        except:
            return Response("Data not present", status=status.HTTP_400_BAD_REQUEST)

        blockchain = BlockChain.objects.get(id=1)
        new_block = Block.objects.create(
            data=data, mined_by=user, prev_block_hash=blockchain.last_block_hash
        )
        hash_string = (
            "data"
            + str(new_block.data)
            + "mined_by"
            + str(new_block.mined_by)
            + "created_at"
            + str(new_block.created_at)
        )

        mined_result = mine_block(hash_string)
        new_block.block_hash = mined_result["block_hash"]
        new_block.nonce = mined_result["nonce"]
        new_block.save()

        blockchain.last_block_hash = new_block.block_hash
        blockchain.number_of_blocks += 1
        blockchain.save()

        return Response(new_block.block_info(), status=status.HTTP_201_CREATED)


class DisplayBlockChain(APIView):
    def get(self, request):

        blocklist = []

        blockchain = BlockChain.objects.get(id=1)

        current_block_hash = blockchain.last_block_hash
        block_number = blockchain.number_of_blocks

        while current_block_hash != "" and block_number > 0:
            try:
                current_block = Block.objects.get(block_hash=current_block_hash)
            except:
                return Response(
                    "Invalid Blockchain at block " + str(current_block.id),
                    status=status.HTTP_404_NOT_FOUND,
                )

            blocklist.append(current_block.block_info())
            current_block_hash = current_block.prev_block_hash
            block_number -= 1

        blocklist.reverse()
        return Response(
            {
                "blockchain": blocklist,
            },
            status=status.HTTP_200_OK,
        )


class ValidateBlockChain(APIView):
    def get(self, request):

        blockchain = BlockChain.objects.get(id=1)

        current_block_hash = blockchain.last_block_hash

        while current_block_hash != "":
            try:
                print(f"current block hash = {current_block_hash}")
                current_block = Block.objects.get(block_hash=current_block_hash)
            except:
                return Response(
                    "Invalid Blockchain " + str(current_block.id),
                    status=status.HTTP_404_NOT_FOUND,
                )

            hash_string = (
                "data"
                + str(current_block.data)
                + "mined_by"
                + str(current_block.mined_by)
                + "created_at"
                + str(current_block.created_at)
                + str(current_block.nonce)
            )

            binary_string = hash_string.encode()
            s = hashlib.sha256()
            s.update(binary_string)
            generate_current_block_hash = s.hexdigest()

            if generate_current_block_hash != current_block_hash:
                return Response(
                    "Blockchain tampered at block number " + str(current_block.id),
                    status=status.HTTP_200_OK,
                )

            current_block_hash = current_block.prev_block_hash

        return Response("Blockchain is valid", status=status.HTTP_200_OK)
