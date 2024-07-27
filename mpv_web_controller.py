import tornado.ioloop
import tornado.web
import json
from subprocess import Popen
import sqlite3

class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class AddHandler(tornado.web.RequestHandler):
    def get(self):
        mediaid = self.get_argument("mediaid", None)
        if mediaid:
            dbpath = "/usr/share/mtvdb/mtv.db"
            conn = sqlite3.connect(dbpath)
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM movies WHERE movid = ?", (mediaid,))
            path = cursor.fetchone()
            conn.close()
            if path:
                Popen(["mpvctl", "add", path[0]])
                response = "Playing media..."
                self.write(json.dumps({"response": response}))
            else:
                response = "Media not found."
                self.write(json.dumps({"response": "No mediaid provided."}))

class CommandHandler(tornado.web.RequestHandler):
    def get(self):
        command = self.get_argument("command", None)
        if command:
            response = self.handle_command(command)
            self.write(json.dumps({"response": response}))
        else:
            self.write(json.dumps({"response": "No command provided."}))

    def handle_command(self, command, mediaid):
        if command == "play":
            Popen(["mpvctl", "play"])
            return "Playing media..."
        elif command == "pause":
            Popen(["mpvctl", "pause"])
            return "Media paused."
        elif command == "next":
            Popen(["mpvctl", "next"])
            return "Playing next media..."
        elif command == "prev":
            Popen(["mpvctl", "prev"])
            return "Playing previous media..."
        else:
            return "Unknown command."

def make_app():
    return tornado.web.Application([
        (r"/test", TestHandler),
        (r"/add/mediaid", AddHandler)
        (r"/command", CommandHandler),
    ])

if __name__ == "__main__":
    Popen(["mpv", "--input-ipc-server=/tmp/mpvsocket", "--fs", "--idle"])
    app = make_app()
    app.listen(9999)
    print("Server started at http://localhost:9999")
    tornado.ioloop.IOLoop.current().start()