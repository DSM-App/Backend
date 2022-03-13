from posts.models import *
from groups.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

b = BlogPost.objects.get(id=33)

from copyrights.models import *

s = User.objects.get(username="san")
g = Group.objects.get(id=1)
blogpost = BlogPost.objects.get(id=33)

# o1 = OwnershipCopyRights.objects.create(copyrighted_by=s, group=g, blogpost=blogpost)

from copyrights.serializers import OwnershipCopyRightsSerializer

os1 = OwnershipCopyRightsSerializer(
    data={"copyrighted_by": s, "group": g, "blogpost": blogpost}
)

c7 = OwnershipCopyRights.objects.get(id=7)
print(c7.copyrighted_votes.all())
print(c7.not_copyrighted_votes.all())
