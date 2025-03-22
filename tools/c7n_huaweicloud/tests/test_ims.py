# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
from huaweicloud_common import *


class ImsTest(BaseTest):

    def test_ims_query(self):
        factory = self.replay_flight_data('ims_image_query')
        p = self.load_policy({
            'name': 'ims_query',
            'resource': 'huaweicloud.ims'
        }, session_factory=factory)
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_ims_deregister(self):
        factory = self.replay_flight_data('ims_image_query')
        p = self.load_policy({
            'name': 'deregister',
            'resource': 'huaweicloud.ims',
            'filters': [{"type": "value","key":"id","value":"2d25ed0b-0392-4921-b457-d1451809a07c"}],
            'actions': ["deregister"]
        }, session_factory=factory)
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_ims_image_age_success(self):
        factory = self.replay_flight_data('ims_image_query')
        p = self.load_policy({
            'name': 'image-age',
            'resource': 'huaweicloud.ims',
            'filters': [{"type": "image-age","days":1}],
            'actions': ["deregister"]
        }, session_factory=factory)
        resources = p.run()
        self.assertEqual(len(resources), 1)

    def test_ims_image_age_fail(self):
        factory = self.replay_flight_data('ims_image_query')
        p = self.load_policy({
            'name': 'image-age',
            'resource': 'huaweicloud.ims',
            'filters': [{"type": "image-age","days":100000}],
        }, session_factory=factory)
        resources = p.run()
        self.assertEqual(len(resources), 0)

    def test_ims_image_attribute(self):
        factory = self.replay_flight_data('ims_image_query')
        p = self.load_policy({
            'name': 'image-attribute',
            'resource': 'huaweicloud.ims',
            'filters': [{"type": "image-attribute","attribute":"__os_type","key":"Value","value":"Windows"}],
        }, session_factory=factory)
        resources = p.run()
        self.assertEqual(len(resources), 1)

    # def test_ims_set_permissions(self):
    #     factory = self.replay_flight_data('ims_image_query')
    #     p = self.load_policy({
    #         'name': 'set-permissions',
    #         'resource': 'huaweicloud.ims',
    #         'filters': [{"type": "value","key":"id","value":"2d25ed0b-0392-4921-b457-d1451809a07c"}],
    #         'actions': [{"type":"set-permissions","add_projects":["05e35909a28026fc2fd0c00c65df4426"]}]
    #     }, session_factory=factory)
    #     resources = p.run()
    #     self.assertEqual(len(resources), 1)

    # def test_ims_copy(self):
    #     factory = self.replay_flight_data('ims_image_query')
    #     p = self.load_policy({
    #         'name': 'copy',
    #         'resource': 'huaweicloud.ims',
    #         'filters': [{"type": "value","key":"id","value":"2d25ed0b-0392-4921-b457-d1451809a07c"}],
    #         'actions': [{"type": "copy","name":"test","description":"123"}]
    #     }, session_factory=factory)
    #     resources = p.run()
    #     self.assertEqual(len(resources), 1)