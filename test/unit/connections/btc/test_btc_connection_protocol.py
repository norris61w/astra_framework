import time

from mock import MagicMock

from astracommon.models.blockchain_peer_info import BlockchainPeerInfo
from astracommon.network.ip_endpoint import IpEndpoint
from astragateway.testing import gateway_helpers
from astracommon.test_utils.abstract_test_case import AbstractTestCase
from astracommon.constants import LOCALHOST
from astracommon.test_utils import helpers
from astracommon.utils import crypto
from astracommon.utils.blockchain_utils.btc.btc_object_hash import BtcObjectHash

from astragateway.btc_constants import BTC_HDR_COMMON_OFF
from astragateway.connections.btc.btc_base_connection_protocol import BtcBaseConnectionProtocol
from astragateway.messages.btc.block_btc_message import BlockBtcMessage
from astragateway.messages.btc.tx_btc_message import TxBtcMessage
from astragateway.testing.mocks.mock_gateway_node import MockGatewayNode
from astragateway.utils.stats.gateway_bdn_performance_stats_service import gateway_bdn_performance_stats_service


class BtcConnectionProtocolTest(AbstractTestCase):
    HASH = BtcObjectHash(binary=crypto.double_sha256(b"123"))

    def setUp(self):
        opts = gateway_helpers.get_gateway_opts(8000, include_default_btc_args=True)
        if opts.use_extensions:
            helpers.set_extensions_parallelism()
        self.node = MockGatewayNode(opts)
        self.node.block_processing_service = MagicMock()

        self.connection = MagicMock()
        gateway_helpers.add_blockchain_peer(self.node, self.connection)
        self.connection.node = self.node
        self.connection.peer_ip = LOCALHOST
        self.connection.peer_port = 8001
        self.connection.network_num = 2
        self.connection.endpoint = IpEndpoint(self.connection.peer_ip, self.connection.peer_port)
        self.node.blockchain_peers.add(BlockchainPeerInfo(self.connection.peer_ip, self.connection.peer_port))
        gateway_bdn_performance_stats_service.set_node(self.node)

        self.sut = BtcBaseConnectionProtocol(self.connection)

    def test_msg_block_success(self):
        block_timestamp = int(
            time.time()) + 1 - self.node.opts.blockchain_ignore_block_interval_count * self.node.opts.blockchain_block_interval
        txns = [TxBtcMessage(0, 0, [], [], i).rawbytes()[BTC_HDR_COMMON_OFF:] for i in range(10)]
        message = BlockBtcMessage(0, 0, self.HASH, self.HASH, block_timestamp, 0, 0, txns)

        self.sut.msg_block(message)
        self.node.block_processing_service.queue_block_for_processing.assert_called_once()

    def test_msg_block_too_old(self):
        block_timestamp = int(
            time.time()) - 1 - self.node.opts.blockchain_ignore_block_interval_count * self.node.opts.blockchain_block_interval
        txns = [TxBtcMessage(0, 0, [], [], i).rawbytes()[BTC_HDR_COMMON_OFF:] for i in range(10)]
        message = BlockBtcMessage(0, 0, self.HASH, self.HASH, 0, block_timestamp, 0, txns)

        self.sut.msg_block(message)
        self.node.block_processing_service.queue_block_for_processing.assert_not_called()
