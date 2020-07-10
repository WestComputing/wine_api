from django.db.models import Model, CharField, TextField


class Wine(Model):
    wine_name = CharField(max_length=50)
    price = CharField(max_length=10)
    varietal = CharField(max_length=50)
    description = TextField()

    def __str__(self):
        return self.wine_name
