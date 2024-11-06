from domains.models.City import City

#Author is an Entity that has a City along with it's other datas
class Author:
    
    def __init__(self,first_name:str,last_name:str,city:City):
        self.first_name = first_name
        self.last_name = last_name
        self.city = city

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    @property
    def city_name(self)-> str:
        return self.city.title