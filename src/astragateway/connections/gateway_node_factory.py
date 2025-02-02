from astracommon.models.blockchain_protocol import BlockchainProtocol
from astragateway.connections.btc.btc_gateway_node import BtcGatewayNode
from astragateway.connections.eth.eth_gateway_node import EthGatewayNode
from astrautils import logging

logger = logging.get_logger(__name__)


def get_gateway_node_type(blockchain_protocol):
    # TODO: This is temporary logic that will be replaced with list of valid protocols and networks from SDN
    if blockchain_protocol == BlockchainProtocol.ETHEREUM.value:
        return EthGatewayNode

    if blockchain_protocol == BlockchainProtocol.ONTOLOGY.value:
        from astragateway.connections.ont.ont_gateway_node import OntGatewayNode
        return OntGatewayNode

    return BtcGatewayNode
