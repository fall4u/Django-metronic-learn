# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Address, Profile, Province, City, Distinct, SearchInfo, RequestBookInfo


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)



class AddressSerializer(DynamicFieldsModelSerializer):
    provinceStr = serializers.SerializerMethodField()
    cityStr = serializers.SerializerMethodField()
    areaStr = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = (
        'provinceStr', 'cityStr', 'areaStr', 'provinceId', 'cityId', 'districtId', 'contact', 'address', 'mobile',
        'zipcode', 'isDefault', 'pk')

    def get_provinceStr(self, obj):
        ret = ''
        if obj.provinceId:
            o = Province.objects.get(idx=obj.provinceId)
            ret = o.name
        return ret

    def get_cityStr(self, obj):
        ret = ''
        if obj.cityId:
            o = City.objects.get(idx=obj.cityId)
            ret = o.name 
        return ret

    def get_areaStr(self, obj):
        ret = ''
        if obj.districtId:
            o = Distinct.objects.get(idx=obj.districtId)
            ret = o.name 
        return ret


class UserProfileSerializer(serializers.ModelSerializer):
    registerTime = serializers.DateTimeField(required=False, format= "%Y-%m-%d")
    class Meta:
        model = Profile
        fields = ('nickName', 'avatarUrl', 'gender', 'city', 'province', 'country', 'language', 'pk', 'registerTime')

class SearchInfoSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = SearchInfo
        fields = ('user', 'info','time')

class RequestBookInfoSerializer(serializers.ModelSerializer):
    createTime = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    user = UserProfileSerializer()

    class Meta: 
        model = RequestBookInfo
        fields = ('name','author','createTime','status', 'formId','user')