# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import logging

from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkims.v2 import *

from c7n.utils import type_schema
from c7n_huaweicloud.actions.base import HuaweiCloudBaseAction
from c7n_huaweicloud.provider import resources
from c7n_huaweicloud.query import QueryResourceManager, TypeInfo

log = logging.getLogger("custodian.huaweicloud.resources.ims")


@resources.register('ims')
class Ims(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'ims'
        enum_spec = ("list_images", 'images', 'ListImagesRequest')
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

    
