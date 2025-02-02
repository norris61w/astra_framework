from astracommon.connections.abstract_connection import AbstractConnection
from astracommon.messages.abstract_message import AbstractMessage
from astracommon.services.broadcast_service import BroadcastService, BroadcastOptions


class GatewayBroadcastService(
    BroadcastService[AbstractMessage, AbstractConnection, BroadcastOptions]
):
    def should_broadcast_to_connection(
        self,
        message: AbstractMessage,
        connection: AbstractConnection,
        options: BroadcastOptions
    ) -> bool:
        # gateway does not really care about network numbers
        return True
