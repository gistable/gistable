    async def cmd_ping(self):
        """
        Usage:
            {command_prefix}ping
        Ping command to test latency
        """
        return Response("Pong!")