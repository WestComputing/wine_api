from builtins import object


class WineSerializer(object):
    def __init__(self, body):
        self.body = body

    @property
    def all_wines(self):
        output = {'wines': []}

        for wine in self.body:
            wine_details = {
                'wine_name': wine.wine_name,
                'price': wine.price,
                'varietal': wine.varietal,
                'description': wine.description
            }
            output['wines'].append(wine_details)

        return output

    @property
    def wine_detail(self):
        return {
            'wine_name': self.body.wine_name,
            'price': self.body.price,
            'varietal': self.body.varietal,
            'description': self.body.description
        }
