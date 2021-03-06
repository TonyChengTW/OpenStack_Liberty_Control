#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from oslo_messaging._drivers.zmq_driver.broker import zmq_base_proxy
from oslo_messaging._drivers.zmq_driver.client.publishers.dealer \
    import zmq_dealer_publisher_proxy
from oslo_messaging._drivers.zmq_driver.client.publishers \
    import zmq_pub_publisher
from oslo_messaging._drivers.zmq_driver import zmq_address
from oslo_messaging._drivers.zmq_driver import zmq_async
from oslo_messaging._drivers.zmq_driver import zmq_names
from oslo_messaging._i18n import _LI

zmq = zmq_async.import_zmq(zmq_concurrency='native')
LOG = logging.getLogger(__name__)


class UniversalQueueProxy(zmq_base_proxy.BaseProxy):

    def __init__(self, conf, context, matchmaker):
        super(UniversalQueueProxy, self).__init__(conf, context)
        self.poller = zmq_async.get_poller(zmq_concurrency='native')

        self.router_socket = context.socket(zmq.ROUTER)
        self.router_socket.bind(zmq_address.get_broker_address(conf))

        self.poller.register(self.router_socket, self._receive_in_request)
        LOG.info(_LI("Polling at universal proxy"))

        self.matchmaker = matchmaker
        reply_receiver = zmq_dealer_publisher_proxy.ReplyReceiver(self.poller)
        self.publisher = zmq_dealer_publisher_proxy.DealerPublisherProxy(
            conf, matchmaker, reply_receiver)
        self.pub_publisher = zmq_pub_publisher.PubPublisherProxy(
            conf, matchmaker)

    def run(self):
        message, socket = self.poller.poll(self.conf.rpc_poll_timeout)
        if message is None:
            return

        if socket == self.router_socket:
            self._redirect_in_request(message)
        else:
            self._redirect_reply(message)

    def _redirect_in_request(self, multipart_message):
        LOG.debug("-> Redirecting request %s to TCP publisher"
                  % multipart_message)
        envelope = multipart_message[zmq_names.MULTIPART_IDX_ENVELOPE]
        if self.conf.use_pub_sub and \
            envelope[zmq_names.FIELD_MSG_TYPE] \
                == zmq_names.CAST_FANOUT_TYPE:
            self.pub_publisher.send_request(multipart_message)
        else:
            self.publisher.send_request(multipart_message)

    def _redirect_reply(self, reply):
        LOG.debug("Reply proxy %s" % reply)
        if reply[zmq_names.IDX_REPLY_TYPE] == zmq_names.ACK_TYPE:
            LOG.debug("Acknowledge dropped %s" % reply)
            return

        LOG.debug("<- Redirecting reply to ROUTER: reply: %s"
                  % reply[zmq_names.IDX_REPLY_BODY:])

        self.router_socket.send_multipart(reply[zmq_names.IDX_REPLY_BODY:])

    def _receive_in_request(self, socket):
        reply_id = socket.recv()
        assert reply_id is not None, "Valid id expected"
        empty = socket.recv()
        assert empty == b'', "Empty delimiter expected"
        envelope = socket.recv_pyobj()
        if envelope[zmq_names.FIELD_MSG_TYPE] == zmq_names.CALL_TYPE:
            envelope[zmq_names.FIELD_REPLY_ID] = reply_id
        payload = socket.recv_multipart()
        payload.insert(0, envelope)
        return payload
