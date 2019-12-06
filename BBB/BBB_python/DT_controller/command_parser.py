import json

class Command_parser:

    def mode(self,data):
        try:
            data = json.loads(data)
            if data[0]["mode"] == "HOME":
                return ["HOME"]
            elif data[0]["mode"] == "ESTOP":
                return ["ESTOP"]
            elif data[0]["mode"] == "cycStart":
                return
            elif data[0]["mode"] == "program":
                return
            elif data[0]["mode"] == "jog":
                return
            elif data[0]["mode"] == "inspection":
                return
            else:
                return None

        except Exception as e:
            return "Erro: {}".format(str(e))
 #   def program(self):
