from groups.models import Group
from django.contrib.auth import get_user_model


User = get_user_model()

g1 = Group.objects.get(id=1)
s = User.objects.get(username="san")

# add member
g1.add_member(s)

# check number of people
g1.number_of_people

# remove member
g1.remove_member(s)

# group members serialization
from groups.serializers import GroupMembersSerializer

g1 = Group.objects.get(id=1)
g2 = Group.objects.get(id=2)
s1 = User.objects.get(username="san")
s2 = User.objects.get(username="san2san2")

gm1 = GroupMembersSerializer(g1.members.all(), many=True)
print(gm1.data)

# user groups serialization
from groups.serializers import GroupSerializer

ug1 = GroupSerializer(s2.user_groups.all(), many=True)
print(ug1.data)
