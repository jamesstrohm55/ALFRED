import tkinter as tk
from threading import Thread
from core.voice import speak
from core.listener import listen
from core.brain import get_response
from services.automation import run_command
from ui.system_overlay import launch_system_overlay

launch_system_overlay()  # Start the system overlay in a separate thread

class ALFREDGUI:
    def __init__(self, root):
        self.root = root
        root.title("A.L.F.R.E.D")
        root.geometry("500x500")

        # Conversation log
        self.log = tk.Text(root, height=20, bg="black", fg="lime", font=("Consolas", 10))
        self.log.pack(pady=10, padx=10)

        # Speak button
        self.listen_button = tk.Button(root, text="🎤 Speak", command=self.handle_speak, font=("Arial", 12))
        self.listen_button.pack(pady=5)

        # Text input field
        self.entry = tk.Entry(root, font=("Arial", 12))
        self.entry.pack(fill=tk.X, padx=10, pady=5)
        self.entry.bind("<Return>", self.handle_text_input)

        # Send button
        self.send_button = tk.Button(root, text="📤 Send", command=self.handle_send, font=("Arial", 12))
        self.send_button.pack(pady=5)

    def handle_speak(self):
        Thread(target=self.process_command_from_voice).start()

    def handle_send(self):
        command = self.entry.get()
        self.entry.delete(0, tk.END)
        Thread(target=self.process_command, args=(command,)).start()

    def handle_text_input(self, event):
        self.handle_send()

    def process_command_from_voice(self):
        command = listen()
        if command:
            self.process_command(command)

    def process_command(self, command):
        self.log.insert(tk.END, f"You: {command}\n")

        if "shutdown" in command.lower():
            speak("Powering down.")
            self.root.quit()
            return

        system_response = run_command(command)
        if system_response:
            speak(system_response)
            self.log.insert(tk.END, f"A.L.F.R.E.D: {system_response}\n")
            return

        response = get_response(command)
        speak(response)
        self.log.insert(tk.END, f"A.L.F.R.E.D: {response}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ALFREDGUI(root)
    speak("Graphic User Interface loaded, sir.")
    root.mainloop()
