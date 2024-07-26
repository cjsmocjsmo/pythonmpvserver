import tornado.ioloop
import tornado.web
import json
from subprocess import Popen
import sqlite3

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
        elif command == "pause":
            Popen(["mpvctl", "pause"])
        elif command == "next":
            Popen(["mpvctl", "next"])
        elif command == "prev":
            Popen(["mpvctl", "prev"])
        else:
            return "Unknown command."

def make_app():
    return tornado.web.Application([
        (r"/add/mediaid", AddHandler)
        (r"/command", CommandHandler),
    ])

if __name__ == "__main__":
    Popen(["mpv", "--input-ipc-server=/tmp/mpvsocket", "--idle", "--fs"])
    app = make_app()
    app.listen(8888)
    print("Server started at http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()