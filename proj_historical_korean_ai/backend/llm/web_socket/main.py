
from web_socket.config.logging_config.logging_config_runner import LoggingConfigRunner
from web_socket.handlers.socket_server import SocketServer

class SocketRunner():

    def __init__(self):
        self.config_logger()
        self.socket_server = SocketServer()
            
    def config_logger(self):
        logging_config_runner = LoggingConfigRunner(_is_singleton=False)
        logging_config_runner.run()
        
    def run(self):
        self.socket_server.run()
    
if __name__ == "__main__":

    socket_runner = SocketRunner()
    socket_runner.run()