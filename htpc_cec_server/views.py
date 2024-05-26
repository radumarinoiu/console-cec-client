from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from htpc
from htpc_cec_server.libcec import CECClient


class ClientMessageCallbackAPIView(APIView):
    def post(self, request, *args, **kwargs):
        message = request.data.get("message")
        if message is None:
            return Response({"error": "No message received"}, status=status.HTTP_400_BAD_REQUEST)

        fields_dict = {
            "event_type": EventTypes
        }

        message["event_type"]
        print(f"[NEW MESSAGE] {message}")
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
