from cards.models import Cards, Categories, Mappings


def create_second_side(category: Categories, mapping_object: Mappings, side1: str, side2: str):
    """
    Creates a new card with the sides reversed (side2 becomes side1 and vice versa)
    and adds it to the same category. Updates the original mapping to indicate that
    it has a corresponding two-sided card.

    :param category: The category to which the cards belong.
    :param mapping_object: The original mapping object associated with the first card.
    :param side1: The front side of the original card.
    :param side2: The back side of the original card.
    """
    # Create a new card with sides reversed
    new_card = Cards.objects.create(side1=side2, side2=side1)

    # Create a new mapping for the reversed card, marking it as a two-sided card
    Mappings.objects.create(card=new_card, category=category, has_two_sides=True)

    # Update the original mapping to indicate it has a corresponding two-sided card
    mapping_object.has_two_sides = True
    mapping_object.save()
