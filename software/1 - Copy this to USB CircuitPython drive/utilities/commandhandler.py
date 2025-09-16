# This file is part of BrickVS by Adam McCaughan.
#
# BrickVS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BrickVS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BrickVS.  If not, see <https://www.gnu.org/licenses/>.

class CommandHandler:
    def __init__(self):
        self.command_map = {
            'HELP': self.help
        }
        self.command_descriptions = {
            'HELP': 'Display this help message'
        }

    def register_command(self, command_name, description=""):
        """Decorator to register a function as a command with a description."""
        command_name = command_name.upper()
        def decorator(func):
            self.command_map[command_name] = func
            self.command_descriptions[command_name] = description
            return func
        return decorator

    def handle_command(self, command_string):
        """Parse and execute a command string."""
        parts = command_string.split()
        if not parts:
            raise ValueError("Empty command string")
        
        command_name = parts[0].upper()
        args = parts[1:]
        
        if command_name not in self.command_map:
            raise ValueError(f'Unknown command "{command_name}"')
        
        func = self.command_map[command_name]
        return func(*args)

    def help(self):
        """Return information about each registered command."""
        help_info = "Available commands:\n-------------------\n"
        for command, description in self.command_descriptions.items():
            help_info += f'"{command}"  {description.strip()}\n'
        return help_info

if __name__ == "__main__":
    # Example usage
    handler = CommandHandler()

    @handler.register_command('greet', "Greets a person. Usage: greet <name>")
    def greet(name):
        return f"Hello, {name}!"

    @handler.register_command('add', "Adds two numbers. Usage: add <x> <y>")
    def add(x, y):
        return int(x) + int(y)
    
    # Test the command handler and help function
    print(handler.handle_command("greet Alice"))  # Output: Hello, Alice!
    print(handler.handle_command("add 3 4"))      # Output: 7
    print(handler.help())                         