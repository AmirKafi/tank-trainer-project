import uuid

# For easier searching City must be an Entity
class City:
    def __repr__(self):
        return f"{self.title}"

    def __init__(self,title:str):
        self.title = title

    def __str__(self):
        return self.title