def handle_main_location(location, Model):
    """Handle main location based on this and other locations."""
    if location.main:
        # If this one is main, it must be the only one
        qs = Model.objects.filter(main=True)

        if location.pk:
            qs = qs.exclude(pk=location.pk)

        qs.update(main=False)
    elif Model.objects.filter(main=True).count() == 0:
        # At least one location has to be main
        location.main = True

    return location
