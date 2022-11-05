import string


class Recommendation:
    def __init__(self, title: string, description: string, fix: string):
        self.title = title
        self.description = description
        self.fix = fix

    def repr_json(self):
        return dict(title=self.title, description=self.description, fix=self.fix)
