# from rest_framework import serializers
# from apps.outline_vpn_admin.models import OutlineVPNKeys, TelegramUsers
#
#
# class BaseSerializer(serializers.ModelSerializer):
#     def update(self, instance, validated_data):
#         for key, value in validated_data.items():
#             setattr(instance, key, value)
#         instance.save()
#         return instance
#
#
# class OutlineVPNKeysSerializer(BaseSerializer):
#     class Meta:
#         model = OutlineVPNKeys
#         # TODO: убрать поле id
#         fields = '__all__'
#
#     # def create(self, validated_data):
#     #     return OutlineVPNKeys.objects.create(**validated_data)
#
#
# class TelegramUsersSerializer(BaseSerializer):
#     class Meta:
#         model = TelegramUsers
#         # TODO: убрать поле id
#         fields = '__all__'
#
#     # def create(self, validated_data):
#     #     return TelegramUsers.objects.create(**validated_data)
