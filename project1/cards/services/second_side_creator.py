from cards.models import Cards, Categories, Mappings

def create_second_side(category: Categories, mapping_object: Mappings, side1: str, side2: str):
    new_object = Cards.objects.create(side1=side2, side2=side1)
    Mappings.objects.create(card=new_object, category=category, has_two_sides=True)
    mapping_object.has_two_sides = True
    mapping_object.save()
