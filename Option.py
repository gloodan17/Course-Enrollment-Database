class Option:
    def __init__(self, prompt: str, action: str):
        self.prompt = prompt
        self.action = action

    def get_prompt(self):
        return self.prompt

    def get_action(self):
        return self.action

    def __str__(self):
        return "prompt {prompt} calls for {action}".format(prompt=self.prompt,
                                                           action=self.action)
