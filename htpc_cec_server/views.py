import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from htpc_cec_client.constants import EventTypes, EventTargets, EVENT_TYPE_KEY, EVENT_TARGET_KEY, EVENT_VALUE_KEY
from htpc_cec_server.libcec import CECClient, CECCommands
from htpc_cec_server.utils import ConsoleManager


class ClientMessageCallbackAPIView(APIView):
    def post(self, request, *args, **kwargs):
        message = request.data.get("message")
        if message is None:
            return Response({"error": "No message received"}, status=status.HTTP_400_BAD_REQUEST)

        fields_dict = {
            EVENT_TYPE_KEY: EventTypes,
            EVENT_TARGET_KEY: EventTargets,
        }

        for key in fields_dict:
            try:
                message[key] = fields_dict[key](message[key])
            except KeyError:
                return Response({"error": f"Field {key} in message is required"}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                pass

        print(f"[NEW MESSAGE] {message}")
        try:
            ConsoleManager().dispatch_event(message)
        except Exception:
            print(traceback.format_exc())
            return Response(
                {"error": "Failed executing command for message"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(status=status.HTTP_201_CREATED)


class ClientLogEmitted(APIView):
    def post(self, request, *args, **kwargs):
        message = request.data.get("message")
        if message is None:
            return Response({"error": "No message received"}, status=status.HTTP_400_BAD_REQUEST)

        print(f"[CLIENT LOG] {message}")

        return Response(status=status.HTTP_201_CREATED)


class SendCECMessageAPIView(APIView):
    def post(self, request, *args, **kwargs):
        message = request.data.get("message")
        if message is None:
            return Response({"error": "No message received"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            CECClient().ProcessCommandTx(message)
        except RuntimeError as ex:
            return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print(f"[SENT MESSAGE] {message}")
        return Response(status=status.HTTP_201_CREATED)


class HomeAssistantGetStateAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"powered_on": ConsoleManager().powered_on}, status=status.HTTP_200_OK)
