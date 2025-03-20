# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import logging

from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkims.v2 import *

from c7n.utils import type_schema
from c7n_huaweicloud.actions.base import HuaweiCloudBaseAction
from c7n_huaweicloud.provider import resources
from c7n_huaweicloud.query import QueryResourceManager, TypeInfo
from c7n.filters import (AgeFilter)

log = logging.getLogger("custodian.huaweicloud.resources.ims")


@resources.register('ims')
class Ims(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'ims'
        enum_spec = ("glance_list_images", 'images', 'marker')
        id = 'id'
        tag = True


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
        # TODO: need to track whether the job succeed
        response = None
        return response


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

        if addListProjectsbody is not None and addListProjectsbody:
            request = BatchAddMembersRequest()
            request.body = BatchAddMembersRequestBody(
                projects=addListProjectsbody,
                images=[resource["id"]]
            )
            print(request)
            response = client.batch_add_members(request)
            log.info(f"add_projects response status_code:{response.status_code}")
        if removeListProjectsbody is not None and removeListProjectsbody:
            request = BatchDeleteMembersRequest()
            request.body = BatchAddMembersRequestBody(
                projects=removeListProjectsbody,
                images=[resource["id"]]
            )
            response = client.batch_delete_members(request)
            log.info(f"remove_projects response status_code:{response.status_code}")
        response = None
        return response

@Ims.action_registry.register("cancel-launch-permission")
class CancelLaunchPermissions(HuaweiCloudBaseAction):
    
    schema = type_schema('cancel-launch-permission', 
                         status={'type': 'string',"enum": ["accepted", "rejected"]},
                         project_id={'type': 'string'},
                         vault_id={'type': 'string'})
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
        # TODO: need to track whether the job succeed
        response = None
        return response
    

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
                         cmk_id={'type': 'string'})
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
        log.info(f"status_code:{response.status_code}")
        # TODO: need to track whether the job succeed
        response = None
        return response
    

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
    
