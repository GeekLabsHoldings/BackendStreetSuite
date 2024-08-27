import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Alert
from channels.layers import get_channel_layer

class WebSocketConsumer(AsyncWebsocketConsumer):
    channel_layer = get_channel_layer()
    async def connect(self):
        # if self.scope["user"].is_authenticated:
        await self.channel_layer.group_add(
            "alerts",
            self.channel_name
        )
        #     print(f'User {self.scope["user"].username} connected to WebSocket')
        await self.accept()
        

    async def disconnect(self, close_code):
        # if self.scope["user"].is_authenticated:
        await self.channel_layer.group_discard(
            "alerts",
            self.channel_name
        )
            # print(f'User {self.scope["user"].username} disconnected from WebSocket')

    async def send_alert(self, event):
        alert = event['alert']
        await self.send(text_data=json.dumps(alert))
    async def send_alert(self, event):
        # Send the alert to the WebSocket
        alert = event['alert']
        await self.send(text_data=json.dumps(alert))

    @staticmethod
    def send_new_alert(alert):
        # Send a new alert to the group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "alerts",
            {
                "type":"send_alert",
                "alert" :{
                    "id": alert.id,
                    "ticker": {
                        "id": alert.ticker.id,
                        "industry": {
                            "type": alert.ticker.industry.type,
                        },
                        "symbol": alert.ticker.symbol,
                        "name": alert.ticker.name,
                        "market_cap": alert.ticker.market_cap,
                        "market_capital": alert.ticker.market_capital,
                    },
                    "strategy": alert.strategy,
                    "time_frame": alert.time_frame,
                    "result_value": alert.result_value,
                    "risk_level": alert.risk_level,
                    "Estimated_Revenue": alert.Estimated_Revenue,
                    "Estimated_EPS": alert.Estimated_EPS,
                    "current_IV": alert.current_IV,
                    "Expected_Moves": alert.Expected_Moves,
                    "earning_time": alert.earning_time,
                    "investor_name": alert.investor_name,
                    "transaction_type": alert.transaction_type,
                    "shares_quantity": alert.shares_quantity,
                    "ticker_price": alert.ticker_price,
                    "amount_of_investment": alert.amount_of_investment,
                    "transaction_date": alert.transaction_date,
                    "job_title": alert.job_title,
                    "filling_date": alert.filling_date,
                    "current_price": alert.current_price
                }
        },
        )
# class WebSocketConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         self.send(text_data=json.dumps({"message": message}))
    # async def send_alert(self, event):
    #     # Send the alert to the WebSocket
    #     alert = event['alert']
    #     await self.send(text_data=json.dumps(alert))



    # @staticmethod
    # def send_new_alert(alert):
    #     channel_layer = get_channel_layer()
    #     async_to_sync(channel_layer.group_send)(
    #         "alerts",
    #         {
    #             "type": "send_alert",
    #             "alert": alert
    #         }
    #     )