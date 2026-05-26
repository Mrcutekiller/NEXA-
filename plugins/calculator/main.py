# Nexa Plugin: calculator
class NexaPlugin:
    def on_command(self, command: str, args: str) -> str:
        return f"[Plugin calculator] Executed command: " + command + " with args: " + args
    
    def on_trigger(self, message: str, context: dict) -> str:
        return None
