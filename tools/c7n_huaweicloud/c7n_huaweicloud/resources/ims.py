# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import logging
import json

from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkims.v2 import *

from c7n.utils import type_schema
from c7n_huaweicloud.actions.base import HuaweiCloudBaseAction
from c7n_huaweicloud.provider import resources
from c7n_huaweicloud.query import QueryResourceManager, TypeInfo
from c7n.filters import (AgeFilter,ValueFilter)

log = logging.getLogger("custodian.huaweicloud.resources.ims")


@resources.register('ims')
class Ims(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'ims'
        enum_spec = ("list_images", 'images', 'ims')
        id = 'id'
        tag_resource_type= 'private_image'



@Ims.action_registry.register("deregister")
class Deregister(HuaweiCloudBaseAction):
    """Deregister IMS Images.

    :Example:

    .. code-block:: yaml

        policies:
          - name: ims-deregister-test
            resource: huaweicloud.ims
            filters:
              - type: value
                key: name
                value: "test"
            actions:
              - delete
    """

    schema = type_schema("deregister")

    def perform_action(self, resource):
        client = self.manager.get_client()
        request = GlanceDeleteImageRequest()
        request.image_id = resource["id"]
        request.body = GlanceDeleteImageRequestBody()
        response = client.glance_delete_image(request)
        log.info(f"status_code:{response.status_code}")
        return json.dumps(response.to_dict())


@Ims.action_registry.register("set-permissions")
class SetPermissions(HuaweiCloudBaseAction):
    """Share IMS Images.

    :Example:

    .. code-block:: yaml

        policies:
          - name: ims-share-image
            resource: huaweicloud.ims
            filters:
              - type: value
                key: name
                value: "test"
            actions:
              - type: set-permissions
                remove_projects: ["imageId"]
    """
    schema = type_schema(
        'set-permissions',
        add_projects={'type': 'array'},
        remove_projects={'type': 'array'}
    )

    def perform_action(self, resource):
        client = self.manager.get_client()
        addListProjectsbody=self.data.get('add_projects',None)
        removeListProjectsbody=self.data.get('remove_projects',None)
        response={}
        if addListProjectsbody is not None and addListProjectsbody:
            request = BatchAddMembersRequest()
            request.body = BatchAddMembersRequestBody(
                projects=addListProjectsbody,
                images=[resource["id"]]
            )
            print("rrrrrrrrr")
            response = client.batch_add_members(request)
            print("wwwwwwww")
            log.info(f"add_projects response status_code:{response.status_code}")
        elif removeListProjectsbody is not None and removeListProjectsbody:
            request = BatchDeleteMembersRequest()
            request.body = BatchAddMembersRequestBody(
                projects=removeListProjectsbody,
                images=[resource["id"]]
            )
            response = client.batch_delete_members(request)
            log.info(f"remove_projects response status_code:{response.status_code}")
        else:
            raise ValueError("invalid add_projects or remove_projects")
        log.info("#######%s" % response)
        return json.dumps(response.to_dict())

@Ims.action_registry.register("cancel-launch-permission")
class CancelLaunchPermissions(HuaweiCloudBaseAction):
    """Accepted Or Rejected IMS Images.

    :Example:

    .. code-block:: yaml

        policies:
          - name: ims-cancel-launch-permission
            resource: huaweicloud.ims
            filters:
              - type: value
                key: name
                value: "test"
            actions:
              - type: cancel-launch-permission
                status: rejected
                project_id: $project_id
    """
    schema = type_schema('cancel-launch-permission', 
                         status={'type': 'string',"enum": ["accepted", "rejected"]},
                         project_id={'type': 'string'},
                         vault_id={'type': 'string'},
                         required=('status','project_id'))
    def perform_action(self, resource):
        client = self.manager.get_client()
        request = BatchUpdateMembersRequest()
        request.body = BatchUpdateMembersRequestBody(
            vault_id=self.data.get('vault_id',None),
            status=self.data.get('status',None),
            project_id=self.data.get('project_id',None),
            images=[resource["id"]]
        )
        response = client.batch_update_members(request)

        log.info(f"status_code:{response.status_code}")
        return json.dumps(response.to_dict())
    

@Ims.action_registry.register("copy")
class Copy(HuaweiCloudBaseAction):
    """Copy IMS Images.

    :Example:

    .. code-block:: yaml

        policies:
          - name: ims-copy-image
            resource: huaweicloud.ims
            filters:
              - type: value
                key: name
                value: "test"
            actions:
              - type: copy
                name: itau-copy
                description: test
    """
    schema = type_schema('copy', 
                         name={'type': 'string'},
                         enterprise_project_id={'type': 'string'},
                         description={'type': 'string'},
                         cmk_id={'type': 'string'}
                         )
    def perform_action(self, resource):
        client = self.manager.get_client()
        request = CopyImageInRegionRequest()
        request.image_id = resource["id"]
        request.body = CopyImageInRegionRequestBody(
            name=self.data.get('name',None),
            enterprise_project_id=self.data.get('enterprise_project_id',None),
            description=self.data.get('description',None),
            cmk_id=self.data.get('cmk_id',None)
        )
        response = client.copy_image_in_region(request)
        print("sssssssss")
        log.info(f"status_code:{response.status_code}")
        # TODO: need to track whether the job succeed
        return json.dumps(response.to_dict())
    

@Ims.filter_registry.register("image-age")
class ImageAge(AgeFilter):
    """Filters images based on the age (in days)

    :example:

    .. code-block:: yaml

            policies:
              - name: ims-image-age-filter
                resource: ims
                filters:
                  - type: image-age
                    days: 30
    """

    date_attribute = "created_at"
    schema = type_schema(
        'image-age',
        op={'$ref': '#/definitions/filters_common/comparison_operators'},
        days={'type': 'number', 'minimum': 0})


@Ims.filter_registry.register("image-attribute")
class ImageAttribute(ValueFilter):

    """IMS Image Value Filter on a given image attribute.

    :example:

    .. code-block:: yaml

            policies:
              - name: ims-image-windows
                resource: huaweicloud.ims
                filters:
                  - type: image-attribute
                    attribute: __os_type
                    key: "Value"
                    value: Windows
    """
    valid_attrs = (
        'virtual_env_type',
        'status',
        'disk_format',
        '__os_type'
    )

    schema = type_schema(
        'image-attribute',
        rinherit=ValueFilter.schema,
        attribute={'enum': valid_attrs},
        required=('attribute',))
    schema_alias = False

    def process(self, resources, event=None):
        attribute = self.data['attribute']
        self.get_image_attribute(resources, attribute)
        return [resource for resource in resources
                if self.match(resource['image:attribute-%s' % attribute])]

    def get_image_attribute(self, resources, attribute):
        for resource in resources:
            resource['image:attribute-%s' % attribute] = {'Value':resource[attribute]}



# 过滤所有镜像中，共享给非白名单用户的镜像
@Ims.filter_registry.register("cross-account")
class ImageAttribute(ValueFilter):

    schema = type_schema(
        'cross-account',
        list={'type': 'array', 'items': {'type': 'string'}})

    def process_resource_set(self, accounts, resource_set):
        results = []
        for r in resource_set:
            image_accounts = set(list_image_members(self, image_id=r['id']))
            if not image_accounts:
                continue
            log.info("*************image_accounts %s" % image_accounts)
            log.info("*************accounts %s" % accounts)
            delta_accounts = image_accounts.difference(accounts)
            if delta_accounts:
                results.append(r)
        return results

    def process(self, resources, event=None):
        results = []
        accounts = self.data.get("list", None)
        shared_or_private_resources = []
        if not accounts:
            return results
        for resource in resources:
            if resource['__imagetype'] in ('private', 'shared'):
                shared_or_private_resources.append(resource)

        try:
            batch_result = self.process_resource_set(accounts, shared_or_private_resources)
            results.extend(batch_result)
        except Exception as e:
            self.log.error("Exception checking cross account access \n %s" % e)
    
        return results
        
def list_image_members(self,image_id):
        client=self.manager.get_client()
        member_id_list=[]
        try:
            request = GlanceListImageMembersRequest()
            request.image_id = image_id
            response = client.glance_list_image_members(request)
            members=response.members
            if not members:
                return member_id_list
            for member in members:
                member_id_list.append(member.member_id)
        except exceptions.ClientRequestException as e:
            log.error(e.error_msg)
        return member_id_list